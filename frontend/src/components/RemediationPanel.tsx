import { Remediation } from "../types";

interface Props {
  remediation: Remediation;
}

export default function RemediationPanel({ remediation }: Props) {
  return (
    <section className="rounded-xl border border-panelBorder bg-panel/50 p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <span className="text-accent">04</span> {remediation.label}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            In-memory proposed patch only — your uploaded files are never modified on disk.
          </p>
        </div>
        {remediation.ai_powered ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            AI-Generated Remediation
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
            Static Template Patch
          </span>
        )}
      </div>

      {!remediation.supported ? (
        <div className="rounded-lg border border-warn/30 bg-warn/5 px-4 py-3 text-sm text-amber-300">
          No automated remediation template is available for this finding category yet.
        </div>
      ) : (
        <>
          <div className="grid sm:grid-cols-2 gap-3">
            <div>
              <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold mb-1.5">
                Before
              </p>
              <pre className="rounded-lg border border-danger/30 bg-danger/5 p-3 text-xs font-mono text-rose-200 overflow-x-auto whitespace-pre-wrap">
                {remediation.original_code}
              </pre>
            </div>
            <div>
              <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold mb-1.5">
                Proposed Remediation
              </p>
              <pre className="rounded-lg border border-safe/30 bg-safe/5 p-3 text-xs font-mono text-emerald-200 overflow-x-auto whitespace-pre-wrap">
                {remediation.proposed_code}
              </pre>
            </div>
          </div>

          <div className="mt-4 space-y-2 text-sm">
            <p className="text-slate-300">
              <span className="text-slate-500">Explanation: </span>
              {remediation.explanation}
            </p>
            <p className="text-slate-300">
              <span className="text-slate-500">Security benefit: </span>
              {remediation.security_benefit}
            </p>
          </div>
        </>
      )}
    </section>
  );
}
