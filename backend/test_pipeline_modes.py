import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

def _load_env_file():
    env_paths = [
        os.path.join(backend_dir, "..", ".env"),
        os.path.join(backend_dir, ".env"),
    ]
    for env_path in env_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            key_name = k.strip()
                            val_name = v.strip().strip("'\"")
                            if key_name and key_name not in os.environ:
                                os.environ[key_name] = val_name
            except Exception:
                pass

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

_load_env_file()

from core.project_loader import load_demo_project
from core.pipeline import run_pipeline

def test_static_fallback():
    print("\n--- TEST 1: STATIC FALLBACK MODE (Without GEMINI_API_KEY) ---")
    orig_key = os.environ.pop("GEMINI_API_KEY", None)
    try:
        project = load_demo_project(os.path.join(backend_dir, "samples", "vulnerable_demo"))
        response = run_pipeline(project, "DEMO_SCENARIO")
        print(f"Scanned files: {response.project_summary.files_scanned}")
        print(f"Findings count: {response.project_summary.findings_count}")
        print(f"AI status: {response.project_summary.ai_status}")
        print(f"Final status: {response.final_status.value}")
        
        assert response.project_summary.ai_status == "STATIC_FALLBACK", f"Expected STATIC_FALLBACK, got {response.project_summary.ai_status}"
        assert response.project_summary.findings_count > 0, "Expected findings in demo scenario"
        
        for r in response.records:
            assert not r.reasoning.ai_powered, f"Expected ai_powered=False for {r.finding.finding_id}"
            assert not r.remediation.ai_powered, f"Expected ai_powered=False for {r.finding.finding_id}"
            assert r.verification.all_passed, f"Verification failed for {r.finding.finding_id}: {r.verification.checks}"
            assert r.regression.all_passed, f"Regression failed for {r.finding.finding_id}: {r.regression.checks}"
        
        print("SUCCESS: Static fallback mode verified cleanly!")
    finally:
        if orig_key:
            os.environ["GEMINI_API_KEY"] = orig_key

def test_gemini_ai_powered():
    print("\n--- TEST 2: GEMINI AI POWERED MODE (With GEMINI_API_KEY) ---")
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        print("SKIP: GEMINI_API_KEY is not set in environment. Set GEMINI_API_KEY to execute live API test.")
        return False
        
    project = load_demo_project(os.path.join(backend_dir, "samples", "vulnerable_demo"))
    response = run_pipeline(project, "DEMO_SCENARIO")
    print(f"Scanned files: {response.project_summary.files_scanned}")
    print(f"Findings count: {response.project_summary.findings_count}")
    print(f"AI status: {response.project_summary.ai_status}")
    print(f"Final status: {response.final_status.value}")
    
    for i, r in enumerate(response.records):
        print(f"\n--- Finding {i+1}: {r.finding.title} ({r.finding.rule_id}) ---")
        print(f"  AI Powered Reasoning: {r.reasoning.ai_powered}")
        print(f"  What was detected: {r.reasoning.what_was_detected}")
        print(f"  Root Cause: {r.reasoning.likely_root_cause}")
        print(f"  AI Powered Remediation: {r.remediation.ai_powered}")
        print(f"  Proposed Code:\n{r.remediation.proposed_code}")
        print(f"  Verification All Passed: {r.verification.all_passed}")
        print(f"  Regression All Passed: {r.regression.all_passed}")
        
        if r.reasoning.ai_powered:
            assert r.remediation.ai_powered, f"Expected ai_powered=True for remediation on {r.finding.finding_id}"
            assert r.verification.all_passed, f"Stage 5 Verification failed on AI code for {r.finding.finding_id}: {r.verification.checks}"
            assert r.regression.all_passed, f"Stage 6 Regression failed on AI code for {r.finding.finding_id}: {r.regression.checks}"
        else:
            print(f"  Note: Finding {r.finding.finding_id} used static fallback (Rate limit / Quota reset).")
    
    assert response.project_summary.ai_status == "AI_POWERED", f"Expected AI_POWERED, got {response.project_summary.ai_status}"
    print("\nSUCCESS: Gemini AI powered mode tested & verified cleanly with real API response!")
    return True

if __name__ == "__main__":
    test_static_fallback()
    test_gemini_ai_powered()
