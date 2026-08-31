"""
verifier.py — Stage 5: VERIFY

Performs REAL static checks against the proposed remediation:
  1. Attempts to parse the proposed code as valid Python (syntax check).
  2. Re-runs a category-specific detector against the proposed code text
     to confirm the original dangerous pattern no longer triggers.

This never claims the user's actual files were modified — it operates
purely on the in-memory `proposed_code` string produced in Stage 4.
"""

from __future__ import annotations

import ast
import re

from models.schemas import (
    Finding, Remediation, Verification, VerificationCheck, Category,
)


def _try_parse(code: str) -> tuple[bool, str]:
    """Best-effort syntax validation of a proposed snippet. Multi-line
    templates with leading comments are stripped of comment-only lines
    that aren't valid statements on their own before parsing when needed."""
    candidates = [code]
    # Also try without comment lines, since some templates contain a
    # comment followed by a real statement and both should independently
    # be syntactically sound Python.
    no_comments = "\n".join(
        line for line in code.splitlines() if not line.strip().startswith("#")
    )
    if no_comments.strip() and no_comments != code:
        candidates.append(no_comments)

    last_error = ""
    for candidate in candidates:
        try:
            ast.parse(candidate)
            return True, "Proposed code parses as valid Python."
        except SyntaxError as exc:
            last_error = str(exc)
    return False, f"Proposed code failed to parse: {last_error}"


_STILL_VULNERABLE_PATTERNS = {
    Category.COMMAND_INJECTION_RISK: re.compile(
        r"os\.system\(|os\.popen\(|shell\s*=\s*True", re.IGNORECASE
    ),
    Category.UNSAFE_DESERIALIZATION: re.compile(
        r"pickle\.loads?\(|yaml\.load\((?!.*Loader\s*=\s*yaml\.SafeLoader)",
        re.IGNORECASE,
    ),
    Category.HARDCODED_SECRET: re.compile(
        r"=\s*['\"][^'\"]{4,}['\"]"
    ),
    Category.SQL_CONSTRUCTION_RISK: re.compile(
        r"execute\(\s*f['\"]|execute\(.*\+.*\)|execute\(.*%\s|\.format\("
    ),
    Category.WEAK_CRYPTO: re.compile(r"hashlib\.(md5|sha1)\(", re.IGNORECASE),
}


def _rule_still_triggers(category: Category, proposed_code: str) -> bool:
    pattern = _STILL_VULNERABLE_PATTERNS.get(category)
    if pattern is None:
        return False
    return bool(pattern.search(proposed_code))


def verify_remediation(finding: Finding, remediation: Remediation) -> Verification:
    checks: list[VerificationCheck] = []

    if not remediation.supported or remediation.proposed_code is None:
        checks.append(VerificationCheck(
            check_name="Remediation availability",
            passed=False,
            detail="No automated remediation is available for this finding category.",
        ))
        return Verification(
            finding_id=finding.finding_id,
            checks=checks,
            all_passed=False,
            verification_note="Verification skipped — no remediation was proposed.",
        )

    syntax_ok, syntax_detail = _try_parse(remediation.proposed_code)
    checks.append(VerificationCheck(
        check_name="Python syntax validation",
        passed=syntax_ok,
        detail=syntax_detail,
    ))

    still_triggers = _rule_still_triggers(finding.category, remediation.proposed_code)
    checks.append(VerificationCheck(
        check_name=f"Original detection rule ({finding.rule_id}) re-check",
        passed=not still_triggers,
        detail=(
            "Original vulnerable pattern no longer matches the proposed code."
            if not still_triggers else
            "Original vulnerable pattern still matches the proposed code — "
            "remediation is incomplete."
        ),
    ))

    checks.append(VerificationCheck(
        check_name="Dangerous pattern removed",
        passed=not still_triggers,
        detail=(
            "Static re-scan of the proposed code found no instance of the "
            "flagged dangerous API/pattern."
            if not still_triggers else
            "Static re-scan still found the flagged dangerous API/pattern."
        ),
    ))

    all_passed = all(c.passed for c in checks)
    note = (
        "All targeted static verification checks passed for this finding."
        if all_passed else
        "One or more verification checks failed — remediation for this finding "
        "should be treated as incomplete."
    )

    return Verification(
        finding_id=finding.finding_id,
        checks=checks,
        all_passed=all_passed,
        verification_note=note,
    )
