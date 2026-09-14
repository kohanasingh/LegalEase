"""Structured I/O contracts passed between Analysis Crew agents (CrewAI's output_pydantic)."""
from pydantic import BaseModel, Field

CLAUSE_TYPES = [
    "payment",
    "termination",
    "liability",
    "confidentiality",
    "dispute_resolution",
    "renewal",
    "obligations",
    "other",
]

RISK_LEVELS = ["safe", "ambiguous", "risky"]


class Clause(BaseModel):
    clause_id: str = Field(description="Stable short id, e.g. 'clause_1'")
    text: str
    clause_type: str = Field(description=f"One of: {', '.join(CLAUSE_TYPES)}")


class ClauseExtractionResult(BaseModel):
    clauses: list[Clause]


class ClauseLegalContext(BaseModel):
    clause_id: str
    relevant_law: list[str] = Field(
        description="Short citations/snippets of Indian law relevant to this clause, e.g. 'Section 73, Indian Contract Act, 1872: ...'"
    )


class LegalContextResult(BaseModel):
    contexts: list[ClauseLegalContext]


class RiskFlaggedClause(BaseModel):
    clause_id: str
    text: str
    clause_type: str
    risk_level: str = Field(description=f"One of: {', '.join(RISK_LEVELS)}")
    reasoning: str


class RiskAnalysisResult(BaseModel):
    flagged_clauses: list[RiskFlaggedClause]


class AnalysisSummary(BaseModel):
    summary: str = Field(description="Plain-language summary of the whole document for a layperson")


class ChatAnswer(BaseModel):
    answer: str = Field(description="Grounded answer, noting which parts come from the user's document vs. Indian law")
    disclaimer: str
    consult_professional_notes: list[str] = Field(default_factory=list)
    out_of_scope_notes: list[str] = Field(default_factory=list)


class GuardrailAnnotation(BaseModel):
    summary: str
    flagged_clauses: list[RiskFlaggedClause]
    disclaimer: str
    consult_professional_notes: list[str] = Field(
        default_factory=list,
        description="Specific points in the analysis that need a qualified professional's judgment",
    )
    out_of_scope_notes: list[str] = Field(
        default_factory=list, description="Anything in the document outside this system's supported scope"
    )
