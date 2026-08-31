"""
gemini_reasoning.py — Real Gemini AI Integration for SENTINEL-AI.

Uses the official Google GenAI Python SDK (google-genai) to perform
context-aware root-cause reasoning, attack surface analysis, and secure code
remediation for AST-detected findings.

Enforces security boundaries:
  - API Key loaded ONLY from GEMINI_API_KEY environment variable.
  - Never exposes API Key to frontend.
  - Sends ONLY minimal finding context (no full repo uploads).
  - Uses Structured JSON Outputs with Pydantic schema validation.
  - Graceful fallback: Returns None if API key is missing or call fails.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Optional

from models.schemas import Finding, Evidence, AIReasoningResult

logger = logging.getLogger("sentinel.gemini")

# Ordered candidate model list for automatic fallback if a specific model encounters high demand / rate limits
CANDIDATE_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]


def analyze_finding_with_gemini(
    finding: Finding,
    evidence: Evidence,
) -> Optional[AIReasoningResult]:
    """
    Calls Google Gemini AI to analyze a specific AST-detected finding.
    Returns AIReasoningResult on success, or None on failure/missing key.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not api_key or api_key == "your_gemini_api_key_here":
        logger.warning(
            f"[GEMINI FALLBACK] GEMINI_API_KEY is missing or unconfigured for finding {finding.finding_id}. "
            "Falling back to static reasoning."
        )
        return None

    masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "***"
    logger.info(f"[GEMINI CONFIG] GEMINI_API_KEY detected (Active Key: {masked_key})")

    try:
        # pyrefly: ignore [missing-import]
        from google import genai
        # pyrefly: ignore [missing-import]
        from google.genai import types

        client = genai.Client(api_key=api_key)

        context_before_str = "\n".join(evidence.context_before)
        context_after_str = "\n".join(evidence.context_after)

        prompt = f"""
You are an expert Application Security Engineer analyzing a real security finding flagged by a static AST analysis scanner.

Target Finding Details:
- Finding ID: {finding.finding_id}
- Rule ID: {finding.rule_id} ({finding.title})
- Category: {finding.category.value}
- Severity: {finding.severity.value}
- File Path: {finding.file_path} (Line {finding.line_number})
- Code Snippet:
```python
{finding.code_snippet}
```

Surrounding Context (Before):
```python
{context_before_str}
```

Surrounding Context (After):
```python
{context_after_str}
```

Scanner Description: {finding.description}
Deterministic Confidence Rationale: {finding.confidence_rationale}

YOUR TASK:
Analyze this specific finding and generate a structured, context-aware security analysis and minimal proposed code fix.

INSTRUCTIONS:
1. Ground your analysis strictly in the provided code snippet and context.
2. Root Cause: Explain why this specific line of code is dangerous.
3. Security Impact: Describe realistic consequences (do not exaggerate).
4. Attack Surface: High-level risk scenario and exposure.
5. Reasoning Summary: Concise 2-sentence summary for developers.
6. Remediation Strategy: Explain how the code should be fixed (e.g. use parameterized query, subprocess without shell, safe yaml load, env vars, SHA-256).
CRITICAL REMEDIATION INSTRUCTIONS FOR PROPOSED CODE:
- Provide ONLY the minimal, exact Python replacement code for the vulnerable line.
- For hardcoded secret fixes, load from environment variables e.g. `os.getenv("VAR_NAME")`. NEVER insert fake or example secret literal strings (such as "sk_live_...", "my_secret_key", "password123") in proposed_code, as they will fail static verification.
- Keep the proposed code snippet minimal, syntactically correct, and free of extraneous variable definitions.

IMPORTANT: Provide output matching the requested JSON schema.
"""

        logger.info(
            f"[GEMINI REQUEST] Gemini reasoning request started for finding {finding.finding_id} ({finding.rule_id})."
        )

        last_error_reason = ""

        for model_name in CANDIDATE_MODELS:
            try:
                logger.info(
                    f"[GEMINI REQUEST] Sending generate_content request for finding {finding.finding_id} using model '{model_name}'..."
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AIReasoningResult,
                        temperature=0.2,
                    ),
                )

                if not response.text:
                    logger.warning(
                        f"[GEMINI WARNING] Model '{model_name}' returned empty response text for finding {finding.finding_id}. Trying next candidate model..."
                    )
                    last_error_reason = f"Model {model_name} returned empty text"
                    continue

                # Parse and validate structured output
                result = AIReasoningResult.model_validate_json(response.text)

                # Clean up any potential markdown code fences in proposed_code
                if result.proposed_code:
                    code = result.proposed_code.strip()
                    if code.startswith("```"):
                        lines = code.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].strip() == "```":
                            lines = lines[:-1]
                        code = "\n".join(lines).strip()
                    result.proposed_code = code

                logger.info(
                    f"[GEMINI SUCCESS] Gemini response successfully received & validated for finding {finding.finding_id} using model '{model_name}'."
                )
                return result

            except Exception as exc:
                last_error_reason = f"Model '{model_name}' error: {exc}"
                logger.warning(
                    f"[GEMINI RETRY] Candidate model '{model_name}' failed for finding {finding.finding_id}: {exc}. Trying next candidate model..."
                )
                time.sleep(1)

        logger.warning(
            f"[GEMINI FALLBACK] All candidate models failed for finding {finding.finding_id}. "
            f"Falling back to static reasoning. Reason: {last_error_reason}"
        )
        return None

    except Exception as exc:
        logger.error(
            f"[GEMINI FALLBACK] Gemini AI initialization/request failed for finding {finding.finding_id}: {exc}. "
            "Operating in static fallback mode."
        )
        return None

