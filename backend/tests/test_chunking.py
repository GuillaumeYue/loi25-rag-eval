from app.ingest.chunking import chunk_text


def test_short_text_is_one_chunk():
    assert chunk_text("Bonjour le monde.") == ["Bonjour le monde."]


def test_empty_text_gives_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("\n\n   \n") == []


def test_paragraphs_are_packed_up_to_the_limit():
    paragraphs = [f"Paragraphe {i}. " + "mot " * 40 for i in range(10)]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text, max_chars=500, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 500 for c in chunks)
    # Every paragraph survives intact in at least one chunk.
    for p in paragraphs:
        assert any(p.strip() in c for c in chunks), p[:20]


def test_consecutive_chunks_overlap():
    paragraphs = [f"P{i} " + "x" * 300 for i in range(6)]
    chunks = chunk_text("\n\n".join(paragraphs), max_chars=700, overlap=100)
    assert len(chunks) >= 3
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        tail = prev[-100:].lstrip()
        assert nxt.startswith(tail)


def test_long_paragraph_is_split_on_sentences():
    sentences = [f"Phrase numéro {i} qui est assez longue pour compter." for i in range(30)]
    text = " ".join(sentences)  # one paragraph, no blank lines
    chunks = chunk_text(text, max_chars=300, overlap=0)
    assert len(chunks) > 1
    assert all(len(c) <= 300 for c in chunks)
    for s in sentences:
        assert any(s in c for c in chunks)


def test_oversized_sentence_is_hard_cut():
    text = "a" * 2000
    chunks = chunk_text(text, max_chars=900, overlap=0)
    assert all(len(c) <= 900 for c in chunks)
    assert "".join(chunks) == text


def test_overlap_must_be_smaller_than_max():
    import pytest

    with pytest.raises(ValueError):
        chunk_text("x", max_chars=100, overlap=100)
