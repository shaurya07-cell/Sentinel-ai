"""
pipeline.py — Orchestrates the six-stage SENTINEL-AI pipeline.

DETECT -> COLLECT EVIDENCE -> REASON -> REMEDIATE -> VERIFY -> REGRESSION

Each stage's typed output feeds the next. The final per-project status
is computed honestly from the actual per-finding results — it is never
hardcoded to VERIFIED_DEFENSE.
"""

from __future__ import annotations

from typing import Dict, List

from core.gemini_reasoning import analyze_finding_with_gemini
from core.project_loader import LoadedProject
from core.scanner import scan_project
from core.evidence import collect_evidence
from core.reasoning import build_reasoning
from core.remediation import build_remediation
from core.verifier import verify_remediation
from core.regression import run_regression_check

from models.schemas import (
    AnalysisResponse, ProjectSummary, PipelineStageSummary,
    FindingPipelineRecord, FinalStatus,
)

import logging

logger = logging.getLogger("sentinel.pipeline")

SUPPORTED_SCOPE = [
    "Unsafe command execution (os.system, os.popen, subprocess shell=True)",
    "Unsafe deserialization (pickle.load/loads, unsafe yaml.load)",
    "Hardcoded secrets (password/secret/token/key literals)",
    "SQL injection risk via dynamic query construction",
    "Weak cryptographic hash usage (MD5, SHA-1)",
]


def _per_finding_status(all_verified: bool, all_regressed: bool, remediation_supported: bool) -> FinalStatus:
    if not remediation_supported:
        return FinalStatus.PARTIALLY_VERIFIED
    if all_verified and all_regressed:
        return FinalStatus.VERIFIED_DEFENSE
    return FinalStatus.VERIFICATION_FAILED


def run_pipeline(project: LoadedProject, analysis_mode: str) -> AnalysisResponse:
    # ---------------- Stage 1: DETECT ----------------
    findings = scan_project(project.python_files, project.relative_path)

    # Preload source lines per relative path for evidence context lookups.
    file_source_lines: Dict[str, List[str]] = {}
    for abs_path in project.python_files:
        rel = project.relative_path(abs_path)
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as fh:
                file_source_lines[rel] = fh.read().splitlines()
        except OSError:
            file_source_lines[rel] = []

    from concurrent.futures import ThreadPoolExecutor

    # ---------------- Stage 2: COLLECT EVIDENCE ----------------
    evidences = [collect_evidence(f, file_source_lines) for f in findings]

    # Optional Real Gemini AI Reasoning — executed concurrently for speed
    ai_results = [None] * len(findings)
    if findings:
        with ThreadPoolExecutor(max_workers=min(len(findings), 8)) as executor:
            ai_results = list(executor.map(
                lambda pair: analyze_finding_with_gemini(pair[0], pair[1]),
                zip(findings, evidences)
            ))

    records: List[FindingPipelineRecord] = []

    for finding, evidence, ai_result in zip(findings, evidences, ai_results):
        # ---------------- Stage 3: REASON ----------------
        reasoning = build_reasoning(finding, evidence, ai_result)

        # ---------------- Stage 4: REMEDIATE ----------------
        remediation = build_remediation(finding, ai_result)

        # ---------------- Stage 5: VERIFY ----------------
        verification = verify_remediation(finding, remediation)

        # ---------------- Stage 6: REGRESSION TEST ----------------
        regression = run_regression_check(finding, remediation)

        finding_status = _per_finding_status(
            verification.all_passed, regression.all_passed, remediation.supported
        )

        records.append(FindingPipelineRecord(
            finding=finding,
            evidence=evidence,
            reasoning=reasoning,
            remediation=remediation,
            verification=verification,
            regression=regression,
            finding_final_status=finding_status,
        ))

    ai_count = sum(1 for r in records if r.reasoning.ai_powered)
    if ai_count > 0:
        ai_status = "AI_POWERED"
        logger.info(f"[PIPELINE MODE] AI_POWERED mode activated for pipeline run ({ai_count}/{len(records)} findings analyzed with Gemini AI).")
    else:
        ai_status = "STATIC_FALLBACK"
        logger.info("[PIPELINE MODE] STATIC_FALLBACK mode activated for pipeline run (0 findings analyzed with Gemini AI).")

    project_summary = ProjectSummary(
        files_scanned=len(project.python_files),
        findings_count=len(findings),
        analysis_mode=analysis_mode,
        supported_analysis_scope=SUPPORTED_SCOPE,
        ai_status=ai_status,
    )


    pipeline_summary = PipelineStageSummary(
        detect={"findings_detected": len(findings)},
        evidence={"evidence_records_collected": len(records)},
        reason={"reasoning_records_generated": len(records)},
        remediate={
            "remediations_proposed": sum(1 for r in records if r.remediation.supported),
            "remediations_unsupported": sum(1 for r in records if not r.remediation.supported),
        },
        verify={
            "checks_passed": sum(1 for r in records if r.verification.all_passed),
            "checks_failed": sum(1 for r in records if not r.verification.all_passed),
        },
        regression={
            "regressions_passed": sum(1 for r in records if r.regression.all_passed),
            "regressions_failed": sum(1 for r in records if not r.regression.all_passed),
        },
    )

    final_status, explanation = _compute_final_status(records)

    return AnalysisResponse(
        project_summary=project_summary,
        records=records,
        pipeline=pipeline_summary,
        final_status=final_status,
        final_status_explanation=explanation,
    )


def _compute_final_status(records: List[FindingPipelineRecord]) -> tuple[FinalStatus, str]:
    if not records:
        return (
            FinalStatus.NO_FINDINGS,
            "No supported security patterns were detected in the scanned Python "
            "source files. This reflects the current, deliberately limited "
            "detector set — it is not a guarantee the project is free of "
            "vulnerabilities outside that scope.",
        )

    statuses = [r.finding_final_status for r in records]

    if all(s == FinalStatus.VERIFIED_DEFENSE for s in statuses):
        return (
            FinalStatus.VERIFIED_DEFENSE,
            f"All {len(records)} finding(s) received a proposed remediation that "
            "passed static verification and the targeted regression check.",
        )

    if any(s == FinalStatus.VERIFICATION_FAILED for s in statuses):
        failed = sum(1 for s in statuses if s == FinalStatus.VERIFICATION_FAILED)
        return (
            FinalStatus.VERIFICATION_FAILED,
            f"{failed} of {len(records)} finding(s) had a proposed remediation that "
            "failed static verification or the targeted regression check — the "
            "flagged pattern was still detected after the proposed fix.",
        )

    return (
        FinalStatus.PARTIALLY_VERIFIED,
        "Some finding(s) do not yet have an automated remediation template "
        "available, so complete verification was not possible for the full "
        "finding set, even though no verification actively failed.",
    )
