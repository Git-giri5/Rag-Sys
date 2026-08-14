import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import llm, store
from app.chunking import chunk_text
from app.config import get_settings
from app.loaders import extract_text
from app.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentInfo,
    HealthResponse,
    IngestResponse,
)

settings = get_settings()

app = FastAPI(title="RAG Q&A API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        llm_configured=bool(settings.groq_api_key),
        embedding_model=settings.embedding_model,
        documents=len(store.list_documents()),
    )


@app.post("/documents", response_model=IngestResponse, status_code=201)
async def ingest(file: UploadFile = File(...)) -> IngestResponse:
    filename = file.filename or "upload"
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    text = extract_text(filename, content)
    chunks = chunk_text(text, settings.chunk_size, settings.chunk_overlap)
    if not chunks:
        raise HTTPException(status_code=400, detail="No extractable text found in the document.")

    document_id = uuid.uuid4().hex
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / f"{document_id}-{Path(filename).name}").write_bytes(content)

    store.add_chunks(document_id, filename, chunks)
    return IngestResponse(document_id=document_id, filename=filename, chunks=len(chunks))


@app.get("/documents", response_model=list[DocumentInfo])
def documents() -> list[DocumentInfo]:
    return store.list_documents()


@app.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str) -> None:
    if not store.delete_document(document_id):
        raise HTTPException(status_code=404, detail=f"Unknown document '{document_id}'.")
    for path in Path(settings.upload_dir).glob(f"{document_id}-*"):
        path.unlink(missing_ok=True)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    sources = store.query(
        request.question,
        request.top_k or settings.top_k,
        request.document_ids,
    )
    if not sources:
        return ChatResponse(
            answer="No documents have been indexed yet. Upload a document first.",
            sources=[],
        )
    return ChatResponse(answer=llm.answer(request.question, sources), sources=sources)
