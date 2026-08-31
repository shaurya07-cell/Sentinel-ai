import { FindingPipelineRecord, Severity, FinalStatus } from "../types";

const SEVERITY_STYLES: Record<Severity, string> = {
  HIGH: "bg-danger/15 text-rose-300 border-danger/40",
  MEDIUM: "bg-warn/15 text-amber-300 border-warn/40",
  LOW: "bg-slate-500/15 text-slate-300 border-slate-500/40",
};

const STATUS_STYLES: Record<FinalStatus, string> = {
  VERIFIED_DEFENSE: "bg-safe/15 text-emerald-300 border-safe/40",
  PARTIALLY_VERIFIED: "bg-warn/15 text-amber-300 border-warn/40",
  VERIFICATION_FAILED: "bg-danger/15 text-rose-300 border-danger/40",
  NO_FINDINGS: "bg-slate-500/15 text-slate-300 border-slate-500/40",
};

interface Props {
  record: FindingPipelineRecord;
  active: boolean;
  onSelect: () => void;
}

export default function FindingCard({ record, active, onSelect }: Props) {
  const { finding, finding_final_status } = record;

  return (
    <button
      onClick={onSelect}
      className={`w-full text-left rounded-lg border px-4 py-3.5 transition-colors ${
        active
          ? "border-accent/60 bg-accent/5"
          : "border-panelBorder bg-panel/40 hover:border-slate-600"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-slate-200 truncate">{finding.title}</p>
          <p className="mt-1 text-xs text-slate-500 font-mono truncate">
            {finding.file_path}:{finding.line_number}
          </p>
        </div>
        <span
          className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-bold tracking-wide ${SEVERITY_STYLES[finding.severity]}`}
        >
          {finding.severity}
        </span>
      </div>

      <div className="mt-3 flex items-center justify-between gap-2">
        <span className="text-[11px] font-mono text-slate-500">{finding.rule_id}</span>
        <span className="text-[11px] text-slate-500">
          confidence <span className="text-slate-300 font-semibold">{Math.round(finding.confidence * 100)}%</span>
        </span>
      </div>

      <div
        className={`mt-2 inline-block rounded border px-2 py-0.5 text-[10px] font-semibold ${STATUS_STYLES[finding_final_status]}`}
      >
        {finding_final_status.replace(/_/g, " ")}
      </div>
    </button>
  );
}
