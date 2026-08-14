from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import main, store
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_delete_unknown_document_returns_404(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(store, "delete_document", lambda document_id: False)
    response = client.delete("/documents/does-not-exist")
    assert response.status_code == 404


def test_delete_removes_stored_upload(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(main.settings, "upload_dir", str(tmp_path))
    monkeypatch.setattr(store, "delete_document", lambda document_id: True)
    stored = tmp_path / "abc123-notes.txt"
    stored.write_text("hello")

    assert client.delete("/documents/abc123").status_code == 204
    assert not stored.exists()


def test_chat_without_documents(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(store, "query", lambda question, top_k, document_ids: [])
    response = client.post("/chat", json={"question": "anything?"})
    assert response.status_code == 200
    assert response.json()["sources"] == []
