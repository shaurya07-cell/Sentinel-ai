"""
regression.py — Stage 6: TARGETED SECURITY REGRESSION CHECK

Not a full test suite run — explicitly a *targeted* check that:
  1. Re-runs the original static detector against the proposed code.
  2. Confirms the dangerous pattern has not reappeared.
  3. Confirms the patched snippet still parses successfully.

This intentionally reuses the same deterministic logic as verifier.py,
because a regression check's job is to confirm the fix *holds* — not to
invent a different testing method for show.
"""

from __future__ import annotations

from models.schemas import Finding, Remediation, Regression, RegressionCheck
from core.verifier import _try_parse, _rule_still_triggers


def run_regression_check(finding: Finding, remediation: Remediation) -> Regression:
    checks: list[RegressionCheck] = []

    if not remediation.supported or remediation.proposed_code is None:
        checks.append(RegressionCheck(
            check_name="Regression scan",
            passed=False,
            detail="Skipped — no remediation was available to regression-test.",
        ))
        return Regression(finding_id=finding.finding_id, checks=checks, all_passed=False)

    syntax_ok, syntax_detail = _try_parse(remediation.proposed_code)
    checks.append(RegressionCheck(
        check_name="Patched snippet still parses",
        passed=syntax_ok,
        detail=syntax_detail,
    ))

    still_triggers = _rule_still_triggers(finding.category, remediation.proposed_code)
    checks.append(RegressionCheck(
        check_name=f"Dangerous pattern has not reappeared ({finding.rule_id})",
        passed=not still_triggers,
        detail=(
            "Re-running the original static detector against the patched "
            "snippet found no reoccurrence of the flagged pattern."
            if not still_triggers else
            "Re-running the original static detector against the patched "
            "snippet still finds the flagged pattern."
        ),
    ))

    all_passed = all(c.passed for c in checks)
    return Regression(finding_id=finding.finding_id, checks=checks, all_passed=all_passed)
