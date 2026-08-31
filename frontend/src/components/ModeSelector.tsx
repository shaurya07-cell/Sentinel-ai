interface Props {
  onSelectDemo: () => void;
  onSelectUpload: () => void;
  error?: string | null;
}

export default function ModeSelector({ onSelectDemo, onSelectUpload, error }: Props) {
  return (
    <div className="min-h-screen bg-void bg-grid bg-grid relative overflow-hidden flex flex-col items-center justify-center px-6">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(34,211,238,0.10),transparent_55%)]" />

      <div className="relative z-10 max-w-3xl text-center animate-fade-in-up">
        <div className="inline-flex items-center gap-2 rounded-full border border-panelBorder bg-panel/60 px-4 py-1.5 text-xs font-medium text-accent mb-8">
          <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse-glow" />
          STATIC ANALYSIS ONLY — UPLOADED CODE IS NEVER EXECUTED
        </div>

        {error && (
          <div className="mb-6 rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-rose-300">
            {error}
          </div>
        )}

        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight text-white">
          SENTINEL<span className="text-accent">-AI</span>
        </h1>
        <p className="mt-4 text-lg sm:text-xl text-slate-400 font-medium">
          Autonomous Cyber Reasoning &amp; Verified Defense
        </p>

        <p className="mt-8 max-w-xl mx-auto text-sm text-slate-500 leading-relaxed">
          Evidence-grounded static security analysis for authorized Python source
          code. Uploaded projects are never executed.
        </p>

        <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={onSelectDemo}
            className="group relative px-7 py-3.5 rounded-lg bg-panel border border-panelBorder hover:border-accent/60 transition-colors text-slate-200 font-semibold shadow-glow"
          >
            <span className="text-accent mr-2">▶</span> Run Demo Scenario
          </button>
          <button
            onClick={onSelectUpload}
            className="px-7 py-3.5 rounded-lg bg-accent text-void hover:bg-cyan-300 transition-colors font-semibold"
          >
            Analyze Authorized Code
          </button>
        </div>

        <div className="mt-16 grid grid-cols-2 sm:grid-cols-6 gap-2 text-[11px] text-slate-500 font-mono">
          {["DETECT", "EVIDENCE", "REASON", "REMEDIATE", "VERIFY", "REGRESSION"].map(
            (stage, i) => (
              <div
                key={stage}
                className="rounded border border-panelBorder bg-panel/50 py-2 px-1 tracking-wider"
              >
                0{i + 1} {stage}
              </div>
            )
          )}
        </div>
      </div>

      <p className="relative z-10 mt-16 text-[11px] text-slate-600 max-w-md text-center">
        Analyze only projects you are authorized to inspect. This prototype
        performs authorized static source-code analysis — it does not perform
        penetration testing or scan external systems.
      </p>
    </div>
  );
}
