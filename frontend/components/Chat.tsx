"use client";

import { useState } from "react";

import { askQuestion, type Source } from "@/lib/api";

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setMessages((current) => [...current, { role: "user", content: trimmed }]);
    setQuestion("");
    setLoading(true);
    setError(null);
    try {
      const response = await askQuestion(trimmed);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.answer, sources: response.sources },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="panel">
      <h2>Ask</h2>
      <div className="messages">
        {messages.length === 0 && (
          <p className="empty">Upload a document, then ask a question about it.</p>
        )}
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.content}
            {message.sources && message.sources.length > 0 && (
              <div className="sources">
                {message.sources.map((source, sourceIndex) => (
                  <details key={`${source.document_id}-${source.chunk_index}`}>
                    <summary>
                      [{sourceIndex + 1}] {source.filename} · chunk {source.chunk_index} · score{" "}
                      {source.score}
                    </summary>
                    <p>{source.text}</p>
                  </details>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <p className="empty">Thinking…</p>}
      </div>
      <form className="composer" onSubmit={handleSubmit}>
        <textarea
          rows={3}
          value={question}
          placeholder="What does the document say about…?"
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          Ask
        </button>
      </form>
      {error && <p className="error">{error}</p>}
    </section>
  );
}
