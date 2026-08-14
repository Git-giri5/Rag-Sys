# RAG Q&A

Ask questions about your own documents. Fully free stack:

| Layer | Choice | Cost |
| --- | --- | --- |
| Frontend | Next.js (App Router), deploy on Vercel | free |
| Backend | FastAPI, deploy on Render (Docker) | free tier |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2`, runs locally | free, no API calls |
| Vector DB | Chroma, persisted on disk | free |
| LLM | Groq (`llama-3.3-70b-versatile`) | free tier |

## How it works

1. `POST /documents` — extract text (pdf/txt/md), chunk it on paragraph boundaries with overlap,
   embed each chunk locally, store vectors + metadata in Chroma.
2. `POST /chat` — embed the question, cosine-search the top *k* chunks, build a numbered context
   block, and ask Groq to answer using only that context with `[n]` citations.
3. The UI shows the answer plus expandable source chunks with similarity scores.

## Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # add your free key from https://console.groq.com/keys
uvicorn app.main:app --reload
```

API docs at http://localhost:8000/docs.

| Endpoint | Description |
| --- | --- |
| `GET /health` | status, whether the LLM key is configured, indexed document count |
| `POST /documents` | multipart upload (`file`), returns `document_id` and chunk count |
| `GET /documents` | list indexed documents |
| `DELETE /documents/{id}` | remove a document and its chunks |
| `POST /chat` | `{ "question": "...", "top_k": 4 }` → answer + sources |

Checks: `ruff check . && mypy app && pytest`.

## Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Checks: `npm run lint && npm run typecheck`.

## Deploy

- **Backend → Render**: `render.yaml` is a free-tier Docker web service rooted at `backend/`. Set
  `GROQ_API_KEY` and `CORS_ORIGINS` (your Vercel URL). Note the free tier has an ephemeral disk, so
  the Chroma index resets on redeploy/sleep; attach a disk or move to Qdrant Cloud free tier to
  persist.
- **Frontend → Vercel**: import the repo with root directory `frontend/` and set
  `NEXT_PUBLIC_API_URL` to the Render URL.

## Possible next steps

Supabase auth + per-user collections, streaming responses, hybrid (BM25 + vector) retrieval,
reranking, and evaluation of answer quality on a small labelled question set.
