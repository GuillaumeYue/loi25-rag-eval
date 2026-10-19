# CLAUDE.md

Read `PROJECT_BRIEF.md` first. It holds the scope, architecture and decisions; do not change those without asking.

## How we work

- Design before code. For each milestone, propose the plan (files, interfaces, tests) and wait for approval before writing it.
- Small steps. One milestone at a time, each ending with passing tests and a commit.
- I must be able to explain every line that gets merged. Prefer plain, readable code over clever code, and explain any non-obvious choice in the commit message or a short comment.
- When something is uncertain (library behaviour, an API detail), check the docs or run it; do not guess.

## Code

- Python 3.11+, FastAPI, psycopg 3 + pgvector, pytest. React (Vite) for the single page.
- Code, identifiers and comments in English. Corpus, prompts shown to the model, and eval questions in French.
- Providers are swappable through environment variables (`LLM_PROVIDER`, `EMBEDDING_PROVIDER`). Unit tests always use the `stub` providers and must pass with no API key and no network.
- Tests that need PostgreSQL skip cleanly when the database is not reachable.

## Security rules for this repo

- Never commit secrets. `.env` is git-ignored; `.env.example` documents every variable.
- The trap documents are fictional (company "Énergie Boréale (fictive)"). Never use a real organization's name, branding or data.
- `send_email` must never send anything. It only writes to the `tool_calls` table.
- Mitigations live behind their own flags and default to off, so baseline and mitigated runs stay comparable. Do not quietly "fix" the baseline.

## Evals

- promptfoo calls the backend over HTTP. Every red-team case carries an OWASP LLM Top 10 ID and a short note on what counts as a failure.
- Record results (date, model, flags, pass rates) in `evals/results/` so the README numbers are traceable.
