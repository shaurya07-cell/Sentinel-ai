import React from "react";

interface Props {
  onSelectDemo: () => void;
  onSelectUpload: () => void;
  error?: string | null;
}

export default function LandingPage({ onSelectDemo, onSelectUpload, error }: Props) {
  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="min-h-screen bg-void bg-grid text-slate-200 selection:bg-accent/30 selection:text-white">
      {/* ---------------- NAVIGATION HEADER ---------------- */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-void/80 border-b border-panelBorder/80 px-6 py-3.5">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-accent/10 border border-accent/30 flex items-center justify-center text-accent font-black text-lg shadow-glow">
              🛡️
            </div>
            <div>
              <span className="font-extrabold text-white tracking-tight text-lg">
                SENTINEL<span className="text-accent">-AI</span>
              </span>
              <span className="hidden sm:inline-block ml-2.5 px-2 py-0.5 rounded text-[10px] font-mono tracking-wider bg-panel border border-panelBorder text-slate-400">
                CYBER REASONING MVP
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-xs font-medium text-slate-400">
            <button onClick={() => scrollToSection("workflow")} className="hover:text-accent transition-colors">
              Workflow
            </button>
            <button onClick={() => scrollToSection("how-it-works")} className="hover:text-accent transition-colors">
              How It Works
            </button>
            <button onClick={() => scrollToSection("capabilities")} className="hover:text-accent transition-colors">
              Capabilities
            </button>
            <button onClick={() => scrollToSection("why-sentinel")} className="hover:text-accent transition-colors">
              Why SENTINEL
            </button>
            <button onClick={() => scrollToSection("scope")} className="hover:text-accent transition-colors">
              Scope
            </button>
            <button onClick={() => scrollToSection("trust-safety")} className="hover:text-accent transition-colors">
              Trust &amp; Safety
            </button>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={onSelectDemo}
              className="px-3.5 py-1.5 rounded-lg bg-panel border border-panelBorder text-slate-300 hover:border-slate-500 hover:text-white text-xs font-medium transition-colors hidden sm:block"
            >
              Run Demo
            </button>
            <button
              onClick={onSelectUpload}
              className="px-4 py-1.5 rounded-lg bg-accent text-void hover:bg-cyan-300 text-xs font-semibold transition-colors shadow-glow"
            >
              Start Analysis
            </button>
          </div>
        </div>
      </header>

      {/* ---------------- SECTION 1: HERO ---------------- */}
      <section className="relative pt-16 pb-20 px-6 overflow-hidden border-b border-panelBorder/40">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_25%,rgba(34,211,238,0.12),transparent_60%)]" />

        <div className="relative z-10 max-w-4xl mx-auto text-center animate-fade-in-up">
          <div className="inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-xs font-mono text-accent mb-8">
            <span className="h-1.5 w-1.5 rounded-full bg-accent animate-pulse-glow" />
            STATIC ANALYSIS ONLY — UPLOADED CODE IS NEVER EXECUTED
          </div>

          {error && (
            <div className="mb-6 max-w-lg mx-auto rounded-lg border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-rose-300">
              ⚠️ {error}
            </div>
          )}

          <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight text-white leading-tight">
            SENTINEL<span className="text-accent">-AI</span>
          </h1>

          <p className="mt-3 text-xl sm:text-2xl font-bold text-slate-300 tracking-wide">
            Autonomous Cyber Reasoning &amp; Verified Defense
          </p>

          <p className="mt-6 max-w-2xl mx-auto text-base sm:text-lg text-slate-400 leading-relaxed">
            Analyze real source code, identify security weaknesses, generate AI-assisted remediation, and validate the proposed defense.
          </p>

          {/* Primary & Secondary CTAs */}
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={onSelectUpload}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-accent text-void font-bold text-sm hover:bg-cyan-300 transition-all shadow-glow flex items-center justify-center gap-2 group"
            >
              <span>START ANALYSIS</span>
              <span className="group-hover:translate-x-0.5 transition-transform">→</span>
            </button>
            <button
              onClick={onSelectDemo}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-panel border border-panelBorder hover:border-accent/60 text-slate-200 font-semibold text-sm transition-all shadow-sm flex items-center justify-center gap-2"
            >
              <span className="text-accent">▶</span>
              <span>RUN CONTROLLED DEMO</span>
            </button>
          </div>

          <div className="mt-8 text-xs font-mono text-slate-500 flex items-center justify-center gap-6 flex-wrap">
            <span className="flex items-center gap-1.5">
              <span className="text-emerald-400">✓</span> Python AST Detection
            </span>
            <span className="flex items-center gap-1.5">
              <span className="text-emerald-400">✓</span> Gemini 2.5/3.6 AI Reasoning
            </span>
            <span className="flex items-center gap-1.5">
              <span className="text-emerald-400">✓</span> In-Memory Verification
            </span>
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 2: CORE WORKFLOW ---------------- */}
      <section id="workflow" className="py-16 px-6 border-b border-panelBorder/40 bg-panel/20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-xs font-mono text-accent tracking-widest uppercase mb-1">AUTOMATED PIPELINE</p>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Six-Stage Cyber Reasoning Workflow</h2>
            <p className="text-sm text-slate-400 mt-2">Every code finding progresses through six deterministic, verifiable stages.</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {[
              { num: "01", title: "DETECT", desc: "AST pattern matching across source files", color: "border-cyan-500/30 text-cyan-400" },
              { num: "02", title: "EVIDENCE", desc: "Line snippet & context extraction", color: "border-sky-500/30 text-sky-400" },
              { num: "03", title: "REASON", desc: "Gemini AI root-cause & impact analysis", color: "border-indigo-500/30 text-indigo-400" },
              { num: "04", title: "REMEDIATE", desc: "Contextual patch & fix generation", color: "border-amber-500/30 text-amber-400" },
              { num: "05", title: "VERIFY", desc: "In-memory AST re-parse verification", color: "border-emerald-500/30 text-emerald-400" },
              { num: "06", title: "REGRESSION", desc: "Targeted static re-inspection check", color: "border-teal-500/30 text-teal-400" },
            ].map((stage, idx) => (
              <div
                key={stage.title}
                className="relative rounded-xl border border-panelBorder bg-panel/70 p-4 flex flex-col justify-between hover:border-slate-600 transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-mono text-slate-500 font-bold">{stage.num}</span>
                    <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border bg-void/50 ${stage.color}`}>
                      STAGE {idx + 1}
                    </span>
                  </div>
                  <h3 className="font-bold text-sm text-white mb-1 tracking-wide">{stage.title}</h3>
                  <p className="text-[11px] text-slate-400 leading-snug">{stage.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 3: HOW IT WORKS ---------------- */}
      <section id="how-it-works" className="py-20 px-6 border-b border-panelBorder/40">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-xs font-mono text-accent tracking-widest uppercase mb-1">SIMPLE &amp; VERIFIABLE</p>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">How SENTINEL-AI Works</h2>
            <p className="text-sm text-slate-400 mt-2 max-w-xl mx-auto">
              From source code submission to verified security defense in four clear steps.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                step: "01",
                title: "Upload",
                desc: "Upload an authorized Python project as a ZIP archive.",
                icon: "📦",
              },
              {
                step: "02",
                title: "Analyze",
                desc: "AST-based static analysis scans the real source files and generates evidence-backed findings.",
                icon: "🔍",
              },
              {
                step: "03",
                title: "Reason",
                desc: "Gemini AI analyzes the actual finding context and produces root-cause analysis and remediation guidance.",
                icon: "🧠",
              },
              {
                step: "04",
                title: "Validate",
                desc: "SENTINEL statically validates the proposed fix and runs targeted security regression checks.",
                icon: "🛡️",
              },
            ].map((item) => (
              <div
                key={item.step}
                className="rounded-2xl border border-panelBorder bg-panel/50 p-6 relative flex flex-col justify-between hover:border-accent/40 transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-2xl">{item.icon}</span>
                    <span className="text-2xl font-black font-mono text-slate-700">{item.step}</span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 4: CORE CAPABILITIES ---------------- */}
      <section id="capabilities" className="py-20 px-6 border-b border-panelBorder/40 bg-panel/20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-xs font-mono text-accent tracking-widest uppercase mb-1">TECHNICAL EXCELLENCE</p>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Core Platform Capabilities</h2>
            <p className="text-sm text-slate-400 mt-2 max-w-xl mx-auto">
              Built specifically for evidence-grounded source code analysis and closed-loop defense.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: "Real Source-Code Security Analysis",
                desc: "AST-driven pattern matching across unsafe command execution, deserialization, hardcoded secrets, SQL injection, and weak cryptography.",
                icon: "🔬",
              },
              {
                title: "Evidence-Backed Findings",
                desc: "Extracts exact line snippets, surrounding code context lines, AST node classification, and rule attribution directly from source text.",
                icon: "📋",
              },
              {
                title: "Gemini AI Cyber Reasoning",
                desc: "Context-aware root-cause analysis, security impact assessment, and attack surface exposure evaluation powered by Google Gemini AI.",
                icon: "⚡",
              },
              {
                title: "Context-Aware Remediation",
                desc: "Generates minimal, category-specific proposed code fixes grounded strictly in the detected source code.",
                icon: "🔧",
              },
              {
                title: "Static Verification",
                desc: "Statically parses and verifies proposed snippets in-memory to confirm syntax correctness and rule elimination before presentation.",
                icon: "✅",
              },
              {
                title: "Security Regression Checks",
                desc: "Targeted re-inspection ensuring proposed remedies do not re-trigger the original security detector.",
                icon: "🔄",
              },
            ].map((cap) => (
              <div
                key={cap.title}
                className="rounded-xl border border-panelBorder bg-panel/60 p-6 hover:border-slate-600 transition-colors"
              >
                <div className="text-2xl mb-3">{cap.icon}</div>
                <h3 className="text-base font-bold text-white mb-2">{cap.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{cap.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 5: WHY SENTINEL-AI ---------------- */}
      <section id="why-sentinel" className="py-20 px-6 border-b border-panelBorder/40">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-xs font-mono text-accent tracking-widest uppercase mb-1">BEYOND DETECTION</p>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Why SENTINEL-AI?</h2>
          </div>

          <div className="rounded-2xl border border-accent/20 bg-gradient-to-b from-panel to-void p-8 sm:p-10 text-center shadow-glow">
            <blockquote className="text-lg sm:text-xl font-medium text-slate-200 max-w-3xl mx-auto leading-relaxed">
              &ldquo;Traditional security tools often stop at detection. SENTINEL-AI continues from evidence to reasoning, remediation, and validation.&rdquo;
            </blockquote>

            <div className="mt-10 grid md:grid-cols-2 gap-6 text-left max-w-3xl mx-auto">
              <div className="rounded-xl border border-panelBorder bg-panel/80 p-5">
                <p className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-2">Traditional Security Tools</p>
                <div className="flex items-center gap-2 text-sm font-mono text-rose-300 font-semibold mb-3">
                  <span>Detect</span>
                  <span>→</span>
                  <span>Alert</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Flags potential issues but leaves manual root-cause investigation, remediation coding, and verification entirely to developers.
                </p>
              </div>

              <div className="rounded-xl border border-accent/40 bg-accent/5 p-5">
                <p className="text-xs font-mono font-bold text-accent uppercase tracking-wider mb-2">SENTINEL-AI Platform</p>
                <div className="flex items-center gap-2 text-xs sm:text-sm font-mono text-emerald-400 font-semibold mb-3 flex-wrap">
                  <span>Detect</span>
                  <span>→</span>
                  <span>Evidence</span>
                  <span>→</span>
                  <span>Reason</span>
                  <span>→</span>
                  <span>Remediate</span>
                  <span>→</span>
                  <span>Verify</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Closed-loop autonomous cyber reasoning that collects evidence, explains root causes with Gemini AI, generates patches, and statically verifies the fix.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 6: SUPPORTED ANALYSIS SCOPE ---------------- */}
      <section id="scope" className="py-20 px-6 border-b border-panelBorder/40 bg-panel/20">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-xs font-mono text-accent tracking-widest uppercase mb-1">BOUNDARIES &amp; CAPABILITIES</p>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Supported Analysis Scope</h2>
            <p className="text-sm text-slate-400 mt-2">Transparent boundaries for the current MVP release.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 items-start">
            {/* MVP Scope Card */}
            <div className="rounded-2xl border border-panelBorder bg-panel/60 p-6 sm:p-8">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <span className="text-accent">🎯</span> Current MVP Scope
              </h3>
              <ul className="space-y-3 text-xs sm:text-sm text-slate-300">
                <li className="flex items-start gap-2.5">
                  <span className="text-accent font-bold mt-0.5">•</span>
                  <span><strong>Python Source Projects:</strong> Inspects authorized Python source files (`.py`).</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-accent font-bold mt-0.5">•</span>
                  <span><strong>ZIP Upload Archive:</strong> Accepts standard `.zip` archive packages for static extraction.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-accent font-bold mt-0.5">•</span>
                  <span><strong>Static Source-Code Analysis:</strong> AST-based pattern detection for command execution, deserialization, secrets, SQL queries, and weak hashes.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="text-accent font-bold mt-0.5">•</span>
                  <span><strong>Authorized Code Only:</strong> Designed strictly for inspectable source code repositories you own or are authorized to audit.</span>
                </li>
              </ul>
            </div>

            {/* Safety & Out-of-Scope Card */}
            <div className="rounded-2xl border border-panelBorder bg-panel/60 p-6 sm:p-8 space-y-6">
              <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4">
                <p className="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wide mb-1">SAFETY PROMISE</p>
                <p className="text-sm font-semibold text-white">
                  &ldquo;Uploaded source code is never executed.&rdquo;
                </p>
              </div>

              <div>
                <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 mb-2">Scope Disclaimers</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  SENTINEL-AI performs static source-code inspection on authorized uploads. It does not perform active network penetration testing, device scanning, binary execution, or arbitrary website scanning.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 7: TRUST & SAFETY ---------------- */}
      <section id="trust-safety" className="py-20 px-6 border-b border-panelBorder/40">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-xs font-mono text-accent tracking-widest uppercase mb-1">SECURITY BOUNDARIES</p>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Trust &amp; Safety Guarantees</h2>
            <p className="text-sm text-slate-400 mt-2">Built with strict security controls and data isolation principles.</p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {[
              {
                title: "Static Analysis Only",
                desc: "Uploaded code is extracted into isolated temporary directories and analyzed statically.",
                icon: "🔒",
              },
              {
                title: "Zero Execution",
                desc: "Uploaded code is NEVER executed at any point during inspection or verification.",
                icon: "🛡️",
              },
              {
                title: "Minimal AI Context",
                desc: "Gemini AI receives only minimal relevant finding snippets—never entire repository dumps.",
                icon: "🤖",
              },
              {
                title: "Backend API Keys",
                desc: "API keys remain strictly backend-only and are never exposed to the frontend client.",
                icon: "🔑",
              },
              {
                title: "Validated Fixes",
                desc: "AI-generated code patches are statically parsed and verified before being marked successful.",
                icon: "✨",
              },
            ].map((trust) => (
              <div
                key={trust.title}
                className="rounded-xl border border-panelBorder bg-panel/50 p-5 text-center flex flex-col items-center hover:border-slate-600 transition-colors"
              >
                <div className="text-2xl mb-3">{trust.icon}</div>
                <h3 className="text-sm font-bold text-white mb-1.5">{trust.title}</h3>
                <p className="text-[11px] text-slate-400 leading-normal">{trust.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------------- SECTION 8: FINAL CTA ---------------- */}
      <section className="py-24 px-6 relative overflow-hidden bg-gradient-to-b from-void via-panel/40 to-void">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(34,211,238,0.15),transparent_65%)]" />

        <div className="relative z-10 max-w-3xl mx-auto text-center">
          <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4">
            READY TO ANALYZE?
          </h2>
          <p className="text-base sm:text-lg text-slate-400 mb-10 max-w-xl mx-auto">
            Scan your authorized Python source code or run the controlled demo scenario.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={onSelectUpload}
              className="px-8 py-4 rounded-xl bg-accent text-void font-bold text-sm hover:bg-cyan-300 transition-all shadow-glow"
            >
              ANALYZE AUTHORIZED CODE
            </button>
            <button
              onClick={onSelectDemo}
              className="px-8 py-4 rounded-xl bg-panel border border-panelBorder hover:border-accent/60 text-slate-200 font-semibold text-sm transition-all"
            >
              RUN CONTROLLED DEMO
            </button>
          </div>
        </div>
      </section>

      {/* ---------------- FOOTER ---------------- */}
      <footer className="border-t border-panelBorder/60 py-8 px-6 bg-void text-center text-xs text-slate-500 font-mono">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-accent font-bold">SENTINEL-AI</span>
            <span>— Autonomous Cyber Reasoning &amp; Verified Defense</span>
          </div>
          <p className="text-[11px] text-slate-600">
            Static analysis prototype for authorized source code only. Uploaded code is never executed.
          </p>
        </div>
      </footer>
    </div>
  );
}
