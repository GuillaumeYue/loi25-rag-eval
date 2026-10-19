"""PostgreSQL access with psycopg 3 and pgvector."""

from __future__ import annotations

import sys

import psycopg
from pgvector.psycopg import register_vector

from app import config


def connect(url: str | None = None) -> psycopg.Connection:
    """Open a connection with the pgvector type adapter registered.

    `register_vector` needs the `vector` extension to exist, so the schema is
    applied first on a plain connection. Both steps are idempotent.
    """
    conn = psycopg.connect(url or config.database_url())
    apply_schema(conn)
    register_vector(conn)
    return conn


def apply_schema(conn: psycopg.Connection) -> None:
    """Run db/schema.sql. Safe to call repeatedly: every statement is IF NOT EXISTS."""
    sql = config.SCHEMA_FILE.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


if __name__ == "__main__":
    # `python -m app.db` applies the schema and prints the table list.
    with connect() as c, c.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        for (name,) in cur.fetchall():
            print(name)
    sys.exit(0)
