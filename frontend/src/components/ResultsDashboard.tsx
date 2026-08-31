import { useState } from "react";
import { AnalysisResponse } from "../types";
import FindingCard from "./FindingCard";
import EvidencePanel from "./EvidencePanel";
import ReasoningPanel from "./ReasoningPanel";
import RemediationPanel from "./RemediationPanel";
import VerificationPanel from "./VerificationPanel";
import FinalResult from "./FinalResult";

interface Props {
  result: AnalysisResponse;
  onReset: () => void;
}

export default function ResultsDashboard({ result, onReset }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(
    result.records[0]?.finding.finding_id ?? null
  );

  const selected = result.records.find((r) => r.finding.finding_id === selectedId);

  return (
    <div className="min-h-screen bg-void bg-grid px-6 py-10">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <p className="text-xs font-mono text-accent tracking-widest mb-1">
              {result.project_summary.analysis_mode === "DEMO_SCENARIO"
                ? "DEMO SCENARIO — SAMPLE PROJECT"
                : "ANALYZE YOUR CODE"}
            </p>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-extrabold text-white">SENTINEL-AI Results</h1>
              {result.project_summary.ai_status === "AI_POWERED" ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Gemini AI Analysis Completed
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
                  Static Fallback Analysis
                </span>
              )}
            </div>
          </div>
          <button
            onClick={onReset}
            className="px-4 py-2 rounded-lg border border-panelBorder text-slate-400 hover:text-slate-200 hover:border-slate-600 text-sm transition-colors"
          >
            ← New Analysis
          </button>
        </div>

        {/* Project summary */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          <SummaryStat label="Files scanned" value={result.project_summary.files_scanned} />
          <SummaryStat label="Findings" value={result.project_summary.findings_count} />
          <SummaryStat
            label="Verified"
            value={result.records.filter((r) => r.finding_final_status === "VERIFIED_DEFENSE").length}
          />
          <SummaryStat
            label="Needs attention"
            value={
              result.records.filter((r) => r.finding_final_status !== "VERIFIED_DEFENSE").length
            }
          />
        </div>

        <div className="mb-6">
          <FinalResult status={result.final_status} explanation={result.final_status_explanation} />
        </div>

        <details className="mb-8 rounded-lg border border-panelBorder bg-panel/30 px-4 py-3">
          <summary className="text-xs text-slate-500 cursor-pointer select-none">
            Supported analysis scope
          </summary>
          <ul className="mt-2 text-xs text-slate-500 list-disc list-inside space-y-1">
            {result.project_summary.supported_analysis_scope.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>
        </details>

        {result.records.length === 0 ? (
          <div className="rounded-xl border border-panelBorder bg-panel/40 p-8 text-center text-slate-500">
            No supported security patterns were detected in the scanned files.
          </div>
        ) : (
          <div className="grid lg:grid-cols-[320px_1fr] gap-6">
            {/* Findings list */}
            <div className="space-y-3">
              <h2 className="text-xs font-bold uppercase tracking-wide text-slate-500 mb-1">
                Security Findings ({result.records.length})
              </h2>
              {result.records.map((record) => (
                <FindingCard
                  key={record.finding.finding_id}
                  record={record}
                  active={record.finding.finding_id === selectedId}
                  onSelect={() => setSelectedId(record.finding.finding_id)}
                />
              ))}
            </div>

            {/* Detail panels */}
            {selected && (
              <div className="space-y-4">
                <div className="rounded-xl border border-panelBorder bg-panel/50 p-5">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="text-lg font-bold text-white">{selected.finding.title}</h2>
                      <p className="text-xs text-slate-500 font-mono mt-1">
                        {selected.finding.file_path}:{selected.finding.line_number} ·{" "}
                        {selected.finding.rule_id}
                      </p>
                    </div>
                  </div>
                  <p className="mt-3 text-sm text-slate-300 leading-relaxed">
                    {selected.finding.description}
                  </p>
                  <p className="mt-2 text-xs text-slate-500">
                    Confidence {Math.round(selected.finding.confidence * 100)}% —{" "}
                    {selected.finding.confidence_rationale}
                  </p>
                </div>

                <EvidencePanel evidence={selected.evidence} />
                <ReasoningPanel reasoning={selected.reasoning} />
                <RemediationPanel remediation={selected.remediation} />
                <VerificationPanel
                  verification={selected.verification}
                  regression={selected.regression}
                />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function SummaryStat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-panelBorder bg-panel/40 px-4 py-3">
      <p className="text-2xl font-extrabold text-white">{value}</p>
      <p className="text-[11px] text-slate-500 mt-0.5">{label}</p>
    </div>
  );
}
