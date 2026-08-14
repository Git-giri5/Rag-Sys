import io

from fastapi import HTTPException
from pypdf import PdfReader

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def extract_text(filename: str, content: bytes) -> str:
    suffix = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix or filename}'. Supported: pdf, txt, md.",
        )

    if suffix == ".pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
        except Exception as exc:  # noqa: BLE001 - surfaced to the client as 400
            raise HTTPException(status_code=400, detail=f"Could not read PDF: {exc}") from exc
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")
