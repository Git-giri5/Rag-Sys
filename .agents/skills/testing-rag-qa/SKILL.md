---
name: testing-rag-qa
description: How to run and end-to-end test the RAG Q&A app (FastAPI + Chroma + local embeddings + Next.js) locally, including retrieval-quality checks that do not need an LLM key.
---

# Testing the RAG Q&A app locally

## Bring up the stack
```bash
cd backend && setsid nohup .venv/bin/uvicorn app.main:app --port 8000 > /tmp/uvicorn.log 2>&1 < /dev/null &
# first request loads all-MiniLM-L6-v2: allow ~40s before /health responds
cp frontend/.env.example frontend/.env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
cd frontend && npm run dev                     # :3000, must be (re)started AFTER .env.local exists
```
Readiness probe: `curl -s localhost:8000/health` → `{"status":"ok","llm_configured":...,"documents":N}`.

## Gotchas
- **Never use `pkill -f uvicorn` / `pgrep -f "bin/uvicorn"` from the agent shell**: `-f` matches the
  agent's own `bash -c` command line and kills the shell mid-command (silent exit code -1, later
  commands in the chain never run). Kill via a bracketed pattern that cannot self-match, e.g.
  `pgrep -f "bin/uvi[c]orn" | xargs -r kill`, and even then verify with a separate command.
- Start long-running servers with `setsid nohup ... < /dev/null &` so they survive the shell.
- Wipe state for a clean run with `rm -rf backend/data` (Chroma + uploads) before starting uvicorn.
- Chroma logs `Failed to send telemetry event ...` lines — harmless noise; filter with `grep -v -i telemetry`.

## Uploading fixtures through the browser file input
The input has `accept=".pdf,.txt,.md"`. In the GTK file chooser press `ctrl+l` and type the absolute
path (e.g. `/tmp/fx/doc.md`) — this bypasses the filter and works for rejected types like `.png` too.

## Testing without a GROQ_API_KEY
`POST /chat` returns HTTP 503 `GROQ_API_KEY is not configured. Set it in backend/.env.` and the UI
renders it as red text under the composer. Retrieval can still be exercised without any key:
```bash
cd backend && .venv/bin/python -c "
from app.store import query
for s in query('your question', 4): print(s.score, s.filename, s.chunk_index, s.text[:80])
"
```
Make this test discriminative: upload a document whose sections each exceed `chunk_size` (1000 chars)
so the index has ~10 distinct chunks about clearly different topics; then assert the top-1 chunk is
the topically correct one and its score is far above the runner-up. With a tiny 1-2 chunk index the
"correct" chunk wins trivially and proves nothing.
Note the source-chunk `<details>` UI in `frontend/components/Chat.tsx` can only be seen with a real
Groq key, since sources are rendered only on a successful `/chat` response.

## Generating fixtures
`reportlab` is not in requirements; `.venv/bin/pip install reportlab` works and is the easiest way to
produce a multi-page PDF for pypdf extraction tests.

## Devin Secrets Needed
- `GROQ_API_KEY` (optional) — only required to test answer generation and the source-chunk UI.
