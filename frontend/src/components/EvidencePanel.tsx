import { Evidence } from "../types";

interface Props {
  evidence: Evidence;
}

export default function EvidencePanel({ evidence }: Props) {
  return (
    <section className="rounded-xl border border-panelBorder bg-panel/50 p-5">
      <h3 className="text-sm font-bold text-slate-200 mb-1 flex items-center gap-2">
        <span className="text-accent">02</span> Evidence
      </h3>
      <p className="text-xs text-slate-500 mb-4">
        Collected directly from the actual uploaded source — nothing here is invented.
      </p>

      <div className="rounded-lg border border-panelBorder bg-void/60 overflow-hidden mb-4">
        <div className="flex items-center justify-between px-4 py-2 border-b border-panelBorder text-xs font-mono text-slate-500">
          <span>{evidence.file_path}</span>
          <span>line {evidence.line_number}</span>
        </div>
        <div className="font-mono text-xs leading-relaxed p-4">
          {evidence.context_before.map((line, i) => (
            <div key={`before-${i}`} className="text-slate-600 px-2">
              {line || "\u00A0"}
            </div>
          ))}
          <div className="bg-danger/10 border-l-2 border-danger px-2 text-rose-200">
            {evidence.code_snippet || "\u00A0"}
          </div>
          {evidence.context_after.map((line, i) => (
            <div key={`after-${i}`} className="text-slate-600 px-2">
              {line || "\u00A0"}
            </div>
          ))}
        </div>
      </div>

      <dl className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <dt className="text-slate-500">AST node type</dt>
          <dd className="text-slate-300 font-mono">{evidence.ast_node_type}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Triggered rule</dt>
          <dd className="text-slate-300 font-mono">{evidence.triggered_rule}</dd>
        </div>
        {evidence.relevant_call && (
          <div className="col-span-2">
            <dt className="text-slate-500">Relevant call</dt>
            <dd className="text-slate-300 font-mono">{evidence.relevant_call}</dd>
          </div>
        )}
      </dl>

      <p className="mt-4 text-xs text-slate-500 leading-relaxed border-t border-panelBorder pt-3">
        {evidence.evidence_summary}
      </p>
    </section>
  );
}
