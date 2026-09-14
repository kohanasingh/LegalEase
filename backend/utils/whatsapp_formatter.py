"""
Converts structured analysis/chat output into readable WhatsApp plain
text (ARCHITECTURE.md §5) — distinct from DocumentSummaryPanel because
WhatsApp only supports simple *bold*/_italic_ markup, no rich UI.
"""
from typing import Any

RISK_EMOJI = {"safe": "🟢", "ambiguous": "🟡", "risky": "🔴"}

DISCLAIMER_PREFIX = "⚖️ *LegalEase is informational only, not legal advice.*"


def format_analysis(analysis: dict[str, Any]) -> str:
    lines = [DISCLAIMER_PREFIX, "", "*Summary*", analysis["summary"], ""]

    if analysis.get("flagged_clauses"):
        lines.append("*Key clauses*")
        for clause in analysis["flagged_clauses"]:
            emoji = RISK_EMOJI.get(clause["risk_level"], "⚪")
            lines.append(f"{emoji} *{clause['clause_type']}*: {clause['reasoning']}")
        lines.append("")

    if analysis.get("consult_professional_notes"):
        lines.append("*Worth confirming with a lawyer*")
        lines.extend(f"- {note}" for note in analysis["consult_professional_notes"])
        lines.append("")

    if analysis.get("out_of_scope_notes"):
        lines.append("*Outside this tool's scope*")
        lines.extend(f"- {note}" for note in analysis["out_of_scope_notes"])
        lines.append("")

    lines.append("Ask me a follow-up question anytime, or send another document to start over.")
    return "\n".join(lines)


def format_chat_answer(answer: dict[str, Any]) -> str:
    lines = [answer["answer"], "", f"_{answer['disclaimer']}_"]

    if answer.get("consult_professional_notes"):
        lines.append("")
        lines.append("*Worth confirming with a lawyer*")
        lines.extend(f"- {note}" for note in answer["consult_professional_notes"])

    if answer.get("out_of_scope_notes"):
        lines.append("")
        lines.append("*Outside this tool's scope*")
        lines.extend(f"- {note}" for note in answer["out_of_scope_notes"])

    return "\n".join(lines)
