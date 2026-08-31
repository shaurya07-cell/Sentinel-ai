"""
remediation.py — Stage 4: REMEDIATE

Generates a minimal, category-specific proposed remediation for each
finding. The proposed code is an in-memory patch only — the uploaded
project's files on disk are never modified. Where a category cannot be
safely auto-remediated with confidence, `supported=False` is returned
and the UI must present it as unsupported rather than fabricating a fix.
"""

from __future__ import annotations

import re

from typing import Optional
from models.schemas import Finding, Remediation, Category, AIReasoningResult


def _remediate_command_injection(finding: Finding) -> Remediation:
    original = finding.code_snippet
    proposed = (
        "# Avoid shell interpretation entirely — pass arguments as a list:\n"
        "subprocess.run([\"<program>\", \"<arg1>\", \"<arg2>\"], shell=False, check=True)"
    )
    return Remediation(
        finding_id=finding.finding_id,
        supported=True,
        original_code=original,
        proposed_code=proposed,
        explanation=(
            "Replace shell-based execution (os.system/os.popen, or subprocess "
            "with shell=True) with subprocess.run() using an explicit argument "
            "list and shell=False. This removes shell metacharacter "
            "interpretation entirely."
        ),
        security_benefit=(
            "Eliminates the shell as an interpretation layer, closing the "
            "primary command-injection vector regardless of argument content."
        ),
        ai_powered=False,
    )


def _remediate_deserialization(finding: Finding) -> Remediation:
    original = finding.code_snippet
    if "yaml" in original:
        proposed = "yaml.safe_load(data)  # restricts construction to basic Python types"
        explanation = (
            "Use yaml.safe_load() instead of yaml.load() so the parser can only "
            "construct basic Python types (str, int, list, dict, etc.), not "
            "arbitrary objects."
        )
    else:
        proposed = (
            "# Prefer a schema-validated, non-executable format:\n"
            "import json\n"
            "data = json.loads(payload)  # validate against an expected schema"
        )
        explanation = (
            "Replace pickle with a data-only format such as JSON plus explicit "
            "schema validation, since pickle can execute arbitrary code during "
            "deserialization of untrusted input."
        )
    return Remediation(
        finding_id=finding.finding_id,
        supported=True,
        original_code=original,
        proposed_code=proposed,
        explanation=explanation,
        security_benefit=(
            "Removes the ability for deserialized input to trigger arbitrary "
            "code execution."
        ),
        ai_powered=False,
    )


def _remediate_hardcoded_secret(finding: Finding) -> Remediation:
    original = finding.code_snippet
    var_match = re.search(r"(\w+)\s*=", original)
    var_name = var_match.group(1) if var_match else "SECRET"
    env_name = var_name.upper()
    proposed = (
        f"import os\n"
        f"{var_name} = os.environ[\"{env_name}\"]  # loaded from environment, never committed"
    )
    return Remediation(
        finding_id=finding.finding_id,
        supported=True,
        original_code=original,
        proposed_code=proposed,
        explanation=(
            f"Load '{var_name}' from an environment variable (or a secret "
            "manager) instead of hardcoding it, and rotate the original "
            "exposed value."
        ),
        security_benefit=(
            "Removes the secret from source control and enables rotation "
            "without a code change."
        ),
        ai_powered=False,
    )


def _remediate_sql_injection(finding: Finding) -> Remediation:
    original = finding.code_snippet
    proposed = (
        "cursor.execute(\"SELECT * FROM table WHERE column = %s\", (value,))\n"
        "# or with sqlite3-style placeholders:\n"
        "cursor.execute(\"SELECT * FROM table WHERE column = ?\", (value,))"
    )
    return Remediation(
        finding_id=finding.finding_id,
        supported=True,
        original_code=original,
        proposed_code=proposed,
        explanation=(
            "Replace string interpolation/concatenation in the query with "
            "parameter placeholders and pass values separately, letting the "
            "database driver perform safe binding."
        ),
        security_benefit=(
            "Query structure and data are kept separate, preventing attacker-"
            "supplied values from altering the query's semantics."
        ),
        ai_powered=False,
    )


def _remediate_weak_crypto(finding: Finding) -> Remediation:
    original = finding.code_snippet
    algo = "md5" if "md5" in original.lower() else "sha1"
    proposed = original.replace(algo, "sha256")
    if proposed == original:
        proposed = "hashlib.sha256(data)  # or a dedicated password hasher for credentials"
    return Remediation(
        finding_id=finding.finding_id,
        supported=True,
        original_code=original,
        proposed_code=proposed,
        explanation=(
            f"Replace {algo.upper()} with SHA-256 (or SHA-3) for general "
            "integrity checks, or with bcrypt/scrypt/Argon2 specifically if "
            "this hash is used for password storage."
        ),
        security_benefit=(
            "Removes reliance on a cryptographically broken hash algorithm."
        ),
        ai_powered=False,
    )


_HANDLERS = {
    Category.COMMAND_INJECTION_RISK: _remediate_command_injection,
    Category.UNSAFE_DESERIALIZATION: _remediate_deserialization,
    Category.HARDCODED_SECRET: _remediate_hardcoded_secret,
    Category.SQL_CONSTRUCTION_RISK: _remediate_sql_injection,
    Category.WEAK_CRYPTO: _remediate_weak_crypto,
}


def build_remediation(
    finding: Finding,
    ai_result: Optional[AIReasoningResult] = None,
) -> Remediation:
    if ai_result is not None and ai_result.proposed_code:
        return Remediation(
            finding_id=finding.finding_id,
            supported=True,
            original_code=finding.code_snippet,
            proposed_code=ai_result.proposed_code,
            explanation=ai_result.patch_explanation,
            security_benefit=ai_result.remediation_strategy,
            label="AI-Generated Proposed Remediation",
            ai_powered=True,
        )

    handler = _HANDLERS.get(finding.category)
    if handler is None:
        return Remediation(
            finding_id=finding.finding_id,
            supported=False,
            original_code=finding.code_snippet,
            proposed_code=None,
            explanation="No automated remediation template is available for this category yet.",
            security_benefit="N/A",
            ai_powered=False,
        )
    return handler(finding)

