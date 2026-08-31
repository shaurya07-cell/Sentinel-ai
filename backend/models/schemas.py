"""
SENTINEL-AI — Pydantic data models.

All pipeline stages consume/produce these typed structures instead of
passing around loose dictionaries. This keeps the six-stage pipeline
honest: every stage has a well-defined contract.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# Enums
# --------------------------------------------------------------------------

class Severity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Category(str, Enum):
    COMMAND_INJECTION_RISK = "command_injection_risk"
    UNSAFE_DESERIALIZATION = "unsafe_deserialization"
    HARDCODED_SECRET = "hardcoded_secret"
    SQL_CONSTRUCTION_RISK = "sql_construction_risk"
    WEAK_CRYPTO = "weak_cryptographic_pattern"


class FinalStatus(str, Enum):
    VERIFIED_DEFENSE = "VERIFIED_DEFENSE"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    NO_FINDINGS = "NO_FINDINGS"


# --------------------------------------------------------------------------
# Stage 1 — DETECT
# --------------------------------------------------------------------------

class Finding(BaseModel):
    finding_id: str
    title: str
    category: Category
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_rationale: str
    file_path: str
    line_number: int
    column_number: int = 0
    rule_id: str
    description: str
    code_snippet: str


# --------------------------------------------------------------------------
# Stage 2 — COLLECT EVIDENCE
# --------------------------------------------------------------------------

class Evidence(BaseModel):
    finding_id: str
    file_path: str
    line_number: int
    code_snippet: str
    context_before: List[str]
    context_after: List[str]
    ast_node_type: str
    triggered_rule: str
    relevant_call: Optional[str] = None
    relevant_arguments: List[str] = Field(default_factory=list)
    evidence_summary: str


# --------------------------------------------------------------------------
# Gemini AI Structured Output Model
# --------------------------------------------------------------------------

class AIReasoningResult(BaseModel):
    finding_id: str
    root_cause: str
    security_impact: str
    attack_surface: str
    reasoning_summary: str
    remediation_strategy: str
    proposed_code: str
    patch_explanation: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    limitations: str


# --------------------------------------------------------------------------
# Stage 3 — REASON
# --------------------------------------------------------------------------

class Reasoning(BaseModel):
    finding_id: str
    what_was_detected: str
    why_dangerous: str
    likely_root_cause: str
    potential_impact: str
    security_principle: str
    attack_surface: Optional[str] = None
    remediation_strategy: Optional[str] = None
    confidence_score: Optional[float] = None
    limitations: Optional[str] = None
    ai_powered: bool = False


# --------------------------------------------------------------------------
# Stage 4 — REMEDIATE
# --------------------------------------------------------------------------

class Remediation(BaseModel):
    finding_id: str
    supported: bool
    original_code: str
    proposed_code: Optional[str] = None
    explanation: str
    security_benefit: str
    label: str = "Proposed Remediation"
    diff: Optional[str] = None
    ai_powered: bool = False


# --------------------------------------------------------------------------
# Stage 5 — VERIFY
# --------------------------------------------------------------------------

class VerificationCheck(BaseModel):
    check_name: str
    passed: bool
    detail: str


class Verification(BaseModel):
    finding_id: str
    checks: List[VerificationCheck]
    all_passed: bool
    verification_note: str


# --------------------------------------------------------------------------
# Stage 6 — REGRESSION TEST
# --------------------------------------------------------------------------

class RegressionCheck(BaseModel):
    check_name: str
    passed: bool
    detail: str


class Regression(BaseModel):
    finding_id: str
    checks: List[RegressionCheck]
    all_passed: bool
    label: str = "Targeted Security Regression Check"


# --------------------------------------------------------------------------
# Aggregate per-finding pipeline record
# --------------------------------------------------------------------------

class FindingPipelineRecord(BaseModel):
    finding: Finding
    evidence: Evidence
    reasoning: Reasoning
    remediation: Remediation
    verification: Verification
    regression: Regression
    finding_final_status: FinalStatus


# --------------------------------------------------------------------------
# Top-level response
# --------------------------------------------------------------------------

class ProjectSummary(BaseModel):
    files_scanned: int
    findings_count: int
    analysis_mode: str
    supported_analysis_scope: List[str]
    ai_status: str = "STATIC_FALLBACK"  # "AI_POWERED" | "STATIC_FALLBACK"



class PipelineStageSummary(BaseModel):
    detect: Dict[str, int]
    evidence: Dict[str, int]
    reason: Dict[str, int]
    remediate: Dict[str, int]
    verify: Dict[str, int]
    regression: Dict[str, int]


class AnalysisResponse(BaseModel):
    project_summary: ProjectSummary
    records: List[FindingPipelineRecord]
    pipeline: PipelineStageSummary
    final_status: FinalStatus
    final_status_explanation: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
