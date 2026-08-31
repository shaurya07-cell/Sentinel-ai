import { Reasoning } from "../types";

interface Props {
  reasoning: Reasoning;
}

const ROWS: { key: keyof Reasoning; label: string }[] = [
  { key: "what_was_detected", label: "What was detected" },
  { key: "why_dangerous", label: "Why it may be dangerous" },
  { key: "likely_root_cause", label: "Likely root cause" },
  { key: "potential_impact", label: "Potential impact" },
  { key: "security_principle", label: "Recommended security principle" },
];

export default function ReasoningPanel({ reasoning }: Props) {
  return (
    <section className="rounded-xl border border-panelBorder bg-panel/50 p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-slate-200 flex items-center gap-2">
            <span className="text-accent">03</span> Root-Cause Reasoning
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Root-cause security analysis & principles.
          </p>
        </div>
        {reasoning.ai_powered ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            Gemini AI Analysis Completed
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">
            Static Fallback Analysis
          </span>
        )}
      </div>

      <div className="space-y-4">
        {ROWS.map((row) => {
          const val = reasoning[row.key] as string | undefined;
          if (!val) return null;
          return (
            <div key={row.key}>
              <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold mb-1">
                {row.label}
              </p>
              <p className="text-sm text-slate-300 leading-relaxed">
                {val}
              </p>
            </div>
          );
        })}
        {reasoning.attack_surface && (
          <div>
            <p className="text-[11px] uppercase tracking-wide text-slate-500 font-semibold mb-1">
              Attack Surface Scenario
            </p>
            <p className="text-sm text-slate-300 leading-relaxed">
              {reasoning.attack_surface}
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
