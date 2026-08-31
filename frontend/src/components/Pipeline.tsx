import { useEffect, useState } from "react";
import { AnalysisResponse } from "../types";
import { ApiError } from "../api/client";

const STAGES = [
  { id: "detect", label: "DETECT", num: "01", sub: "Scanning AST for security vulnerability patterns..." },
  { id: "evidence", label: "EVIDENCE", num: "02", sub: "Extracting call graphs & code context..." },
  { id: "reason", label: "REASON", num: "03", sub: "Analyzing root cause with Gemini AI..." },
  { id: "remediate", label: "REMEDIATE", num: "04", sub: "Synthesizing AI security remediation patches..." },
  { id: "verify", label: "VERIFY", num: "05", sub: "Re-verifying syntax & target rule removal..." },
  { id: "regression", label: "REGRESSION", num: "06", sub: "Checking anti-reappearance regression..." },
];

interface Props {
  mode: "DEMO_SCENARIO" | "ANALYZE_YOUR_CODE";
  pendingRequest: Promise<AnalysisResponse> | null;
  onSuccess: (data: AnalysisResponse) => void;
  onError: (errorMsg: string) => void;
}

export default function Pipeline({ mode, pendingRequest, onSuccess, onError }: Props) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [resolvedData, setResolvedData] = useState<AnalysisResponse | null>(null);
  const [requestFailed, setRequestFailed] = useState<string | null>(null);

  // Listen to the backend pending promise
  useEffect(() => {
    if (!pendingRequest) return;
    let isMounted = true;
    pendingRequest
      .then((data) => {
        if (isMounted) setResolvedData(data);
      })
      .catch((err) => {
        if (isMounted) {
          const msg = err instanceof ApiError ? err.message : "Analysis failed. Please verify backend service.";
          setRequestFailed(msg);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [pendingRequest]);

  // Stage timer progression
  useEffect(() => {
    if (requestFailed) {
      onError(requestFailed);
      return;
    }

    if (activeIndex >= STAGES.length) {
      if (resolvedData) {
        const t = setTimeout(() => onSuccess(resolvedData), 350);
        return () => clearTimeout(t);
      }
      return;
    }

    // Pause on stage 2 (REASON) / stage 3 (REMEDIATE) until response resolves
    if ((activeIndex === 2 || activeIndex === 3) && !resolvedData) {
      // Hold on stage until resolvedData arrives
      return;
    }

    const delay = resolvedData ? 250 : 500;
    const t = setTimeout(() => setActiveIndex((i) => i + 1), delay);
    return () => clearTimeout(t);
  }, [activeIndex, resolvedData, requestFailed, onSuccess, onError]);

  return (
    <div className="min-h-screen bg-void bg-grid flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-2xl text-center animate-fade-in-up">
        <p className="text-xs font-mono text-accent tracking-widest mb-2">
          {mode === "DEMO_SCENARIO" ? "DEMO SCENARIO" : "ANALYZE YOUR CODE"}
        </p>
        <h2 className="text-xl font-bold text-white mb-2">
          Running SENTINEL-AI Pipeline…
        </h2>
        <p className="text-xs text-slate-500 mb-8">
          Static analysis only — uploaded code is never executed.
        </p>

        <div className="space-y-3">
          {STAGES.map((stage, i) => {
            const done = i < activeIndex;
            const active = i === activeIndex;
            const isWaitingAi = active && (i === 2 || i === 3) && !resolvedData;

            return (
              <div
                key={stage.id}
                className={`flex flex-col rounded-lg border px-5 py-3.5 text-left transition-all duration-300 ${
                  done
                    ? "border-safe/30 bg-safe/5"
                    : active
                    ? "border-accent/50 bg-accent/5 shadow-glow"
                    : "border-panelBorder bg-panel/30"
                }`}
              >
                <div className="flex items-center gap-4">
                  <span
                    className={`font-mono text-xs w-8 ${
                      done ? "text-safe" : active ? "text-accent" : "text-slate-600"
                    }`}
                  >
                    {stage.num}
                  </span>
                  <span
                    className={`font-semibold tracking-wide text-sm flex-1 ${
                      done ? "text-safe" : active ? "text-white" : "text-slate-500"
                    }`}
                  >
                    {stage.label}
                  </span>
                  {done && <span className="text-safe">✓</span>}
                  {active && (
                    <span className="h-2 w-2 rounded-full bg-accent animate-pulse-glow" />
                  )}
                </div>

                {active && (
                  <div className="mt-2 ml-12 text-xs text-slate-400 font-mono flex items-center gap-2">
                    {isWaitingAi ? (
                      <>
                        <span className="inline-block w-3 h-3 border-2 border-accent border-t-transparent rounded-full animate-spin" />
                        <span>Querying Gemini AI Reasoning Engine &amp; Generating Patches...</span>
                      </>
                    ) : (
                      <span>{stage.sub}</span>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

