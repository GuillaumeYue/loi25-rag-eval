# loi25-rag-eval

A small RAG assistant over Quebec's private-sector privacy law (Loi 25 / P-39.1),
built as a **test subject** for LLM evaluation and red teaming. The deliverable is
the evaluation suite and this README, written as a traceable test report.

Status: milestone 1 of 9 (repo, database, ingestion, corpus, trap documents).
This README is rewritten as the full test report at milestone 9. See
[PROJECT_BRIEF.md](PROJECT_BRIEF.md) for scope, architecture and decisions.

## Run (milestone 1)

```bash
cp .env.example .env
docker compose up -d                       # PostgreSQL 16 + pgvector on port 5433
python3.12 -m venv .venv && .venv/bin/pip install -e "backend[dev]"
.venv/bin/python scripts/fetch_corpus.py   # downloads P-39.1, one Markdown file per article
cd backend && ../.venv/bin/python -m app.ingest ../data
```

Tests (no API key, no network; the database test skips when PostgreSQL is down):

```bash
cd backend && ../.venv/bin/python -m pytest
```

## Layout

- `backend/app/` – config, database, embedding providers (`stub`, `fastembed`), ingestion.
- `scripts/fetch_corpus.py` – downloads and parses the law into `data/public/loi-25/` (git-ignored).
- `data/public/` – public documents of the fictional company **Énergie Boréale (fictive)**,
  including the poisoned FAQ used as an indirect-injection trap.
- `data/internal/` – the fictional internal incident note (canary document).
- `db/schema.sql` – `documents`, `chunks`, `tool_calls`.
