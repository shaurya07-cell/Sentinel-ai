"""
reasoning.py — Stage 3: REASON

Evidence-grounded, deterministic rule-based reasoning. No external LLM
API is called here — this is an intentional, honest design choice for
the hackathon prototype: reasoning text is generated from templates
keyed to the actual finding category and evidence, never fabricated.
"""

from __future__ import annotations

from typing import Optional
from models.schemas import Finding, Evidence, Reasoning, Category, AIReasoningResult


_TEMPLATES = {
    Category.COMMAND_INJECTION_RISK: dict(
        what="A call was detected that executes a command through a system shell "
             "(os.system/os.popen, or subprocess with shell=True / a dynamically "
             "built command).",
        why="Shell execution interprets metacharacters such as ';', '|', '&&', and "
            "backticks. If any part of the executed string is influenced by "
            "external input, an attacker can chain arbitrary additional commands.",
        root_cause="Untrusted or externally-influenced data reaching a shell "
                   "execution sink without validation, allow-listing, or use of a "
                   "non-shell argument-array API.",
        impact="Arbitrary command execution on the host running this code, "
               "potentially leading to full system compromise depending on "
               "process privileges.",
        principle="Principle of least privilege for command execution: avoid "
                  "shell interpretation entirely, prefer argument-array APIs "
                  "(e.g. subprocess.run([...], shell=False)), and never build "
                  "commands via string interpolation of external input.",
    ),
    Category.UNSAFE_DESERIALIZATION: dict(
        what="A call to pickle.load()/pickle.loads() (or yaml.load() without a "
             "safe loader) was detected, deserializing byte/text data into "
             "Python objects.",
        why="pickle's format allows arbitrary object construction and can invoke "
            "arbitrary callables during unpickling. Unsafe YAML loaders can "
            "similarly instantiate arbitrary Python types from the document.",
        root_cause="Deserializing data from a source that is not fully trusted "
                   "(e.g. network input, uploaded files, user-controlled storage) "
                   "using a format capable of arbitrary code execution.",
        impact="Remote code execution during deserialization if the serialized "
               "payload is attacker-controlled.",
        principle="Never deserialize untrusted data with formats that support "
                  "arbitrary object construction; prefer structured, "
                  "schema-validated formats (e.g. JSON with explicit validation) "
                  "or yaml.safe_load().",
    ),
    Category.HARDCODED_SECRET: dict(
        what="A variable whose name matches a credential-like pattern "
             "(password/secret/token/key) is assigned a hardcoded string "
             "literal directly in the source file.",
        why="Secrets committed to source code are exposed to anyone with read "
            "access to the repository or its history, including CI logs, forks, "
            "and future collaborators — and they cannot be rotated without a "
            "code change and redeploy.",
        root_cause="Credential material embedded in source rather than injected "
                   "at runtime through a secret manager or environment variable.",
        impact="Credential leakage enabling unauthorized access to the "
               "associated system, service, or account.",
        principle="Never store secrets in source code; load them from "
                  "environment variables or a dedicated secret-management "
                  "service, and rotate any secret that has ever been committed.",
    ),
    Category.SQL_CONSTRUCTION_RISK: dict(
        what="A database .execute()/.executemany() call was found where the "
             "SQL query string is built via f-string interpolation, string "
             "concatenation, %-formatting, or .format() rather than "
             "parameter placeholders.",
        why="When any interpolated segment originates from external input, an "
            "attacker can inject SQL syntax that changes the query's meaning "
            "(SQL injection), potentially reading, modifying, or deleting data "
            "outside the intended scope.",
        root_cause="Query text and query data are combined before reaching the "
                   "database driver, instead of being kept separate via bound "
                   "parameters.",
        impact="Unauthorized data disclosure, data modification, authentication "
               "bypass, or in severe cases full database compromise.",
        principle="Always use parameterized queries / prepared statements — let "
                  "the database driver bind values, never interpolate them into "
                  "the query string.",
    ),
    Category.WEAK_CRYPTO: dict(
        what="A call to a cryptographically weak hash function (MD5 or SHA-1) "
             "was detected.",
        why="MD5 and SHA-1 have known collision and pre-image weaknesses and are "
            "no longer considered safe for security-sensitive integrity or "
            "authentication purposes.",
        root_cause="Use of a legacy hash algorithm in a context that may be "
                   "security-sensitive (e.g. password hashing, signatures, "
                   "integrity checks) without static analysis being able to "
                   "confirm the exact downstream use.",
        impact="Reduced resistance to collision or forgery attacks in "
               "security-sensitive contexts; if used for password storage, "
               "increased risk of credential recovery via precomputed tables.",
        principle="Use a modern, purpose-appropriate algorithm: SHA-256/SHA-3 "
                  "for integrity, and a dedicated password-hashing function "
                  "(bcrypt, scrypt, or Argon2) for credential storage.",
    ),
}


def build_reasoning(
    finding: Finding,
    evidence: Evidence,
    ai_result: Optional[AIReasoningResult] = None,
) -> Reasoning:
    if ai_result is not None:
        what = (
            f"[AI Analysis] {ai_result.reasoning_summary} "
            f"Flagged at {finding.file_path}:{finding.line_number} by rule {finding.rule_id}."
        )
        return Reasoning(
            finding_id=finding.finding_id,
            what_was_detected=what,
            why_dangerous=ai_result.security_impact,
            likely_root_cause=ai_result.root_cause,
            potential_impact=ai_result.security_impact,
            security_principle=ai_result.remediation_strategy,
            attack_surface=ai_result.attack_surface,
            remediation_strategy=ai_result.remediation_strategy,
            confidence_score=ai_result.confidence_score,
            limitations=ai_result.limitations,
            ai_powered=True,
        )

    template = _TEMPLATES[finding.category]

    what = (
        f"{template['what']} Specifically, this was flagged at "
        f"{finding.file_path}:{finding.line_number} by rule {finding.rule_id} "
        f"(confidence {finding.confidence:.2f})."
    )

    return Reasoning(
        finding_id=finding.finding_id,
        what_was_detected=what,
        why_dangerous=template["why"],
        likely_root_cause=template["root_cause"],
        potential_impact=template["impact"],
        security_principle=template["principle"],
        ai_powered=False,
    )

