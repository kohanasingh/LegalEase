import type { FlaggedClause } from "./types";

// Generic question per clause type, used to suggest something actually
// relevant to the document just analyzed instead of a fixed unrelated
// example. Keyed to match backend/agents/schemas.py's CLAUSE_TYPES.
const CLAUSE_TYPE_QUESTIONS: Record<string, string> = {
  payment: "Is the payment schedule in this document fair to me?",
  termination: "What happens if I want to end this agreement early?",
  liability: "What am I liable for under this agreement?",
  confidentiality: "What information am I required to keep confidential?",
  dispute_resolution: "How would a dispute under this agreement be resolved?",
  renewal: "How does this agreement renew, and can I opt out?",
  obligations: "What are my main obligations under this agreement?",
  other: "Can you explain the riskiest part of this document in more detail?",
};

export function suggestExampleQuestion(clauses: FlaggedClause[]): string | null {
  if (clauses.length === 0) return null;
  const prioritized =
    clauses.find((c) => c.risk_level === "risky") ??
    clauses.find((c) => c.risk_level === "ambiguous") ??
    clauses[0];
  return CLAUSE_TYPE_QUESTIONS[prioritized.clause_type] ?? CLAUSE_TYPE_QUESTIONS.other;
}
