import { useState } from "react";
import LandingPage from "./components/LandingPage";
import UploadPanel from "./components/UploadPanel";
import Pipeline from "./components/Pipeline";
import ResultsDashboard from "./components/ResultsDashboard";
import { runDemo, analyzeProject } from "./api/client";
import { AnalysisResponse } from "./types";

type Screen = "landing" | "upload" | "running" | "results";

export default function App() {
  const [screen, setScreen] = useState<Screen>("landing");
  const [mode, setMode] = useState<"DEMO_SCENARIO" | "ANALYZE_YOUR_CODE">("DEMO_SCENARIO");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pendingRequest, setPendingRequest] = useState<Promise<AnalysisResponse> | null>(null);

  const reset = () => {
    setScreen("landing");
    setResult(null);
    setError(null);
    setPendingRequest(null);
  };

  const startDemo = () => {
    setError(null);
    setMode("DEMO_SCENARIO");
    setPendingRequest(runDemo());
    setScreen("running");
  };

  const startUploadFlow = () => {
    setError(null);
    setScreen("upload");
  };

  const handleAnalyze = (file: File) => {
    setError(null);
    setMode("ANALYZE_YOUR_CODE");
    setPendingRequest(analyzeProject(file));
    setScreen("running");
  };

  const handleSuccess = (data: AnalysisResponse) => {
    setResult(data);
    setScreen("results");
  };

  const handleError = (errorMsg: string) => {
    setError(errorMsg);
    setScreen(mode === "ANALYZE_YOUR_CODE" ? "upload" : "landing");
  };

  if (screen === "landing") {
    return <LandingPage onSelectDemo={startDemo} onSelectUpload={startUploadFlow} error={error} />;
  }

  if (screen === "upload") {
    return <UploadPanel onBack={reset} onAnalyze={handleAnalyze} error={error} />;
  }

  if (screen === "running") {
    return (
      <Pipeline
        mode={mode}
        pendingRequest={pendingRequest}
        onSuccess={handleSuccess}
        onError={handleError}
      />
    );
  }

  if (screen === "results" && result) {
    return <ResultsDashboard result={result} onReset={reset} />;
  }

  return null;
}
