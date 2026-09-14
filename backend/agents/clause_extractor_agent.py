"""Clause Extractor Agent (ARCHITECTURE.md §2): breaks structured text into discrete, typed clauses."""
from crewai import Agent

from backend.agents.llm import get_llm
from backend.agents.schemas import CLAUSE_TYPES


def build_agent() -> Agent:
    return Agent(
        role="Legal Clause Extractor",
        goal=(
            "Break a structured legal document into discrete clauses, each tagged with a "
            f"clause_type from: {', '.join(CLAUSE_TYPES)}. Every clause must be a complete, "
            "self-contained provision — never split a single clause across two entries, and "
            "never merge two distinct clauses into one."
        ),
        backstory=(
            "A contracts specialist who has read thousands of Indian rental agreements, "
            "employment contracts, and loan agreements, and can instantly tell where one "
            "clause ends and the next begins."
        ),
        llm=get_llm(),
        verbose=False,
    )
