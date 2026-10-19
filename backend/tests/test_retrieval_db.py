"""Needs PostgreSQL. Skips cleanly otherwise."""

from pathlib import Path

from app.embeddings.stub import StubEmbedder
from app.ingest.ingest import ingest_dir
from app.retrieval import retrieve

SOURCES = ["public/alpha.md", "internal/beta.md"]
ALPHA_TEXT = "Alpha : texte unique du premier document de test de recherche."
BETA_TEXT = "Beta : texte unique du second document, classé interne."


def _cleanup(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM documents WHERE source = ANY(%s)", (SOURCES,))
    conn.commit()


def test_exact_text_retrieves_its_own_chunk_first(db_conn, tmp_path: Path):
    data = tmp_path / "data"
    (data / "public").mkdir(parents=True)
    (data / "internal").mkdir()
    (data / "public" / "alpha.md").write_text(ALPHA_TEXT, encoding="utf-8")
    (data / "internal" / "beta.md").write_text(BETA_TEXT, encoding="utf-8")
    embedder = StubEmbedder()
    _cleanup(db_conn)
    try:
        ingest_dir(db_conn, embedder, data)

        # The stub maps identical text to identical vectors, so the chunk's own
        # content must come back first with cosine similarity ~1.
        top = retrieve(db_conn, embedder, BETA_TEXT, k=3, role="public")
        assert top[0].source == "internal/beta.md"
        assert top[0].classification == "interne"  # baseline: no filtering by role
        assert abs(top[0].score - 1.0) < 1e-6
        assert len(top) <= 3
        assert all(top[i].score >= top[i + 1].score for i in range(len(top) - 1))
    finally:
        _cleanup(db_conn)
