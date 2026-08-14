from functools import lru_cache

from fastapi import HTTPException
from groq import Groq

from app.config import get_settings
from app.schemas import Source

SYSTEM_PROMPT = (
    "You are a precise question-answering assistant. Answer using only the provided context. "
    "Cite the sources you use as [1], [2], ... matching the numbered context blocks. "
    "If the context does not contain the answer, say you don't know."
)


@lru_cache
def get_client() -> Groq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured. Set it in backend/.env.",
        )
    return Groq(api_key=settings.groq_api_key)


def build_context(sources: list[Source]) -> str:
    return "\n\n".join(
        f"[{index}] ({source.filename}, chunk {source.chunk_index})\n{source.text}"
        for index, source in enumerate(sources, start=1)
    )


def answer(question: str, sources: list[Source]) -> str:
    settings = get_settings()
    completion = get_client().chat.completions.create(
        model=settings.groq_model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context:\n{build_context(sources)}\n\nQuestion: {question}",
            },
        ],
    )
    return completion.choices[0].message.content or ""
