# SENTINEL-AI: Current Project State Report

> **Document Version:** 1.0.0  
> **Audit Date:** August 30, 2026  
> **Audit Scope:** Comprehensive Read-Only Audit of SENTINEL-AI (Frontend & Backend)  
> **Source of Truth:** Files currently present on disk inside `c:\Users\SHAURYA\Downloads\sentinel-ai 22\sentinel-ai`

---

## 1. Executive Summary

SENTINEL-AI is a specialized **Python static analysis prototype** designed for hackathon demonstration. It features a modern dark-mode React frontend (built with Vite, React 18, TypeScript, and Tailwind CSS) connected to a FastAPI backend (Python 3.10+ / 3.14 compatible).

The core application receives Python source code (either via a bundled demo scenario or a user-uploaded `.zip` archive), safe-extracts the `.py` files into an isolated temporary directory without executing any code, runs an **AST-based static analysis scanner**, and passes findings through a **six-stage pipeline**:

1. **DETECT** — AST-based pattern matching across 5 vulnerability categories.
2. **COLLECT EVIDENCE** — Context line extraction, AST node classification, and rule attribution from source text.
3. **REASON** — Deterministic, template-based root-cause explanations grounded in the finding category.
4. **REMEDIATE** — Category-specific in-memory proposed code fix generation.
5. **VERIFY** — Real static re-inspection of the proposed snippet (Python syntax parse + rule re-check).
6. **REGRESSION TEST** — Targeted static confirmation that the proposed snippet does not re-trigger the detector.

---

## 2. Complete Project Folder Tree & File Catalog

```
sentinel-ai/
│
├── CURRENT_PROJECT_STATE.md        [NEW] Complete project state report (this document)
├── README.md                       Comprehensive project overview, architecture, & setup guide
├── .gitignore                      Git ignore patterns (.venv, node_modules, dist, etc.)
│
├── backend/                        FastAPI Python Backend Application
│   ├── main.py                     FastAPI application, CORS config, and HTTP endpoints
│   ├── requirements.txt            Python dependencies (fastapi, uvicorn, pydantic, python-multipart)
│   │
│   ├── models/
│   │   └── schemas.py              Typed Pydantic models for all 6 pipeline stages & API responses
│   │
│   ├── core/
│   │   ├── project_loader.py       Safe ZIP archive validation, path-traversal protection & temp extraction
│   │   ├── scanner.py              Stage 1: AST-based static detectors & deterministic confidence scoring
│   │   ├── evidence.py             Stage 2: Code snippet & context line extraction
│   │   ├── reasoning.py            Stage 3: Rule-based root cause reasoning generator
│   │   ├── remediation.py          Stage 4: In-memory proposed patch generator
│   │   ├── verifier.py             Stage 5: Static syntax parsing & rule re-verification
│   │   ├── regression.py           Stage 6: Targeted static regression re-check
│   │   └── pipeline.py             Orchestrates all 6 stages & calculates overall final verdict
│   │
│   └── samples/
│       └── vulnerable_demo/        Bundled sample Python files for Demo Scenario
│           ├── report_tool.py      Sample code with command injection, subprocess, & pickle flaws
│           └── user_management.py  Sample code with hardcoded secrets, SQL injection, & MD5 hashing
│
└── frontend/                       React + TypeScript + Vite + Tailwind Frontend Application
    ├── index.html                  HTML template with Inter & JetBrains Mono Google Fonts
    ├── package.json                Node project manifest & dependencies
    ├── package-lock.json           Locked Node dependency graph
    ├── postcss.config.js           PostCSS configuration for Tailwind CSS & Autoprefixer
    ├── tailwind.config.js          Custom theme tokens (void, panel, accent, safe, warn, danger)
    ├── tsconfig.json               TypeScript compiler configuration
    ├── tsconfig.tsbuildinfo        TypeScript build cache
    ├── vite.config.ts              Vite dev server config with /api proxy settings
    │
    └── src/
        ├── App.tsx                 Top-level UI state machine ("landing" | "upload" | "running" | "results")
        ├── main.tsx                React DOM root mount
        ├── index.css               Tailwind directives, custom scrollbars, & keyframe animations
        │
        ├── api/
        │   └── client.ts           Fetch API client wrapper for backend endpoints (/api/*)
        │
        ├── types/
        │   └── index.ts            TypeScript interface definitions matching backend Pydantic schemas
        │
        └── components/
            ├── ModeSelector.tsx    Landing page with hero banner, CTAs, and pipeline badge
            ├── UploadPanel.tsx     Drag-and-drop ZIP file upload interface with safety disclaimers
            ├── Pipeline.tsx        Animated 6-stage execution progress visualization
            ├── FindingCard.tsx     Sidebar card component for individual security findings
            ├── EvidencePanel.tsx   Stage 2 panel displaying code snippet, context, and AST details
            ├── ReasoningPanel.tsx  Stage 3 panel detailing root cause, impact, and principles
            ├── RemediationPanel.tsx Stage 4 panel showing side-by-side Before/After code patches
            ├── VerificationPanel.tsx Stage 5 & 6 panel displaying static verification check checks
            ├── FinalResult.tsx     Top verdict banner (VERIFIED DEFENSE / PARTIALLY VERIFIED / etc.)
            └── ResultsDashboard.tsx Main multi-column results view orchestrating detail panels
```

### Detailed File Responsibilities

| File Path | Description / Primary Responsibility |
| :--- | :--- |
| [`backend/main.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/main.py) | Entry point for FastAPI server. Defines `/api/health`, `/api/demo/run`, and `/api/project/analyze`. Sets CORS middleware. |
| [`backend/models/schemas.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/models/schemas.py) | Pydantic v2 data structures (`Finding`, `Evidence`, `Reasoning`, `Remediation`, `Verification`, `Regression`, `AnalysisResponse`, `FinalStatus`, `Category`, `Severity`). |
| [`backend/core/project_loader.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/project_loader.py) | Enforces ZIP limits (20MB upload, 100MB uncompressed, 2000 files), path traversal checks (`_is_safe_member_path`), extracts `.py` files only into `tempfile.mkdtemp()`, provides cleanup methods. |
| [`backend/core/scanner.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/scanner.py) | Parses Python AST (`ast.parse`) using custom `_Detector(ast.NodeVisitor)` to find command injection, pickle/yaml deserialization, hardcoded secrets, SQL injection, and weak crypto hashes. |
| [`backend/core/evidence.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/evidence.py) | Extracts line snippets and context lines (2 lines before/after) from Python source files. |
| [`backend/core/reasoning.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/reasoning.py) | Maps findings to deterministic template strings detailing problem, root cause, impact, and security principle. |
| [`backend/core/remediation.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/remediation.py) | Generates in-memory proposed Python code replacements for vulnerable snippets. |
| [`backend/core/verifier.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/verifier.py) | Tests proposed code with `ast.parse` syntax check and regex re-checks against original rule pattern. |
| [`backend/core/regression.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/regression.py) | Re-evaluates proposed code string to confirm syntax validity and detector non-triggering. |
| [`backend/core/pipeline.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/pipeline.py) | Sequentially executes Stages 1-6 for each finding and computes overall final verdict (`_compute_final_status`). |
| [`frontend/src/App.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/App.tsx) | Main React view manager switching between landing, upload, pipeline execution, and dashboard screens. |
| [`frontend/src/api/client.ts`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/api/client.ts) | Async fetch wrappers calling `/api/demo/run`, `/api/project/analyze`, and `/api/health`. |
| [`frontend/src/types/index.ts`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/types/index.ts) | TypeScript type definitions mirroring all Pydantic backend models. |
| [`frontend/src/components/ModeSelector.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/ModeSelector.tsx) | Landing view containing branding, disclaimers, pipeline stage pill badges, and scenario selection buttons. |
| [`frontend/src/components/UploadPanel.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/UploadPanel.tsx) | File dropzone interface restricted to `.zip` files with error reporting. |
| [`frontend/src/components/Pipeline.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/Pipeline.tsx) | Progress animation stepping through stages 01 to 06 on fixed intervals while waiting for API call. |
| [`frontend/src/components/ResultsDashboard.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/ResultsDashboard.tsx) | Main layout displaying top stats, final verdict, finding selector list, and detail panels. |

---

## 3. Frontend Audit

- **Framework & Dependencies:** React `^18.3.1`, React DOM `^18.3.1`, Vite `^5.3.1`, TypeScript `^5.5.3`, Tailwind CSS `^3.4.4`, PostCSS `^8.4.39`, Autoprefixer `^10.4.19`.
- **Main Entry Point:** `index.html` loads `src/main.tsx` which mounts `App.tsx` into `#root`.
- **Routing & Navigation:** Single Page Application (SPA) driven by React local state (`type Screen = "landing" | "upload" | "running" | "results"`). No URL router (such as `react-router-dom`) is implemented.
- **State Management:** Simple React `useState` hooks inside `App.tsx` and component-level states. No Redux, Zustand, or Context API.
- **API Service Layer:** [`client.ts`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/api/client.ts) handles HTTP `fetch` calls relative to `/api` proxy. Custom `ApiError` class extracts JSON detail messages on non-200 responses.
- **Design System & Styling:** Custom dark cyberpunk palette defined in [`tailwind.config.js`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/tailwind.config.js):
  - `bg-void` (`#05070a`), `bg-panel` (`#0b0f16`), `border-panelBorder` (`#1c2531`)
  - Accent: `accent` (`#22d3ee` cyan)
  - Status colors: `safe` (`#34d399` emerald), `warn` (`#f59e0b` amber), `danger` (`#f43f5e` rose)
  - Typography: Google Fonts `Inter` (sans) and `JetBrains Mono` (code/mono).

### Major Frontend Components Breakdown

#### 1. [`ModeSelector.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/ModeSelector.tsx)
- **Purpose:** Hero section / Landing view.
- **Props:** `onSelectDemo: () => void`, `onSelectUpload: () => void`.
- **What User Sees:** "SENTINEL-AI" title, "Autonomous Cyber Reasoning & Verified Defense" tagline, pulse badge ("STATIC ANALYSIS ONLY"), two action buttons ("Run Demo Scenario" & "Analyze Authorized Code"), 6 pipeline stage pill badges, legal disclaimers.

#### 2. [`UploadPanel.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/UploadPanel.tsx)
- **Purpose:** File selection for authorized code analysis.
- **Props:** `onBack: () => void`, `onAnalyze: (file: File) => void`, `error: string | null`.
- **What User Sees:** Back button, file drag-and-drop dropzone targeting `.zip` files, selected file indicator, error box (if API rejected upload), "Run SENTINEL Analysis" submit button.

#### 3. [`Pipeline.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/Pipeline.tsx)
- **Purpose:** Visual progress indicator during pipeline execution.
- **Props:** `onComplete: () => void`, `mode: "DEMO_SCENARIO" | "ANALYZE_YOUR_CODE"`.
- **What User Sees:** Animated list of 6 pipeline stages (01 DETECT to 06 REGRESSION). Steps transition from inactive -> active (cyan pulse) -> complete (emerald checkmark) on a timer loop.

#### 4. [`ResultsDashboard.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/ResultsDashboard.tsx)
- **Purpose:** Master-detail view of scan results.
- **Props:** `result: AnalysisResponse`, `onReset: () => void`.
- **What User Sees:** Summary statistics bar (Files scanned, Findings, Verified, Needs attention), `FinalResult` top banner, collapsible analysis scope box, left sidebar finding selector list (`FindingCard`), right column active detail panels (`EvidencePanel`, `ReasoningPanel`, `RemediationPanel`, `VerificationPanel`).

#### 5. [`EvidencePanel.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/EvidencePanel.tsx)
- **Purpose:** Displays Stage 2 evidence.
- **Props:** `evidence: Evidence`.
- **What User Sees:** File path, line number, code context box (2 lines before in gray, flagged line highlighted in red, 2 lines after in gray), AST node type, triggered rule ID, and evidence summary text.

#### 6. [`ReasoningPanel.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/ReasoningPanel.tsx)
- **Purpose:** Displays Stage 3 root-cause analysis.
- **Props:** `reasoning: Reasoning`.
- **What User Sees:** 5 structured text sections: What was detected, Why it may be dangerous, Likely root cause, Potential impact, Recommended security principle.

#### 7. [`RemediationPanel.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/RemediationPanel.tsx)
- **Purpose:** Displays Stage 4 proposed code patch.
- **Props:** `remediation: Remediation`.
- **What User Sees:** Side-by-side comparison boxes: "Before" (original vulnerable line in red) vs "Proposed Remediation" (suggested fix in green), followed by explanation and security benefit notes.

#### 8. [`VerificationPanel.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/VerificationPanel.tsx)
- **Purpose:** Displays Stage 5 (Verification) and Stage 6 (Regression) check results.
- **Props:** `verification: Verification`, `regression: Regression`.
- **What User Sees:** Two side-by-side check lists showing green checkmarks or red X marks for syntax validation, original rule re-checks, and regression non-reappearance tests.

#### 9. [`FinalResult.tsx`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/src/components/FinalResult.tsx)
- **Purpose:** Displays top-level project verdict.
- **Props:** `status: FinalStatus`, `explanation: string`.
- **What User Sees:** Banner with status label (`VERIFIED DEFENSE`, `PARTIALLY VERIFIED`, `VERIFICATION FAILED`, or `NO FINDINGS`) with color-coded border/icon and explanation text.

---

## 4. Backend Audit

- **Framework:** FastAPI (`fastapi==0.115.0` or `0.141.1`), Uvicorn (`uvicorn==0.30.6` or `0.52.4`), Pydantic v2 (`pydantic==2.9.2` or `2.13.5`), Python Standard Library (`ast`, `zipfile`, `tempfile`, `re`, `shutil`).
- **Main Server Entry Point:** [`backend/main.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/main.py). Configures CORS (`allow_origins=["*"]`) and mounts routes.

### API Endpoints Summary

#### 1. `GET /api/health`
- **Purpose:** Service health check.
- **Input:** None.
- **Process:** Constructs `HealthResponse` object.
- **Output:** `{"status": "ok", "service": "sentinel-ai-backend", "version": "0.1.0"}`
- **Modules Involved:** [`main.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/main.py), [`models/schemas.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/models/schemas.py).

#### 2. `POST /api/demo/run`
- **Purpose:** Runs full 6-stage pipeline against bundled sample files.
- **Input:** None.
- **Process:** Calls `load_demo_project("samples/vulnerable_demo")`, copies files to a temp directory, executes `run_pipeline(project, "DEMO_SCENARIO")`, cleans up temp directory in `finally` block.
- **Output:** Complete `AnalysisResponse` JSON object.
- **Modules Involved:** [`main.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/main.py), [`project_loader.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/project_loader.py), [`pipeline.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/pipeline.py).

#### 3. `POST /api/project/analyze`
- **Purpose:** Accepts user `.zip` upload, safe-extracts `.py` files, and runs full pipeline.
- **Input:** `multipart/form-data` request with key `file` containing `.zip` file.
- **Process:** Validates `.zip` extension and file size, reads bytes, calls `load_zip_bytes(data)`, safe-extracts `.py` files into temp directory, runs `run_pipeline(project, "ANALYZE_YOUR_CODE")`, cleans up temp directory in `finally` block.
- **Output:** Complete `AnalysisResponse` JSON object.
- **Modules Involved:** [`main.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/main.py), [`project_loader.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/project_loader.py), [`pipeline.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/pipeline.py).

---

## 5. Security Analysis Engine Audit

SENTINEL-AI currently analyzes **Python source files (`.py`) only**. All other file types in uploaded archives are silently skipped.

### Detection Mechanism
Source code is loaded into memory as text strings and parsed into an Abstract Syntax Tree using Python's built-in `ast.parse()`. An `ast.NodeVisitor` subclass named `_Detector` walks the AST nodes. No code execution occurs.

### Implemented Vulnerability Rules Table

| Rule ID | Category | Language | Detection Method | Severity | Confidence Logic & Rationale | Real or Simulated |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SENTINEL-CMD-001` | `command_injection_risk` | Python | AST (`ast.Call`) | **HIGH** / **MEDIUM** | **0.90** for `os.system`/`os.popen`; **0.94** if arg is not constant; **0.88** for `subprocess` with `shell=True`; **0.95** for `shell=True` + f-string/format/add; **0.55** (MEDIUM severity) for dynamic subprocess without `shell=True`. | **REAL** static AST rule |
| `SENTINEL-DESER-001` | `unsafe_deserialization` | Python | AST (`ast.Call`) | **HIGH** / **MEDIUM** | **0.90** for `pickle.load` / `pickle.loads`; **0.75** (MEDIUM severity) for `yaml.load()` without explicit `Loader=yaml.SafeLoader` or `CSafeLoader`. | **REAL** static AST rule |
| `SENTINEL-SECRET-001` | `hardcoded_secret` | Python | AST (`ast.Assign`) | **HIGH** | **0.80** if variable name matches secret regex (`password`, `secret`, `key`, `token`) and is assigned non-placeholder string literal >= 4 chars; **0.90** if length >= 16. Literals redacted in UI. | **REAL** static AST rule |
| `SENTINEL-SQL-001` | `sql_construction_risk` | Python | AST (`ast.Call`) | **HIGH** | **0.85** if `.execute()` or `.executemany()` first argument is built via f-string (`ast.JoinedStr`), concatenation (`ast.Add`), `%`-formatting (`ast.Mod`), or `.format()`. | **REAL** static AST rule |
| `SENTINEL-CRYPTO-001` | `weak_cryptographic_pattern` | Python | AST (`ast.Call`) | **MEDIUM** | **0.70** if `hashlib.md5()` or `hashlib.sha1()` is directly invoked. | **REAL** static AST rule |

---

## 6. AI & Reasoning Audit

- **Is an LLM connected?** **NO.** There are no external API calls (e.g. OpenAI, Anthropic, Gemini, Ollama) anywhere in the codebase.
- **Reasoning Outputs:** 100% **deterministic and template-based** ([`backend/core/reasoning.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/reasoning.py)). Fixed text dictionaries are selected based on finding `Category`.
- **Confidence Scores:** 100% **deterministic formulas** based on AST node attributes.
- **Remediation Generation:** 100% **template-based** ([`backend/core/remediation.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/core/remediation.py)). Produces static string snippets representing proposed fixes.
- **Patch Application:** Proposed patches exist **only as string variables** in JSON responses. Code files on disk are **never updated or overwritten**.
- **Verification & Regression Testing:** Performs **real static re-checks** against the generated proposed code string using `ast.parse` and regex pattern matching. It does not run actual unit tests or execute code.

### Implementation Status Classification
- **REAL IMPLEMENTATION:** AST-based static detectors, safe ZIP extraction, code snippet extraction, static syntax parsing & regex re-verification of proposed code snippets.
- **DETERMINISTIC / TEMPLATE IMPLEMENTATION:** Root-cause reasoning, proposed patch generation, confidence scores, final status calculation.
- **SIMULATED / PLACEHOLDER:** "Targeted Security Regression Check" (re-uses the exact same static regex re-check as Stage 5 rather than executing real tests or test suites).

---

## 7. Remediation & Verification Audit

When a vulnerability is detected, it moves through the following pipeline lifecycle:

```
Finding (Stage 1)
  │
  ▼
Evidence Collection (Stage 2) ── Pulls 2 lines context before/after from source file
  │
  ▼
Reasoning Generation (Stage 3) ── Selects deterministic category template
  │
  ▼
Remediation (Stage 4) ────────── Creates in-memory proposed code replacement string
  │
  ▼
Verification (Stage 5) ───────── Runs ast.parse() & regex pattern re-check on proposed string
  │
  ▼
Regression Test (Stage 6) ────── Re-evaluates syntax & non-triggering regex on proposed string
  │
  ▼
Final Verdict Calculation ────── Computes VERIFIED_DEFENSE / PARTIALLY_VERIFIED / VERIFICATION_FAILED
```

### Technical Meaning of "Verified Defense"
`VERIFIED_DEFENSE` is assigned if and only if **every** finding in the project receives a proposed code snippet that:
1. Successfully parses as valid Python syntax via `ast.parse()`.
2. Does not match the vulnerable regex pattern for its category in Stage 5 re-check.
3. Does not match the vulnerable regex pattern for its category in Stage 6 regression re-check.

### Critical Discrepancies (UI Claims vs. Backend Reality)
1. **"Targeted Security Regression Check":** The UI panel title implies an independent test suite or dynamic verification step. In reality, Stage 6 (`regression.py`) imports and executes the exact same static regex helper function (`_rule_still_triggers`) used in Stage 5.
2. **"Autonomous Cyber Reasoning":** The branding implies an active AI/LLM model. In reality, all reasoning text is generated from fixed static dictionary templates.
3. **"Proposed Remediation":** The UI shows clean proposed code fixes, but these fixes are never applied back to the user's project files or rendered as a downloadable `.patch` / `.diff` file.

---

## 8. Upload Analysis Flow Audit

```
User selects .zip file in React UI
  │
  ▼
UploadPanel.tsx validates .zip extension client-side
  │
  ▼
API request sent via POST /api/project/analyze (multipart/form-data)
  │
  ▼
FastAPI handler in main.py validates file size (<= 20MB)
  │
  ▼
load_zip_bytes() in project_loader.py validates zip member paths (_is_safe_member_path)
  │
  ▼
.py files extracted to temp directory created via tempfile.mkdtemp(prefix="sentinel_ai_")
  │
  ▼
run_pipeline() in pipeline.py runs scan_project() across extracted .py files
  │
  ▼
Findings piped sequentially through Stages 2, 3, 4, 5, 6
  │
  ▼
shutil.rmtree(root_dir) cleans up temp directory in finally block
  │
  ▼
AnalysisResponse JSON returned to frontend
  │
  ▼
App.tsx sets result state and transitions to ResultsDashboard.tsx
```

### Security Boundaries & Limits
- **Max Upload Size:** 20 MB compressed (`MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024`).
- **Max Extracted Files:** 2,000 files (`MAX_EXTRACTED_FILES = 2000`).
- **Max Total Extracted Size:** 100 MB uncompressed (`MAX_TOTAL_EXTRACTED_SIZE = 100 * 1024 * 1024`).
- **Max Single File Size:** 5 MB (`MAX_SINGLE_FILE_SIZE = 5 * 1024 * 1024`).
- **ZIP Path Traversal Protection:** `_is_safe_member_path()` rejects entries starting with `/`, `\`, absolute paths, Windows drive letters (e.g. `C:`), or containing `..`.
- **Containment Check:** Explicitly checks `dest_path.startswith(normpath(root_dir) + os.sep)`.
- **Code Execution:** Uploaded code is **never executed** (no `import`, no `exec()`, no `eval()`, no `subprocess`).
- **Cleanup:** `project.cleanup()` is guaranteed to execute via `finally` block in `main.py`.

---

## 9. Controlled Demo Flow Audit

The Controlled Demo flow is triggered via `POST /api/demo/run` when the user clicks **"Run Demo Scenario"**.

- **Sample Target Files:** [`backend/samples/vulnerable_demo/report_tool.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/samples/vulnerable_demo/report_tool.py) and [`user_management.py`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/samples/vulnerable_demo/user_management.py).
- **Vulnerabilities Demonstrated:**
  1. `os.system("libreoffice --convert-to pdf " + filename)` (Command Injection)
  2. `subprocess.call(export_cmd, shell=True)` (Command Injection)
  3. `pickle.load(fh)` (Unsafe Deserialization)
  4. `DB_PASSWORD = "sup3rSecretDbPass!"` (Hardcoded Secret)
  5. `API_KEY = "sk_live_9f8a7b6c5d4e3f2a1b0c"` (Hardcoded Secret)
  6. `cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")` (SQL Injection Risk)
  7. `hashlib.md5(password.encode()).hexdigest()` (Weak Cryptographic Hash)
- **Execution Mechanism:** Files are copied into a temporary directory using `load_demo_project()` and processed through the identical `run_pipeline()` path as live uploads.

---

## 10. Current User Experience (Step-by-Step)

1. **Visitor Landing:** User opens `http://localhost:5173`. User sees the dark cyberpunk landing page (`ModeSelector.tsx`) featuring glowing badges and two action buttons.
2. **Scenario Selection:**
   - **Path A (Demo):** User clicks "Run Demo Scenario". App transitions to `Pipeline.tsx` screen.
   - **Path B (Upload):** User clicks "Analyze Authorized Code". App transitions to `UploadPanel.tsx`. User drops/selects a `.zip` file and clicks "Run SENTINEL Analysis". App transitions to `Pipeline.tsx` screen.
3. **Pipeline Progress:** User views 6 pipeline stages sequentially checking off (01 DETECT through 06 REGRESSION) while the backend API request resolves.
4. **Results Viewing:** User lands on `ResultsDashboard.tsx`. User sees top stat metrics, `VERIFIED DEFENSE` verdict banner, left column finding list, and right column breakdown (Evidence, Reasoning, Remediation, Verification).
5. **Reset:** User clicks "← New Analysis" in header to return to landing view.

---

## 11. Current UI/UX Visual Design Breakdown

- **Background:** Deep dark `#05070a` (`bg-void`) with cyan-tinted radial gradient and subtle `#94a3b8` 36px grid overlay (`bg-grid`).
- **Panels & Cards:** Dark slate `#0b0f16` (`bg-panel`) with thin border `#1c2531` (`border-panelBorder`) and rounded corners (`rounded-lg`, `rounded-xl`).
- **Typography:** Sans-serif text rendered in Inter (`#e2e8f0` text-slate-200 / `#94a3b8` text-slate-400 / `#64748b` text-slate-500). Code snippets, stage numbers, and rule IDs rendered in JetBrains Mono font.
- **Accents & Animations:** Cyan `#22d3ee` glow shadows (`shadow-glow`), subtle pulsing dot indicators (`animate-pulse-glow`), and smooth entry transitions (`animate-fade-in-up`).

---

## 12. Dependencies Audit

### Frontend Dependencies ([`frontend/package.json`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/frontend/package.json))
- `react` (`^18.3.1`) & `react-dom` (`^18.3.1`) — UI view rendering.
- `vite` (`^5.3.1`) — Development server and bundling.
- `typescript` (`^5.5.3`) — Static type checking.
- `tailwindcss` (`^3.4.4`), `postcss` (`^8.4.39`), `autoprefixer` (`^10.4.19`) — Styling framework.

### Backend Dependencies ([`backend/requirements.txt`](file:///c:/Users/SHAURYA/Downloads/sentinel-ai%2022/sentinel-ai/backend/requirements.txt))
- `fastapi` (`==0.115.0` or `0.141.1`) — Web framework.
- `uvicorn[standard]` (`==0.30.6` or `0.52.4`) — ASGI server.
- `pydantic` (`==2.9.2` or `2.13.5`) — Data validation and serialization.
- `python-multipart` (`==0.0.9` or `0.0.32`) — Form data and file upload parsing.

---

## 13. Running the Project

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ & npm 10+

### Step 1: Start Backend Server
```bash
cd backend
.venv\Scripts\activate              # On Windows
.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```
- **Backend URL:** `http://127.0.0.1:8001`
- **Swagger API Docs:** `http://127.0.0.1:8001/docs`

### Step 2: Start Frontend Development Server
```bash
cd frontend
npm run dev
```
- **Frontend URL:** `http://localhost:5173`

---

## 14. Testing Status

- **Automated Test Files:** **0 test files present.** There are no `tests/` directories, `pytest` files, or `jest` spec files in the repository.
- **Manual Verification Status:** Endpoint `/api/health`, `/api/demo/run`, and `/api/project/analyze` have been manually verified operational.

---

## 15. Technical Architecture Diagram

```
                             ┌──────────────────────────────────┐
                             │       User Browser (React)       │
                             │      http://localhost:5173       │
                             └────────────────┬─────────────────┘
                                              │ HTTP Requests
                                              ▼
                             ┌──────────────────────────────────┐
                             │       FastAPI Backend API        │
                             │     http://127.0.0.1:8001        │
                             └────────────────┬─────────────────┘
                                              │
                                              ▼
                             ┌──────────────────────────────────┐
                             │    project_loader.py (Zip Temp)  │
                             └────────────────┬─────────────────┘
                                              │
                                              ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                              pipeline.py (Pipeline Orchestration)                      │
 └──────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────┘
        │              │              │              │              │              │
        ▼              ▼              ▼              ▼              ▼              ▼
  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ Stage 1  │   │ Stage 2  │   │ Stage 3  │   │ Stage 4  │   │ Stage 5  │   │ Stage 6  │
  │ DETECT   │──▶│ EVIDENCE │──▶│ REASON   │──▶│REMEDIATE │──▶│ VERIFY   │──▶│REGRESSION│
  │scanner.py│   │evidence.py   │reasoning.py  │remediation   │verifier.py   │regression│
  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

---

## 16. Complete Feature Matrix

| Feature | Implemented | Partially Implemented | Demo Only | Not Implemented | Notes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **ZIP Project Upload** | ✅ | | | | Validated & extracted safely in `project_loader.py`. |
| **Python Static Analysis** | ✅ | | | | AST-based rules for 5 vulnerability categories. |
| **Multi-Language Scanning** | | | | ❌ | Only `.py` files are scanned. |
| **Evidence Extraction** | ✅ | | | | Pulls snippets & 2 lines context before/after. |
| **Deterministic Reasoning** | ✅ | | | | Template-based root cause analysis. |
| **LLM / AI Integration** | | | | ❌ | No external LLM calls or model APIs attached. |
| **In-Memory Remediation** | ✅ | | | | Category-specific code replacement templates. |
| **Disk Patching / PRs** | | | | ❌ | Files on disk are never modified. |
| **Static Verification** | ✅ | | | | Re-checks proposed snippets with `ast.parse` & regex. |
| **Dynamic Test Suites** | | | | ❌ | No pytest, unit tests, or code execution performed. |
| **Bundled Demo Scenario** | | | ✅ | | Pre-packaged vulnerable Python files scanned on command. |
| **Authentication & Database** | | | | ❌ | Stateless API; scan results are not saved to DB. |

---

## 17. Critical Issues & Technical Discrepancies

1. **Regression Stage Equivalence:** Stage 6 (`regression.py`) performs the identical static regex check as Stage 5 (`verifier.py`) rather than running a test suite or dynamic check.
2. **AI Branding vs. Template Implementation:** Branding mentions "Cyber Reasoning", but all reasoning is generated via hardcoded string templates.
3. **Vite Proxy Port Mismatch:** `vite.config.ts` was originally set to proxy port `8000`. On Windows, port `8000` frequently encounters socket permission errors (`WinError 10013`), requiring backend execution on port `8001`.
4. **PyYAML Dependency:** `scanner.py` checks for `yaml.load`, but `pyyaml` is omitted from `requirements.txt`. (Note: Since analysis is AST-based, `pyyaml` is not required to run scans).
5. **No Test Coverage:** The repository lacks automated unit or integration test files.

---

## 18. Final Project State Summary

- **CURRENT PROJECT:** SENTINEL-AI (Cybersecurity Static Analysis Prototype)
- **CURRENT INPUT:** ZIP archives containing Python source files (`.py`) or bundled demo scenario
- **SUPPORTED LANGUAGES:** Python (`.py`) only
- **CURRENT ANALYSIS:** Real AST-based static analysis matching 5 vulnerability patterns (`SENTINEL-CMD-001`, `SENTINEL-DESER-001`, `SENTINEL-SECRET-001`, `SENTINEL-SQL-001`, `SENTINEL-CRYPTO-001`)
- **CURRENT AI CAPABILITY:** None (Deterministic template-based reasoning; no external LLM connected)
- **CURRENT REMEDIATION:** In-memory proposed code string generation (files on disk are never modified)
- **CURRENT VERIFICATION:** Real static syntax parsing (`ast.parse`) and regex re-checking of proposed code snippets
- **CURRENT USER FLOW:** Landing page -> Scenario Selection -> Animated Pipeline -> Results Dashboard
- **CURRENT UI:** Cyberpunk dark theme (`#05070a` void background, cyan `#22d3ee` accents, Inter & JetBrains Mono typography)
- **CURRENT LIMITATIONS:** Single-language support, no taint/data-flow analysis, no database persistence, no test suite execution
- **STRONGEST WORKING FEATURE:** Honest, evidence-grounded AST static analysis engine paired with a polished 6-stage visualization pipeline
