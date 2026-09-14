"""
Scope Guardrail Agent (ARCHITECTURE.md §2, CLAUDE.md non-negotiable #6):
the safety layer. Every output — Analysis Crew and Chat Crew alike — must
pass through this agent before reaching the user. It attaches the
disclaimer, flags anything needing a qualified professional's judgment,
and calls out anything outside this system's supported scope. This is
enforced by crew_analysis.py/crew_chat.py always including this agent as
the last task, never by convention alone.
"""
from crewai import Agent

from backend.agents.llm import get_llm

DISCLAIMER = (
    "This analysis is informational only and is not a substitute for advice from a "
    "qualified legal professional. Consult a lawyer before acting on it."
)


def build_agent() -> Agent:
    return Agent(
        role="Scope & Disclaimer Guardrail",
        goal=(
            "Review the drafted analysis before it reaches the user. Always attach this "
            f'exact disclaimer: "{DISCLAIMER}" Identify any point that genuinely needs a '
            "qualified legal professional's judgment (e.g. anything jurisdiction-specific, "
            "any clause whose enforceability is genuinely unclear) and list it under "
            "consult_professional_notes. Identify anything in the document or summary that "
            "falls outside Indian contract/rental/consumer law generally, or that speculates "
            "beyond what the retrieved legal context supports, and list it under "
            "out_of_scope_notes. Never remove or water down risk flags already identified — "
            "your job is to add safety framing, not to override the risk analysis."
        ),
        backstory=(
            "A compliance-minded reviewer whose sole job is making sure nothing reaches an "
            "ordinary user without a clear 'this isn't legal advice' framing, and that "
            "anything genuinely uncertain is flagged for a real lawyer rather than answered "
            "speculatively."
        ),
        llm=get_llm(),
        verbose=False,
    )
