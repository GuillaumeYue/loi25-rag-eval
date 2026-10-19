"""Needs PostgreSQL (docker compose up -d). Skips cleanly otherwise."""

from pathlib import Path

from app.embeddings.stub import StubEmbedder
from app.ingest.ingest import ingest_dir


def _make_data_dir(tmp_path: Path) -> Path:
    data = tmp_path / "data"
    (data / "public").mkdir(parents=True)
    (data / "internal").mkdir()
    (data / "raw").mkdir()
    (data / "public" / "faq.md").write_text(
        "# FAQ test\n\n" + "\n\n".join("Paragraphe " + "mot " * 150 for _ in range(4)),
        encoding="utf-8",
    )
    (data / "internal" / "note.md").write_text("# Note interne\n\nCourt.", encoding="utf-8")
    (data / "raw" / "ignored.html").write_text("<p>jamais ingéré</p>", encoding="utf-8")
    return data


def _cleanup(conn, sources):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents WHERE source = ANY(%s)", (list(sources),))
    conn.commit()


def test_ingest_then_reingest_replaces_chunks(db_conn, tmp_path: Path):
    data = _make_data_dir(tmp_path)
    sources = ["public/faq.md", "internal/note.md"]
    _cleanup(db_conn, sources)
    try:
        results = ingest_dir(db_conn, StubEmbedder(), data)
        assert set(results) == set(sources)
        assert results["public/faq.md"] > 1
        assert results["internal/note.md"] == 1

        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT source, title, classification FROM documents "
                "WHERE source = ANY(%s) ORDER BY source",
                (sources,),
            )
            rows = cur.fetchall()
        assert rows == [
            ("internal/note.md", "Note interne", "interne"),
            ("public/faq.md", "FAQ test", "public"),
        ]

        def chunk_count(source: str) -> int:
            with db_conn.cursor() as cur:
                cur.execute(
                    "SELECT count(*) FROM chunks c JOIN documents d ON d.id = c.document_id "
                    "WHERE d.source = %s",
                    (source,),
                )
                return cur.fetchone()[0]

        before = chunk_count("public/faq.md")
        ingest_dir(db_conn, StubEmbedder(), data)
        assert chunk_count("public/faq.md") == before  # replaced, not appended

        # The stored vector round-trips through pgvector.
        with db_conn.cursor() as cur:
            cur.execute(
                "SELECT c.content, c.embedding FROM chunks c JOIN documents d "
                "ON d.id = c.document_id WHERE d.source = %s",
                ("internal/note.md",),
            )
            content, embedding = cur.fetchone()
        assert "Court." in content
        # pgvector returns a numpy array when numpy is installed, else its own Vector type.
        values = embedding.to_list() if hasattr(embedding, "to_list") else list(embedding)
        assert len(values) == 384
    finally:
        _cleanup(db_conn, sources)
