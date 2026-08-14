import Chat from "@/components/Chat";
import DocumentPanel from "@/components/DocumentPanel";

export default function Home() {
  return (
    <main>
      <div className="layout">
        <div>
          <h1>RAG Q&amp;A</h1>
          <p className="subtitle">
            Local embeddings + Chroma retrieval, answers generated with Groq.
          </p>
          <DocumentPanel />
        </div>
        <Chat />
      </div>
    </main>
  );
}
