"""
Chat Crew orchestration (ARCHITECTURE.md §2): QA Agent -> Scope Guardrail.
Runs per follow-up message. Conversation history is sent by the client
each call (ARCHITECTURE.md §1) rather than kept server-side, so the crew
stays stateless between messages.
"""
from crewai import Crew, Process, Task

from backend import config
from backend.agents import qa_agent, scope_guardrail_agent
from backend.agents.schemas import ChatAnswer, GuardrailAnnotation


def _format_history(history: list[dict] | None) -> str:
    if not history:
        return "(no prior messages)"
    return "\n".join(f"{turn['role']}: {turn['content']}" for turn in history)


def run_chat_crew(doc_id: str, question: str, history: list[dict] | None = None) -> ChatAnswer:
    qa = qa_agent.build_agent()
    guardrail = scope_guardrail_agent.build_agent()

    qa_task = Task(
        description=(
            f"The current document's doc_id is '{doc_id}'. Conversation so far:\n"
            f"{_format_history(history)}\n\n"
            f"Answer this follow-up question, grounded in the document and Indian law: {question}"
        ),
        expected_output="A grounded answer noting which parts come from the document vs. Indian law.",
        agent=qa,
    )

    guardrail_task = Task(
        description=(
            "Review the drafted answer below. Attach the required disclaimer, list anything "
            "needing a qualified professional's judgment under consult_professional_notes, and "
            "list anything out of this system's scope under out_of_scope_notes. Pass the answer "
            "through unchanged in substance."
        ),
        expected_output="The final ChatAnswer JSON object.",
        agent=guardrail,
        context=[qa_task],
        output_pydantic=ChatAnswer,
    )

    crew = Crew(
        agents=[qa, guardrail],
        tasks=[qa_task, guardrail_task],
        process=Process.sequential,
        max_rpm=config.AGENT_MAX_RPM,
        verbose=False,
    )

    result = crew.kickoff()
    return result.pydantic
