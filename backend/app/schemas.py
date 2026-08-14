from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int


class Source(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    score: float
    text: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int | None = Field(default=None, ge=1, le=20)
    document_ids: list[str] | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    chunks: int


class HealthResponse(BaseModel):
    status: str
    llm_configured: bool
    embedding_model: str
    documents: int
