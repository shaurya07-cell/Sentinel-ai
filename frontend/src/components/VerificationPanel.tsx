import { Verification, Regression } from "../types";

interface Props {
  verification: Verification;
  regression: Regression;
}

function CheckRow({ name, passed, detail }: { name: string; passed: boolean; detail: string }) {
  return (
    <div className="flex items-start gap-3 py-2">
      <span
        className={`mt-0.5 shrink-0 h-5 w-5 rounded-full flex items-center justify-center text-xs font-bold ${
          passed ? "bg-safe/15 text-emerald-300" : "bg-danger/15 text-rose-300"
        }`}
      >
        {passed ? "✓" : "✗"}
      </span>
      <div className="min-w-0">
        <p className="text-sm font-medium text-slate-200">{name}</p>
        <p className="text-xs text-slate-500 mt-0.5">{detail}</p>
      </div>
    </div>
  );
}

export default function VerificationPanel({ verification, regression }: Props) {
  return (
    <div className="grid sm:grid-cols-2 gap-4">
      <section className="rounded-xl border border-panelBorder bg-panel/50 p-5">
        <h3 className="text-sm font-bold text-slate-200 mb-1 flex items-center gap-2">
          <span className="text-accent">05</span> Verification
        </h3>
        <p className="text-xs text-slate-500 mb-3">
          Real static re-checks against the proposed remediation.
        </p>
        <div className="divide-y divide-panelBorder">
          {verification.checks.map((c, i) => (
            <CheckRow key={i} name={c.check_name} passed={c.passed} detail={c.detail} />
          ))}
        </div>
        <p className="mt-3 text-xs text-slate-500 border-t border-panelBorder pt-3">
          {verification.verification_note}
        </p>
      </section>

      <section className="rounded-xl border border-panelBorder bg-panel/50 p-5">
        <h3 className="text-sm font-bold text-slate-200 mb-1 flex items-center gap-2">
          <span className="text-accent">06</span> {regression.label}
        </h3>
        <p className="text-xs text-slate-500 mb-3">
          Targeted checks confirming the fix holds — not a full test suite run.
        </p>
        <div className="divide-y divide-panelBorder">
          {regression.checks.map((c, i) => (
            <CheckRow key={i} name={c.check_name} passed={c.passed} detail={c.detail} />
          ))}
        </div>
      </section>
    </div>
  );
}
