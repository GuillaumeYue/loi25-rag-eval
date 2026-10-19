"""Top-k retrieval over pgvector with cosine distance."""

from __future__ import annotations

from dataclasses import dataclass

import psycopg

from app.embeddings.base import Embedder


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    content: str
    title: str
    source: str
    classification: str
    score: float  # cosine similarity, 1.0 = identical


def retrieve(
    conn: psycopg.Connection,
    embedder: Embedder,
    question: str,
    k: int,
    role: str,
) -> list[RetrievedChunk]:
    """Return the k chunks closest to the question, best first.

    `role` is accepted but not used yet. In the baseline every chunk, public or
    interne, is a candidate for every caller; that is the sensitive-information
    leak the red-team suite is meant to catch. Filtering by classification lands
    in milestone 7 behind the ENFORCE_ACCESS_CONTROL flag, inside this query.
    """
    del role  # see docstring
    (vector,) = embedder.embed([question])
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.content, d.title, d.source, d.classification,
                   1 - (c.embedding <=> %(v)s::vector) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.embedding <=> %(v)s::vector
            LIMIT %(k)s
            """,
            {"v": vector, "k": k},
        )
        rows = cur.fetchall()
    return [RetrievedChunk(*row) for row in rows]
