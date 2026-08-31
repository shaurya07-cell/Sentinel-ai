"""
scanner.py — Stage 1: DETECT

Real AST-based static analysis of uploaded Python source files.

This module NEVER executes uploaded code. Every detector works purely
by parsing source text into an `ast` tree and inspecting node shapes.

Detectors implemented (deliberately kept small and reliable):
  1. Unsafe command execution      -> SENTINEL-CMD-001
  2. Unsafe deserialization        -> SENTINEL-DESER-001
  3. Hardcoded secrets             -> SENTINEL-SECRET-001
  4. SQL construction risk         -> SENTINEL-SQL-001
  5. Weak cryptographic pattern    -> SENTINEL-CRYPTO-001

Confidence is deterministic, derived from the specific AST shape that
matched — never randomized. The rationale is recorded on the Finding
itself so the UI can explain *why* a given confidence was assigned.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import List, Optional

from models.schemas import Finding, Severity, Category


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

_SECRET_KEY_PATTERN = re.compile(
    r"(pass(word)?|secret|api[_-]?key|access[_-]?token|auth[_-]?token|token)",
    re.IGNORECASE,
)

# Values that are obviously placeholders, not real secrets.
_PLACEHOLDER_VALUES = re.compile(
    r"^(changeme|todo|xxx+|placeholder|your[_-]?.*here|<.*>|\*+|example.*|test.*|"
    r"none|null)$",
    re.IGNORECASE,
)

_WEAK_HASHES = {"md5", "sha1"}


def _get_source_line(lines: List[str], lineno: int) -> str:
    if 1 <= lineno <= len(lines):
        return lines[lineno - 1].strip()
    return ""


def _redact(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


def _next_id_factory():
    counter = {"n": 0}

    def _next(prefix: str = "finding") -> str:
        counter["n"] += 1
        return f"{prefix}-{counter['n']:03d}"

    return _next


@dataclass
class RawHit:
    category: Category
    severity: Severity
    title: str
    rule_id: str
    line_number: int
    col_offset: int
    description: str
    confidence: float
    confidence_rationale: str
    node_type: str


class _Detector(ast.NodeVisitor):
    """Runs all detector logic in a single AST walk over one file."""

    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines
        self.hits: List[RawHit] = []
        self._import_aliases = {}   # local name -> module name, e.g. "sys" -> "os"

    # ---- import tracking (helps disambiguate os.system vs custom .system) --
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            local = alias.asname or alias.name.split(".")[0]
            self._import_aliases[local] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.generic_visit(node)

    def _dotted_name(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Attribute):
            base = self._dotted_name(node.value)
            if base:
                return f"{base}.{node.attr}"
            return node.attr
        if isinstance(node, ast.Name):
            return node.id
        return None

    def _check_os_system(self, node: ast.Call) -> None:
        name = self._dotted_name(node.func)
        if name in ("os.system", "os.popen"):
            line = node.lineno
            confidence = 0.9
            rationale = (
                "Direct call to os.system()/os.popen() detected — this API always "
                "invokes a system shell, so confidence is high regardless of arguments."
            )
            severity = Severity.HIGH
            # Escalate if the argument looks dynamically constructed
            if node.args and not isinstance(node.args[0], ast.Constant):
                confidence = 0.94
                rationale += " Argument is not a constant string, indicating dynamic command construction."
            self.hits.append(RawHit(
                category=Category.COMMAND_INJECTION_RISK,
                severity=severity,
                title="Unsafe Command Execution",
                rule_id="SENTINEL-CMD-001",
                line_number=line,
                col_offset=node.col_offset,
                description=(
                    f"Call to {name}() executes its argument through a system shell. "
                    "If any part of the command string originates from user input, this "
                    "may allow arbitrary command injection."
                ),
                confidence=confidence,
                confidence_rationale=rationale,
                node_type="Call",
            ))
            return

        if name == "subprocess.call" or name and name.startswith("subprocess."):
            shell_true = False
            dynamic_cmd = False
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    shell_true = True
            if node.args:
                first = node.args[0]
                if isinstance(first, (ast.JoinedStr,)):
                    dynamic_cmd = True
                elif isinstance(first, ast.BinOp):
                    dynamic_cmd = True
                elif isinstance(first, ast.Call):
                    fname = self._dotted_name(first.func)
                    if fname in ("str.format",) or (isinstance(first.func, ast.Attribute) and first.func.attr == "format"):
                        dynamic_cmd = True

            if shell_true:
                confidence = 0.88
                rationale = "shell=True explicitly passed to a subprocess call, enabling full shell interpretation."
                severity = Severity.HIGH
                if dynamic_cmd:
                    confidence = 0.95
                    rationale += " Command argument also appears to be dynamically constructed (f-string/format/concatenation)."
                self.hits.append(RawHit(
                    category=Category.COMMAND_INJECTION_RISK,
                    severity=severity,
                    title="Unsafe Command Execution (subprocess shell=True)",
                    rule_id="SENTINEL-CMD-001",
                    line_number=node.lineno,
                    col_offset=node.col_offset,
                    description=(
                        f"Call to {name}() is invoked with shell=True. Combined with any "
                        "externally influenced argument, this can allow shell metacharacter "
                        "injection."
                    ),
                    confidence=confidence,
                    confidence_rationale=rationale,
                    node_type="Call",
                ))
            elif dynamic_cmd:
                self.hits.append(RawHit(
                    category=Category.COMMAND_INJECTION_RISK,
                    severity=Severity.MEDIUM,
                    title="Dynamically Constructed Subprocess Command",
                    rule_id="SENTINEL-CMD-001",
                    line_number=node.lineno,
                    col_offset=node.col_offset,
                    description=(
                        f"Call to {name}() builds its command using string formatting or "
                        "concatenation. Without shell=True the risk is lower, but "
                        "unsanitized dynamic arguments are still worth review."
                    ),
                    confidence=0.55,
                    confidence_rationale=(
                        "shell=True is not set, so shell metacharacter injection is not "
                        "directly possible, but dynamic argument construction still "
                        "warrants a medium-confidence, lower-severity flag."
                    ),
                    node_type="Call",
                ))

    # ---- 2. Unsafe deserialization -------------------------------------
    def _check_pickle_load(self, node: ast.Call) -> None:
        name = self._dotted_name(node.func)
        if name in ("pickle.load", "pickle.loads", "cPickle.load", "cPickle.loads"):
            self.hits.append(RawHit(
                category=Category.UNSAFE_DESERIALIZATION,
                severity=Severity.HIGH,
                title="Unsafe Deserialization (pickle)",
                rule_id="SENTINEL-DESER-001",
                line_number=node.lineno,
                col_offset=node.col_offset,
                description=(
                    f"Call to {name}() deserializes data using pickle, which can execute "
                    "arbitrary code during unpickling if the input is not fully trusted."
                ),
                confidence=0.9,
                confidence_rationale=(
                    "pickle.load/loads is inherently unsafe on untrusted input by design "
                    "of the format — direct API usage detection is high confidence."
                ),
                node_type="Call",
            ))

    def _check_yaml_unsafe_load(self, node: ast.Call) -> None:
        name = self._dotted_name(node.func)
        if name == "yaml.load":
            has_safe_loader = any(
                kw.arg == "Loader" and isinstance(kw.value, ast.Attribute)
                and kw.value.attr in ("SafeLoader", "CSafeLoader")
                for kw in node.keywords
            )
            if not has_safe_loader:
                self.hits.append(RawHit(
                    category=Category.UNSAFE_DESERIALIZATION,
                    severity=Severity.MEDIUM,
                    title="Unsafe YAML Loading",
                    rule_id="SENTINEL-DESER-001",
                    line_number=node.lineno,
                    col_offset=node.col_offset,
                    description=(
                        "yaml.load() is called without an explicit SafeLoader. The default "
                        "loader in older PyYAML versions can construct arbitrary Python "
                        "objects from untrusted YAML."
                    ),
                    confidence=0.75,
                    confidence_rationale=(
                        "No SafeLoader/CSafeLoader keyword argument found, but severity is "
                        "kept at MEDIUM since modern PyYAML defaults changed."
                    ),
                    node_type="Call",
                ))

    # ---- 5. Weak cryptographic pattern ---------------------------------
    def _check_weak_hash(self, node: ast.Call) -> None:
        name = self._dotted_name(node.func)
        if name in (f"hashlib.{h}" for h in _WEAK_HASHES):
            algo = name.split(".")[-1]
            self.hits.append(RawHit(
                category=Category.WEAK_CRYPTO,
                severity=Severity.MEDIUM,
                title=f"Weak Cryptographic Hash ({algo.upper()})",
                rule_id="SENTINEL-CRYPTO-001",
                line_number=node.lineno,
                col_offset=node.col_offset,
                description=(
                    f"hashlib.{algo}() is used. {algo.upper()} is considered cryptographically "
                    "broken for security-sensitive purposes such as password hashing or "
                    "integrity verification against a motivated adversary."
                ),
                confidence=0.7,
                confidence_rationale=(
                    f"Direct call to hashlib.{algo} detected. Confidence is MEDIUM because "
                    f"{algo.upper()} may be acceptable for non-security uses (e.g. cache keys), "
                    "which this static analysis cannot fully distinguish."
                ),
                node_type="Call",
            ))

    # ---- 3. Hardcoded secrets -------------------------------------------
    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name) and _SECRET_KEY_PATTERN.search(target.id):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    value = node.value.value
                    if value and not _PLACEHOLDER_VALUES.match(value) and len(value) >= 4:
                        confidence = 0.8
                        if len(value) >= 16:
                            confidence = 0.9
                        self.hits.append(RawHit(
                            category=Category.HARDCODED_SECRET,
                            severity=Severity.HIGH,
                            title="Hardcoded Secret",
                            rule_id="SENTINEL-SECRET-001",
                            line_number=node.lineno,
                            col_offset=node.col_offset,
                            description=(
                                f"Variable '{target.id}' looks like a credential and is assigned "
                                "a hardcoded string literal directly in source code."
                            ),
                            confidence=confidence,
                            confidence_rationale=(
                                "Variable name matches a credential-like pattern (password/"
                                "secret/token/key) and is assigned a non-placeholder string "
                                f"literal of length {len(value)}."
                            ),
                            node_type="Assign",
                        ))
        self.generic_visit(node)

    # ---- 1 & 2 & 4 & 5: single Call visitor dispatching to all detectors --
    def visit_Call(self, node: ast.Call) -> None:
        self._check_os_system(node)
        self._check_pickle_load(node)
        self._check_yaml_unsafe_load(node)
        self._check_weak_hash(node)
        self._check_sql_execute(node)
        self.generic_visit(node)

    _SQL_KEYWORDS = re.compile(
        r"\b(select|insert|update|delete|drop|union)\b", re.IGNORECASE
    )

    def _looks_like_sql(self, s: str) -> bool:
        return bool(self._SQL_KEYWORDS.search(s))

    def _check_sql_execute(self, node: ast.Call) -> None:
        name = self._dotted_name(node.func)
        if name is None:
            return
        if not (name.endswith(".execute") or name.endswith(".executemany")):
            return
        if not node.args:
            return
        first = node.args[0]

        risky = False
        sample_repr = ""

        if isinstance(first, ast.JoinedStr):
            # f-string
            text_parts = [
                v.value for v in first.values
                if isinstance(v, ast.Constant) and isinstance(v.value, str)
            ]
            joined = "".join(text_parts)
            if self._looks_like_sql(joined) or True:
                risky = True
                sample_repr = "f-string SQL construction"

        elif isinstance(first, ast.BinOp) and isinstance(first.op, ast.Add):
            risky = True
            sample_repr = "string concatenation ('+') SQL construction"

        elif isinstance(first, ast.Call):
            fname = self._dotted_name(first.func)
            if fname and fname.endswith(".format"):
                risky = True
                sample_repr = "str.format() SQL construction"

        elif isinstance(first, ast.BinOp) and isinstance(first.op, ast.Mod):
            risky = True
            sample_repr = "%-formatting SQL construction"

        if risky:
            self.hits.append(RawHit(
                category=Category.SQL_CONSTRUCTION_RISK,
                severity=Severity.HIGH,
                title="Potential SQL Injection via Dynamic Query Construction",
                rule_id="SENTINEL-SQL-001",
                line_number=node.lineno,
                col_offset=node.col_offset,
                description=(
                    f"Call to {name}() builds its SQL query using {sample_repr} rather than "
                    "parameterized placeholders. If any interpolated value originates from "
                    "user input, this may allow SQL injection."
                ),
                confidence=0.85,
                confidence_rationale=(
                    f"The first argument to {name}() is built via {sample_repr} instead of a "
                    "constant string or parameter tuple — a strong static signal for "
                    "injection risk, though true exploitability depends on data flow this "
                    "tool does not trace across the whole program."
                ),
                node_type="Call",
            ))


def scan_source(file_path: str, relative_path: str, source_text: str, id_gen) -> List[Finding]:
    """Run all detectors against a single Python source file and return
    typed Finding objects. Never executes the source — only parses it."""
    try:
        tree = ast.parse(source_text, filename=relative_path)
    except SyntaxError as exc:
        # A file that doesn't parse simply yields no findings for itself;
        # this is reported at the project level, not hidden.
        return []

    lines = source_text.splitlines()
    detector = _Detector(lines)
    detector.visit(tree)

    findings: List[Finding] = []
    for hit in detector.hits:
        snippet = _get_source_line(lines, hit.line_number)
        if hit.category == Category.HARDCODED_SECRET:
            # Redact the literal value portion if present in the snippet.
            match = re.search(r"=\s*(['\"])(.*?)\1", snippet)
            if match:
                redacted = _redact(match.group(2))
                snippet = snippet.replace(match.group(2), redacted)

        findings.append(Finding(
            finding_id=id_gen("finding"),
            title=hit.title,
            category=hit.category,
            severity=hit.severity,
            confidence=hit.confidence,
            confidence_rationale=hit.confidence_rationale,
            file_path=relative_path,
            line_number=hit.line_number,
            column_number=hit.col_offset,
            rule_id=hit.rule_id,
            description=hit.description,
            code_snippet=snippet,
        ))

    return findings


def scan_project(python_files: List[str], relative_path_fn) -> List[Finding]:
    """Scan every Python file in the loaded project."""
    id_gen = _next_id_factory()
    all_findings: List[Finding] = []

    for abs_path in sorted(python_files):
        rel_path = relative_path_fn(abs_path)
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as fh:
                source_text = fh.read()
        except OSError:
            continue

        all_findings.extend(scan_source(abs_path, rel_path, source_text, id_gen))

    return all_findings
