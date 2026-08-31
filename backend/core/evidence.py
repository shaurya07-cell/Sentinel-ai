"""
evidence.py — Stage 2: COLLECT EVIDENCE

Builds an Evidence record for each Finding, grounded entirely in the
real source text of the uploaded/demo project. No evidence field is
invented — every value is derived from the file content and the
Finding's own line/column/rule data produced by scanner.py.
"""

from __future__ import annotations

from typing import Dict, List

from models.schemas import Finding, Evidence, Category

_CONTEXT_LINES = 2

# A lightweight re-derivation of "what call/arguments are relevant" per
# category, purely from the code snippet text, for the evidence panel.
_CALL_HINTS = {
    Category.COMMAND_INJECTION_RISK: ["os.system", "os.popen", "subprocess"],
    Category.UNSAFE_DESERIALIZATION: ["pickle.load", "pickle.loads", "yaml.load"],
    Category.HARDCODED_SECRET: ["="],
    Category.SQL_CONSTRUCTION_RISK: [".execute", ".executemany"],
    Category.WEAK_CRYPTO: ["hashlib."],
}

_AST_NODE_TYPE = {
    Category.COMMAND_INJECTION_RISK: "ast.Call",
    Category.UNSAFE_DESERIALIZATION: "ast.Call",
    Category.HARDCODED_SECRET: "ast.Assign",
    Category.SQL_CONSTRUCTION_RISK: "ast.Call",
    Category.WEAK_CRYPTO: "ast.Call",
}


def _extract_relevant_call(snippet: str, category: Category) -> str | None:
    for hint in _CALL_HINTS.get(category, []):
        if hint != "=" and hint in snippet:
            return hint
    return None


def collect_evidence(
    finding: Finding,
    file_source_lines: Dict[str, List[str]],
) -> Evidence:
    lines = file_source_lines.get(finding.file_path, [])

    start = max(0, finding.line_number - 1 - _CONTEXT_LINES)
    end = min(len(lines), finding.line_number - 1 + _CONTEXT_LINES + 1)

    context_before = lines[start: finding.line_number - 1]
    context_after = lines[finding.line_number: end]

    relevant_call = _extract_relevant_call(finding.code_snippet, finding.category)

    summary = (
        f"Rule {finding.rule_id} matched on {finding.file_path}:{finding.line_number}. "
        f"Static AST inspection identified the pattern shown in the code snippet; "
        f"no runtime execution was performed to obtain this evidence."
    )

    return Evidence(
        finding_id=finding.finding_id,
        file_path=finding.file_path,
        line_number=finding.line_number,
        code_snippet=finding.code_snippet,
        context_before=context_before,
        context_after=context_after,
        ast_node_type=_AST_NODE_TYPE.get(finding.category, "ast.AST"),
        triggered_rule=finding.rule_id,
        relevant_call=relevant_call,
        relevant_arguments=[],
        evidence_summary=summary,
    )
