"""
SENTINEL-AI backend — FastAPI application.

Static analysis only — uploaded code is never executed.
Analyze only projects you are authorized to inspect.
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sentinel.main")

from core.project_loader import (
    load_zip_bytes, load_demo_project, ProjectLoadError, LoadedProject,
)
from core.pipeline import run_pipeline
from models.schemas import AnalysisResponse, HealthResponse

APP_VERSION = "0.1.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEMO_PROJECT_DIR = os.path.join(BASE_DIR, "samples", "vulnerable_demo")

def _load_env_file():
    try:
        from dotenv import load_dotenv
        env_paths = [
            os.path.join(BASE_DIR, ".env"),
            os.path.join(BASE_DIR, "..", ".env"),
        ]
        loaded_path = None
        for env_path in env_paths:
            if os.path.exists(env_path):
                load_dotenv(dotenv_path=env_path, override=True)
                loaded_path = env_path
                break
        if loaded_path:
            logger.info(f"Successfully loaded environment variables from: {loaded_path}")
    except Exception as exc:
        logger.warning(f"Could not load dotenv: {exc}")

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key and api_key != "your_gemini_api_key_here":
        masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "***"
        logger.info(f"[GEMINI CONFIG] GEMINI_API_KEY detected and active (Key: {masked})")
    else:
        logger.warning("[GEMINI CONFIG] GEMINI_API_KEY is missing or unconfigured! Gemini AI mode will fall back to static analysis.")

_load_env_file()

app = FastAPI(
    title="SENTINEL-AI",
    description=(
        "Evidence-grounded static security analysis for authorized Python "
        "source code. Static analysis only — uploaded code is never executed."
    ),
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="sentinel-ai-backend", version=APP_VERSION)


@app.post("/api/demo/run", response_model=AnalysisResponse)
def run_demo() -> AnalysisResponse:
    """
    Runs the full six-stage pipeline against the bundled, deliberately
    vulnerable demo project. This is a demonstration scenario — it is
    NOT a live scan of an arbitrary system.
    """
    project: LoadedProject | None = None
    try:
        project = load_demo_project(DEMO_PROJECT_DIR)
        result = run_pipeline(project, analysis_mode="DEMO_SCENARIO")
        return result
    except ProjectLoadError as exc:
        raise HTTPException(status_code=500, detail=f"Demo project error: {exc}") from exc
    finally:
        if project is not None:
            project.cleanup()


@app.post("/api/project/analyze", response_model=AnalysisResponse)
async def analyze_project(file: UploadFile = File(...)) -> AnalysisResponse:
    """
    Accepts an authorized Python project as a ZIP archive, safely
    extracts it (no code execution at any point), runs real AST-based
    static analysis, and returns the full six-stage pipeline output.
    """
    if file.filename and not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip archives are accepted.")

    data = await file.read()

    project: LoadedProject | None = None
    try:
        project = load_zip_bytes(data)
        result = run_pipeline(project, analysis_mode="ANALYZE_YOUR_CODE")
        return result
    except ProjectLoadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if project is not None:
            project.cleanup()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
