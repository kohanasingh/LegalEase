"""
Legal Retriever Agent (ARCHITECTURE.md §2): for a *batch* of clauses, looks
up relevant Indian statutory context via ChromaRetrieverTool. This is one
agent invocation processing the whole clause list — not a Python loop
issuing one LLM call per clause (CLAUDE.md non-negotiable #1). The agent
may call the tool multiple times internally per clause; what matters is a
single Task/LLM-call cycle overall.
"""
from crewai import Agent

from backend.agents.llm import get_llm
from backend.tools.chroma_retriever_tool import chroma_retriever_tool


def build_agent() -> Agent:
    return Agent(
        role="Legal Researcher",
        goal=(
            "Given a batch of contract clauses, look up relevant Indian statutory law for "
            "each one using ChromaRetrieverTool (scope='legal_corpus'), and produce a "
            "clause-by-clause mapping to the relevant law found. If nothing relevant is "
            "found for a clause, say so plainly rather than inventing a citation."
        ),
        backstory=(
            "A legal researcher who cross-references every contract clause against Indian "
            "bare acts and regulations before anyone assesses risk, and never cites law that "
            "wasn't actually retrieved from the corpus."
        ),
        tools=[chroma_retriever_tool],
        llm=get_llm(),
        verbose=False,
    )
