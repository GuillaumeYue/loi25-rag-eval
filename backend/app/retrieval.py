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


ALL_CLASSIFICATIONS = ("public", "interne")


def allowed_classifications(role: str, enforce: bool) -> list[str]:
    """Which document classifications a caller may retrieve.

    Baseline (enforce=False): everything, for everyone. That is the leak the
    red-team suite measures. With ENFORCE_ACCESS_CONTROL a public caller only
    gets public documents; an employee gets both. Unknown roles get public only.
    """
    if not enforce or role == "employe":
        return list(ALL_CLASSIFICATIONS)
    return ["public"]


def retrieve(
    conn: psycopg.Connection,
    embedder: Embedder,
    question: str,
    k: int,
    role: str,
    *,
    enforce_access_control: bool = False,
) -> list[RetrievedChunk]:
    """Return the k chunks closest to the question, best first.

    Access control is applied in the WHERE clause, before ranking: an interne
    chunk a public caller may not see never reaches the prompt, so no prompt
    wording or output check has to hold the line (ENFORCE_ACCESS_CONTROL).
    """
    allowed = allowed_classifications(role, enforce_access_control)
    (vector,) = embedder.embed([question])
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.content, d.title, d.source, d.classification,
                   1 - (c.embedding <=> %(v)s::vector) AS score
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.classification = ANY(%(allowed)s)
            ORDER BY c.embedding <=> %(v)s::vector
            LIMIT %(k)s
            """,
            {"v": vector, "k": k, "allowed": allowed},
        )
        rows = cur.fetchall()
    return [RetrievedChunk(*row) for row in rows]
