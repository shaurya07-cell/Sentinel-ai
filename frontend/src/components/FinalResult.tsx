import { FinalStatus } from "../types";

interface Props {
  status: FinalStatus;
  explanation: string;
}

const CONFIG: Record<FinalStatus, { label: string; classes: string; icon: string }> = {
  VERIFIED_DEFENSE: {
    label: "VERIFIED DEFENSE",
    classes: "border-safe/40 bg-safe/10 text-emerald-300",
    icon: "🛡️",
  },
  PARTIALLY_VERIFIED: {
    label: "PARTIALLY VERIFIED",
    classes: "border-warn/40 bg-warn/10 text-amber-300",
    icon: "⚠️",
  },
  VERIFICATION_FAILED: {
    label: "VERIFICATION FAILED",
    classes: "border-danger/40 bg-danger/10 text-rose-300",
    icon: "⛔",
  },
  NO_FINDINGS: {
    label: "NO FINDINGS",
    classes: "border-slate-500/40 bg-slate-500/10 text-slate-300",
    icon: "ℹ️",
  },
};

export default function FinalResult({ status, explanation }: Props) {
  const cfg = CONFIG[status];
  return (
    <div className={`rounded-xl border px-6 py-5 ${cfg.classes}`}>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{cfg.icon}</span>
        <h2 className="text-xl font-extrabold tracking-wide">{cfg.label}</h2>
      </div>
      <p className="mt-2 text-sm text-slate-300 leading-relaxed">{explanation}</p>
    </div>
  );
}
