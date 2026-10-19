"""Ingest files from the data directory into PostgreSQL.

Layout rule (see PROJECT_BRIEF.md):
    data/public/**    -> classification 'public'
    data/internal/**  -> classification 'interne'
"""

from __future__ import annotations

from pathlib import Path

import psycopg

from app.embeddings.base import Embedder
from app.ingest.chunking import chunk_text
from app.ingest.loaders import SUPPORTED_SUFFIXES, load_file, title_for


def classification_for(path: Path, data_dir: Path) -> str:
    rel = path.resolve().relative_to(data_dir.resolve())
    top = rel.parts[0] if rel.parts else ""
    if top == "public":
        return "public"
    if top == "internal":
        return "interne"
    raise ValueError(f"{rel} is not under data/public or data/internal")


def ingest_file(
    conn: psycopg.Connection,
    embedder: Embedder,
    path: Path,
    classification: str,
    source: str,
) -> int:
    """Upsert one document and replace its chunks. Returns the number of chunks."""
    text = load_file(path)
    title = title_for(path, text)
    chunks = chunk_text(text)
    vectors = embedder.embed(chunks) if chunks else []

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents (source, title, classification)
            VALUES (%s, %s, %s)
            ON CONFLICT (source) DO UPDATE
                SET title = EXCLUDED.title, classification = EXCLUDED.classification
            RETURNING id
            """,
            (source, title, classification),
        )
        (doc_id,) = cur.fetchone()
        cur.execute("DELETE FROM chunks WHERE document_id = %s", (doc_id,))
        cur.executemany(
            "INSERT INTO chunks (document_id, ordinal, content, embedding) VALUES (%s, %s, %s, %s)",
            [
                (doc_id, i, content, vec)
                for i, (content, vec) in enumerate(zip(chunks, vectors, strict=True))
            ],
        )
    conn.commit()
    return len(chunks)


def ingest_dir(conn: psycopg.Connection, embedder: Embedder, data_dir: Path) -> dict[str, int]:
    """Ingest every supported file under data/public and data/internal."""
    results: dict[str, int] = {}
    for sub in ("public", "internal"):
        root = data_dir / sub
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            source = path.relative_to(data_dir).as_posix()
            results[source] = ingest_file(
                conn, embedder, path, classification_for(path, data_dir), source
            )
    return results
