"""
Risk Analyst Agent (ARCHITECTURE.md §2): cross-references clauses against
retrieved legal context and flags risk, batched across all clauses in one
task (CLAUDE.md non-negotiable #1) rather than looped per clause.
"""
from crewai import Agent

from backend.agents.llm import get_llm
from backend.agents.schemas import RISK_LEVELS


def build_agent() -> Agent:
    return Agent(
        role="Legal Risk Analyst",
        goal=(
            "Given contract clauses and their relevant Indian legal context, classify each "
            f"clause's risk_level as one of: {', '.join(RISK_LEVELS)}, with clear reasoning "
            "grounded in the retrieved law where available. 'risky' means the clause is "
            "unusually unfavorable or potentially unenforceable; 'ambiguous' means unclear "
            "wording that could be interpreted against the signer; 'safe' means standard and "
            "unremarkable. Be conservative — don't inflate risk to seem thorough."
        ),
        backstory=(
            "A cautious legal risk analyst who has seen how vague or one-sided clauses in "
            "rental and employment contracts hurt ordinary people who didn't have a lawyer "
            "review the fine print."
        ),
        llm=get_llm(),
        verbose=False,
    )
