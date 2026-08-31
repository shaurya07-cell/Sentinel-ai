export type Severity = "HIGH" | "MEDIUM" | "LOW";

export type Category =
  | "command_injection_risk"
  | "unsafe_deserialization"
  | "hardcoded_secret"
  | "sql_construction_risk"
  | "weak_cryptographic_pattern";

export type FinalStatus =
  | "VERIFIED_DEFENSE"
  | "PARTIALLY_VERIFIED"
  | "VERIFICATION_FAILED"
  | "NO_FINDINGS";

export interface Finding {
  finding_id: string;
  title: string;
  category: Category;
  severity: Severity;
  confidence: number;
  confidence_rationale: string;
  file_path: string;
  line_number: number;
  column_number: number;
  rule_id: string;
  description: string;
  code_snippet: string;
}

export interface Evidence {
  finding_id: string;
  file_path: string;
  line_number: number;
  code_snippet: string;
  context_before: string[];
  context_after: string[];
  ast_node_type: string;
  triggered_rule: string;
  relevant_call: string | null;
  relevant_arguments: string[];
  evidence_summary: string;
}

export interface Reasoning {
  finding_id: string;
  what_was_detected: string;
  why_dangerous: string;
  likely_root_cause: string;
  potential_impact: string;
  security_principle: string;
  attack_surface?: string | null;
  remediation_strategy?: string | null;
  confidence_score?: number | null;
  limitations?: string | null;
  ai_powered?: boolean;
}

export interface Remediation {
  finding_id: string;
  supported: boolean;
  original_code: string;
  proposed_code: string | null;
  explanation: string;
  security_benefit: string;
  label: string;
  diff?: string | null;
  ai_powered?: boolean;
}

export interface VerificationCheck {
  check_name: string;
  passed: boolean;
  detail: string;
}

export interface Verification {
  finding_id: string;
  checks: VerificationCheck[];
  all_passed: boolean;
  verification_note: string;
}

export interface RegressionCheck {
  check_name: string;
  passed: boolean;
  detail: string;
}

export interface Regression {
  finding_id: string;
  checks: RegressionCheck[];
  all_passed: boolean;
  label: string;
}

export interface FindingPipelineRecord {
  finding: Finding;
  evidence: Evidence;
  reasoning: Reasoning;
  remediation: Remediation;
  verification: Verification;
  regression: Regression;
  finding_final_status: FinalStatus;
}

export interface ProjectSummary {
  files_scanned: number;
  findings_count: number;
  analysis_mode: string;
  supported_analysis_scope: string[];
  ai_status?: string;
}

export interface PipelineStageSummary {
  detect: Record<string, number>;
  evidence: Record<string, number>;
  reason: Record<string, number>;
  remediate: Record<string, number>;
  verify: Record<string, number>;
  regression: Record<string, number>;
}

export interface AnalysisResponse {
  project_summary: ProjectSummary;
  records: FindingPipelineRecord[];
  pipeline: PipelineStageSummary;
  final_status: FinalStatus;
  final_status_explanation: string;
}

export type Mode = "landing" | "demo" | "upload";
