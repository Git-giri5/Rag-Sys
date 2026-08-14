export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type DocumentInfo = {
  document_id: string;
  filename: string;
  chunks: number;
};

export type Source = {
  document_id: string;
  filename: string;
  chunk_index: number;
  score: number;
  text: string;
};

export type ChatResponse = {
  answer: string;
  sources: Source[];
};

type ValidationError = { loc?: (string | number)[]; msg?: string };

/** FastAPI returns a string for HTTPException and an array of errors for 422s. */
function formatDetail(detail: unknown): string | null {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return (
      (detail as ValidationError[])
        .map((error) => [error.loc?.join("."), error.msg].filter(Boolean).join(": "))
        .filter(Boolean)
        .join("; ") || null
    );
  }
  return null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(formatDetail(body?.detail) ?? `Request failed with status ${response.status}`);
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export function listDocuments(): Promise<DocumentInfo[]> {
  return request<DocumentInfo[]>("/documents", { cache: "no-store" });
}

export function uploadDocument(file: File): Promise<DocumentInfo> {
  const body = new FormData();
  body.append("file", file);
  return request<DocumentInfo>("/documents", { method: "POST", body });
}

export function deleteDocument(documentId: string): Promise<void> {
  return request<void>(`/documents/${documentId}`, { method: "DELETE" });
}

export function askQuestion(question: string): Promise<ChatResponse> {
  return request<ChatResponse>("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}
