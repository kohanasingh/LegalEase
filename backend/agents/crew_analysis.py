"""
Analysis Crew orchestration (ARCHITECTURE.md §2): runs once per upload.

Upload -> Parser Agent -> Clause Extractor -> Legal Retriever (batched)
       -> Risk Analyst (batched) -> Summarizer -> Scope Guardrail
       -> stored analysis, keyed by doc_id

Every path through this crew ends at the Scope Guardrail Agent — its
output (GuardrailAnnotation) is the only thing callers should surface.
"""
from crewai import Crew, Process, Task

from backend import config
from backend.agents import (
    clause_extractor_agent,
    document_parser_agent,
    legal_retriever_agent,
    risk_analyst_agent,
    scope_guardrail_agent,
    summarizer_agent,
)
from backend.agents.schemas import (
    AnalysisSummary,
    ClauseExtractionResult,
    GuardrailAnnotation,
    LegalContextResult,
    RiskAnalysisResult,
)


def run_analysis_crew(raw_text: str) -> GuardrailAnnotation:
    parser = document_parser_agent.build_agent()
    extractor = clause_extractor_agent.build_agent()
    retriever = legal_retriever_agent.build_agent()
    analyst = risk_analyst_agent.build_agent()
    summarizer = summarizer_agent.build_agent()
    guardrail = scope_guardrail_agent.build_agent()

    parse_task = Task(
        description=(
            "Clean up the following raw, PDF-extracted document text into well-structured "
            "plain text. Preserve every clause and all numbering exactly; only remove "
            "extraction artifacts (repeated headers/footers, stray page numbers, broken "
            "line wraps).\n\nRAW TEXT:\n{raw_text}"
        ),
        expected_output="The full document as clean, structured plain text.",
        agent=parser,
    )

    extract_task = Task(
        description="Break the structured document into discrete, typed clauses.",
        expected_output="A JSON list of clauses, each with clause_id, text, and clause_type.",
        agent=extractor,
        context=[parse_task],
        output_pydantic=ClauseExtractionResult,
    )

    retrieve_task = Task(
        description=(
            "For every clause produced by the Clause Extractor, use ChromaRetrieverTool "
            "(scope='legal_corpus') to find relevant Indian statutory law. Produce one "
            "legal-context entry per clause_id, even if it's an empty list when nothing "
            "relevant was found."
        ),
        expected_output="A JSON mapping of clause_id to a list of relevant law citations/snippets.",
        agent=retriever,
        context=[extract_task],
        output_pydantic=LegalContextResult,
    )

    risk_task = Task(
        description=(
            "Using the extracted clauses and their retrieved legal context, classify each "
            "clause's risk_level (safe/ambiguous/risky) with clear reasoning."
        ),
        expected_output="A JSON list of clauses annotated with risk_level and reasoning.",
        agent=analyst,
        context=[extract_task, retrieve_task],
        output_pydantic=RiskAnalysisResult,
    )

    # Scale summary length to the document instead of a fixed paragraph count
    # (~500 words/page is a standard estimate for a normally-formatted
    # document), capped so a very long contract doesn't demand a
    # unreasonably long summary.
    word_count = len(raw_text.split())
    estimated_pages = max(1, min(8, round(word_count / 500)))
    paragraph_word = "paragraph" if estimated_pages == 1 else "paragraphs"

    summarize_task = Task(
        description=(
            "Using the full structured document text and the risk-flagged clauses below, "
            "write a concise plain-language explanation for a layperson: what the document is "
            "and who it's between, the most important obligations for each party (with actual "
            "figures/dates/durations from the document where relevant), and the most notable "
            "risks already identified and why they matter. This is a summary, not an exhaustive "
            "restatement — prioritize the most important information and leave out minor detail "
            "if you're short on space.\n\n"
            f"Format requirement: write approximately {estimated_pages} {paragraph_word} total "
            "(roughly one paragraph per page of the original document). "
            + (
                "Put a literal blank line (two newline characters) between each paragraph."
                if estimated_pages > 1
                else "A single paragraph is expected here — don't pad it out."
            )
        ),
        expected_output=(
            f"Approximately {estimated_pages} {paragraph_word}"
            + (", separated by blank lines (two newline characters between each), " if estimated_pages > 1 else " ")
            + "covering the document's purpose, key obligations, and notable risks — concise, not exhaustive."
        ),
        agent=summarizer,
        context=[parse_task, risk_task],
        output_pydantic=AnalysisSummary,
    )

    guardrail_task = Task(
        description=(
            "Review the summary and risk-flagged clauses below. Attach the required "
            "disclaimer, list anything needing a qualified professional's judgment under "
            "consult_professional_notes, and list anything out of this system's scope under "
            "out_of_scope_notes. Pass the summary and flagged_clauses through unchanged in "
            "content — do not remove or soften existing risk flags."
        ),
        expected_output="The final GuardrailAnnotation JSON object.",
        agent=guardrail,
        context=[risk_task, summarize_task],
        output_pydantic=GuardrailAnnotation,
    )

    crew = Crew(
        agents=[parser, extractor, retriever, analyst, summarizer, guardrail],
        tasks=[parse_task, extract_task, retrieve_task, risk_task, summarize_task, guardrail_task],
        process=Process.sequential,
        max_rpm=config.AGENT_MAX_RPM,
        verbose=False,
    )

    result = crew.kickoff(inputs={"raw_text": raw_text})
    return result.pydantic
