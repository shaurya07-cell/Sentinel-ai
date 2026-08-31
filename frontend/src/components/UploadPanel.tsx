import { useCallback, useRef, useState } from "react";

interface Props {
  onBack: () => void;
  onAnalyze: (file: File) => void;
  error: string | null;
}

export default function UploadPanel({ onBack, onAnalyze, error }: Props) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!file.name.toLowerCase().endsWith(".zip")) {
      setLocalError("Invalid file format. Please upload a Python project as a .zip archive.");
      setSelectedFile(null);
      return;
    }
    setLocalError(null);
    setSelectedFile(file);
  }, []);

  return (
    <div className="min-h-screen bg-void bg-grid flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-xl animate-fade-in-up">
        <button
          onClick={onBack}
          className="text-slate-500 hover:text-slate-300 text-sm mb-6 inline-flex items-center gap-1"
        >
          ← Back
        </button>

        <h2 className="text-2xl font-bold text-white mb-1">Analyze Authorized Code</h2>
        <p className="text-sm text-slate-500 mb-6">
          Upload a Python source project as a .zip archive.
        </p>

        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragActive(true);
          }}
          onDragLeave={() => setDragActive(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragActive(false);
            handleFiles(e.dataTransfer.files);
          }}
          onClick={() => inputRef.current?.click()}
          className={`cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
            dragActive
              ? "border-accent bg-accent/5"
              : "border-panelBorder bg-panel/40 hover:border-slate-600"
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".zip"
            className="hidden"
            onChange={(e) => handleFiles(e.target.files)}
          />
          <div className="text-3xl mb-3">📦</div>
          {selectedFile ? (
            <p className="text-slate-200 font-medium">{selectedFile.name}</p>
          ) : (
            <>
              <p className="text-slate-300 font-medium">Drag and drop ZIP</p>
              <p className="text-slate-500 text-sm mt-1">or click to choose a project ZIP</p>
            </>
          )}
        </div>

        <div className="mt-6 space-y-1.5 text-xs text-slate-500">
          <p>
            <span className="text-slate-400 font-medium">Supported:</span> Python source
            projects (.zip)
          </p>
          <p className="text-accent/90">
            Static analysis only — uploaded code is never executed.
          </p>
          <p>Authorized use only.</p>
        </div>

        {(error || localError) && (
          <div className="mt-5 rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-rose-300">
            {error || localError}
          </div>
        )}

        <button
          disabled={!selectedFile}
          onClick={() => selectedFile && onAnalyze(selectedFile)}
          className="mt-6 w-full rounded-lg bg-accent disabled:bg-panel disabled:text-slate-600 disabled:cursor-not-allowed text-void font-semibold py-3 hover:bg-cyan-300 transition-colors"
        >
          Run SENTINEL Analysis
        </button>
      </div>
    </div>
  );
}
