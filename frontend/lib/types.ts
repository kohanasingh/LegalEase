// Mirrors backend/agents/schemas.py and the API responses in
// backend/api/document_routes.py + chat_routes.py.

export type RiskLevel = "safe" | "ambiguous" | "risky";

export interface FlaggedClause {
  clause_id: string;
  text: string;
  clause_type: string;
  risk_level: RiskLevel;
  reasoning: string;
}

export interface AnalysisResult {
  summary: string;
  flagged_clauses: FlaggedClause[];
  disclaimer: string;
  consult_professional_notes: string[];
  out_of_scope_notes: string[];
}

export type DocumentStatus =
  | "uploaded"
  | "parsing"
  | "chunking"
  | "embedding"
  | "analyzing"
  | "complete"
  | "failed";

export interface DocumentStatusResponse {
  status: DocumentStatus;
  chunk_count?: number;
  error?: string;
}

export interface UploadResponse {
  doc_id: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatAnswer {
  answer: string;
  disclaimer: string;
  consult_professional_notes: string[];
  out_of_scope_notes: string[];
}
