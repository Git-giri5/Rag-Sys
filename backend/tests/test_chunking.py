from app.chunking import chunk_text


def test_merges_small_paragraphs() -> None:
    text = "alpha\n\nbeta\n\ngamma"
    assert chunk_text(text, chunk_size=100, overlap=10) == ["alpha\n\nbeta\n\ngamma"]


def test_splits_long_paragraph_with_overlap() -> None:
    chunks = chunk_text("x" * 250, chunk_size=100, overlap=20)
    assert len(chunks) == 4
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_empty_text() -> None:
    assert chunk_text("   \n\n  ", chunk_size=100, overlap=10) == []
