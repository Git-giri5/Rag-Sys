"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { deleteDocument, listDocuments, uploadDocument, type DocumentInfo } from "@/lib/api";

export default function DocumentPanel() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const refresh = useCallback(async () => {
    try {
      setDocuments(await listDocuments());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load documents");
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function handleUpload(file: File) {
    setBusy(true);
    setError(null);
    try {
      await uploadDocument(file);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  async function handleDelete(documentId: string) {
    setBusy(true);
    try {
      await deleteDocument(documentId);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <aside className="panel">
      <h2>Documents</h2>
      <input
        ref={fileInput}
        type="file"
        accept=".pdf,.txt,.md"
        disabled={busy}
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void handleUpload(file);
        }}
      />
      {busy && <p className="empty">Working…</p>}
      {error && <p className="error">{error}</p>}
      {documents.length === 0 ? (
        <p className="empty">No documents indexed yet.</p>
      ) : (
        <ul className="doc-list">
          {documents.map((doc) => (
            <li key={doc.document_id} className="doc-item">
              <span>
                {doc.filename} <span className="empty">({doc.chunks} chunks)</span>
              </span>
              <button
                type="button"
                aria-label={`Delete ${doc.filename}`}
                disabled={busy}
                onClick={() => void handleDelete(doc.document_id)}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
