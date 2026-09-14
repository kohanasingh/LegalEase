"""
Document Parser Agent (ARCHITECTURE.md §2): cleans up raw PDF-extracted
text into structured plain text with headers/clauses/numbering intact.
Raw extraction (backend/tools/pdf_parser_tool.py) already happened in the
Stage 3 upload pipeline; this agent's job is LLM cleanup (fixing broken
line wraps, stripping page headers/footers/page numbers), not re-parsing.
"""
from crewai import Agent

from backend.agents.llm import get_llm


def build_agent() -> Agent:
    return Agent(
        role="Legal Document Parser",
        goal=(
            "Clean up raw, messily-extracted PDF text into well-structured plain text, "
            "preserving every clause, heading, and numbering exactly as written — never "
            "summarizing or dropping content, only removing extraction artifacts like "
            "repeated page headers/footers, stray page numbers, and broken line wraps."
        ),
        backstory=(
            "A meticulous paralegal who has spent years turning scanned and badly-formatted "
            "contracts into clean, readable text without ever changing their legal meaning."
        ),
        llm=get_llm(),
        verbose=False,
    )
