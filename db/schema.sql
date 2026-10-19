-- Schema for loi25-rag-eval. Every statement is idempotent so this file can be
-- run on a fresh database (docker-entrypoint) and re-run by the app safely.

CREATE EXTENSION IF NOT EXISTS vector;

-- One row per ingested file. `source` is the path relative to the data
-- directory, e.g. "public/faq-clients.md". Re-ingesting the same source
-- replaces its chunks instead of adding duplicates.
CREATE TABLE IF NOT EXISTS documents (
    id             serial PRIMARY KEY,
    source         text NOT NULL UNIQUE,
    title          text NOT NULL,
    classification text NOT NULL CHECK (classification IN ('public', 'interne')),
    created_at     timestamptz NOT NULL DEFAULT now()
);

-- 384 dimensions matches paraphrase-multilingual-MiniLM-L12-v2 and the stub.
-- No vector index on purpose: the corpus is a few hundred chunks, and an
-- exact scan is both fast enough and simpler to reason about in evals.
CREATE TABLE IF NOT EXISTS chunks (
    id          serial PRIMARY KEY,
    document_id integer NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    ordinal     integer NOT NULL,
    content     text NOT NULL,
    embedding   vector(384) NOT NULL,
    UNIQUE (document_id, ordinal)
);

-- Mock outbox for the send_email tool. Nothing is ever sent; evals read this
-- table to detect tool misuse.
CREATE TABLE IF NOT EXISTS tool_calls (
    id         serial PRIMARY KEY,
    tool       text NOT NULL,
    arguments  jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
