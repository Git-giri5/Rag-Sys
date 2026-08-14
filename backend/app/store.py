from functools import lru_cache
from pathlib import Path
from typing import Literal

import chromadb
from chromadb.api.models.Collection import Collection
from chromadb.api.types import IncludeEnum, Where

from app.config import get_settings
from app.embeddings import embed
from app.schemas import DocumentInfo, Source


@lru_cache
def get_collection() -> Collection:
    settings = get_settings()
    Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=settings.chroma_dir)
    return client.get_or_create_collection(
        name=settings.collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(document_id: str, filename: str, chunks: list[str]) -> int:
    if not chunks:
        return 0
    collection = get_collection()
    collection.add(
        ids=[f"{document_id}:{index}" for index in range(len(chunks))],
        documents=chunks,
        embeddings=embed(chunks),
        metadatas=[
            {"document_id": document_id, "filename": filename, "chunk_index": index}
            for index in range(len(chunks))
        ],
    )
    return len(chunks)


def query(question: str, top_k: int, document_ids: list[str] | None = None) -> list[Source]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    where: Where | None = None
    if document_ids:
        wanted: dict[Literal["$in", "$nin"], list[str | int | float | bool]] = {
            "$in": list(document_ids)
        }
        where = {"document_id": wanted}
    result = collection.query(
        query_embeddings=embed([question]),
        n_results=min(top_k, collection.count()),
        where=where,
        include=[IncludeEnum.documents, IncludeEnum.metadatas, IncludeEnum.distances],
    )

    documents = (result.get("documents") or [[]])[0]
    metadatas = (result.get("metadatas") or [[]])[0]
    distances = (result.get("distances") or [[]])[0]

    sources: list[Source] = []
    for text, metadata, distance in zip(documents, metadatas, distances, strict=False):
        sources.append(
            Source(
                document_id=str(metadata.get("document_id", "")),
                filename=str(metadata.get("filename", "")),
                chunk_index=int(metadata.get("chunk_index", 0)),
                score=round(1.0 - float(distance), 4),
                text=text,
            )
        )
    return sources


def list_documents() -> list[DocumentInfo]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    records = collection.get(include=[IncludeEnum.metadatas])
    counts: dict[str, DocumentInfo] = {}
    for metadata in records.get("metadatas") or []:
        document_id = str(metadata.get("document_id", ""))
        info = counts.get(document_id)
        if info is None:
            counts[document_id] = DocumentInfo(
                document_id=document_id,
                filename=str(metadata.get("filename", "")),
                chunks=1,
            )
        else:
            info.chunks += 1
    return sorted(counts.values(), key=lambda doc: doc.filename)


def delete_document(document_id: str) -> None:
    get_collection().delete(where={"document_id": document_id})


def count_chunks() -> int:
    return get_collection().count()
