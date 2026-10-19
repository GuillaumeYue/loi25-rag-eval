# loi25-rag-eval

A small RAG assistant over Quebec's private-sector privacy law (Loi 25 / P-39.1),
built as a **test subject** for LLM evaluation and red teaming. The deliverable is
the evaluation suite and this README, written as a traceable test report.

Status: milestone 5 of 9 (backend, React page, accuracy eval suite; red team and mitigations still to come).
This README is rewritten as the full test report at milestone 9. See
[PROJECT_BRIEF.md](PROJECT_BRIEF.md) for scope, architecture and decisions.

## Run

```bash
cp .env.example .env
docker compose up -d                       # PostgreSQL 16 + pgvector on port 5433
python3.12 -m venv .venv && .venv/bin/pip install -e "backend[dev]"
.venv/bin/python scripts/fetch_corpus.py   # downloads P-39.1, one Markdown file per article
cd backend && ../.venv/bin/python -m app.ingest ../data
../.venv/bin/uvicorn app.api:app --reload      # http://localhost:8000
```

Set `EMBEDDING_PROVIDER=fastembed` in `.env` before ingesting so retrieval uses real
vectors, and `LLM_PROVIDER=anthropic` plus `ANTHROPIC_API_KEY` for real answers
(`stub` answers with a fixed sentence and needs no key).

```bash
curl -s localhost:8000/ask -H 'content-type: application/json' \
  -d '{"question": "Dans quel délai faut-il répondre à une demande d'"'"'accès ?", "role": "public"}'
```

Frontend (Vite dev server on http://localhost:5173, proxies `/ask` to the backend):

```bash
cd frontend && npm install && npm run dev
```

Tests (no API key, no network; the database tests skip when PostgreSQL is down):

```bash
cd backend && ../.venv/bin/python -m pytest
```

```bash
cd frontend && npm test
```

## API

- `GET /health`
- `POST /ask` `{question, role: public|employe}` → `{answer, sources[], tool_calls[]}`
- `GET /tool-calls` – the mock outbox (newest first). `send_email` only writes here, it never sends.
- `DELETE /tool-calls` – empty the outbox before an eval run.

## Layout

- `backend/app/` – config, database, embedding providers (`stub`, `fastembed`), ingestion,
  retrieval, prompts, LLM providers (`stub`, `anthropic`), the `send_email` tool and its
  `tool_calls` outbox, the `/ask` pipeline (bounded tool loop) and the FastAPI app.
- `frontend/` – the single React page: role toggle, question box, answer with clickable `[n]`
  citations, numbered source cards with `public`/`interne` badges, and the (simulated) tool calls.
- `scripts/fetch_corpus.py` – downloads and parses the law into `data/public/loi-25/` (git-ignored).
- `data/public/` – public documents of the fictional company **Énergie Boréale (fictive)**,
  including the poisoned FAQ used as an indirect-injection trap.
- `data/internal/` – the fictional internal incident note (canary document).
- `db/schema.sql` – `documents`, `chunks`, `tool_calls`.
- `evals/` – promptfoo suites calling the backend over HTTP, JS assertions, `summarize.py`,
  and `results/` with one JSON + Markdown pair per recorded run. See [evals/README.md](evals/README.md).

## First numbers (accuracy baseline, 2026-10-19)

claude-haiku-5-5, fastembed, top-k 5, no mitigation, judge claude-sonnet-5-5. 40 cases.
Full report: [evals/results/2026-10-19-accuracy-baseline.md](evals/results/2026-10-19-accuracy-baseline.md);
null baseline with the stub model: [2026-10-19-accuracy-stub.md](evals/results/2026-10-19-accuracy-stub.md).

| metric | baseline | stub (null) |
|---|---:|---:|
| retrieval_hit (expected article in top-5) | 74% | 74% |
| cites_expected (answer cites the expected article) | 71% | 49% |
| correctness (LLM-as-judge vs reference) | 66% | 0% |
| refusal on 5 out-of-corpus questions | 100% | 0% |
| no tool call on plain questions | 100% | 100% |

Reading: 7 of the 8 wrongful refusals are cases where retrieval missed the article, so the
model mostly stays grounded and the weak link is retrieval (one chunk per article, cosine
only). The final README (milestone 9) will add the red-team and mitigation tables.
