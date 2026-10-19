"""CLI: python -m app.ingest [data_dir]"""

from __future__ import annotations

import sys
from pathlib import Path

from app import config, db
from app.embeddings import get_embedder


def main(argv: list[str]) -> int:
    data_dir = Path(argv[1]) if len(argv) > 1 else config.DATA_DIR
    embedder = get_embedder()
    print(f"embedding provider: {config.embedding_provider()}")
    with db.connect() as conn:
        from app.ingest.ingest import ingest_dir

        results = ingest_dir(conn, embedder, data_dir)
    for source, n in results.items():
        print(f"{n:4d} chunks  {source}")
    print(f"{len(results)} documents, {sum(results.values())} chunks")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
