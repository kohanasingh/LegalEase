import type {
  AnalysisResult,
  ChatAnswer,
  ChatMessage,
  DocumentStatusResponse,
  UploadResponse,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function parseJsonOrThrow<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json();
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });
  return parseJsonOrThrow<UploadResponse>(response);
}

export async function getDocumentStatus(docId: string): Promise<DocumentStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${docId}/status`);
  return parseJsonOrThrow<DocumentStatusResponse>(response);
}

export async function getDocumentAnalysis(docId: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${docId}/analysis`);
  return parseJsonOrThrow<AnalysisResult>(response);
}

export async function sendChatMessage(
  docId: string,
  question: string,
  history: ChatMessage[]
): Promise<ChatAnswer> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${docId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });
  return parseJsonOrThrow<ChatAnswer>(response);
}
