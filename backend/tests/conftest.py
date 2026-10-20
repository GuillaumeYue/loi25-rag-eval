"""Shared fixtures. Unit tests never need a database; the one test that does
(test_ingest_db.py) skips itself when PostgreSQL is not reachable."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Make `scripts/` importable so the corpus parser can be tested.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "evals"))  # summarize.py

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def stub_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests always run with stub providers and every mitigation off,
    whatever .env or the shell says. Tests that need a flag set it themselves."""
    monkeypatch.setenv("EMBEDDING_PROVIDER", "stub")
    monkeypatch.setenv("LLM_PROVIDER", "stub")
    for name in ("ENFORCE_ACCESS_CONTROL", "ISOLATE_CONTEXT", "TOOL_GUARD", "OUTPUT_FILTER"):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def db_conn():
    """A connection to the test database, or skip.

    With REQUIRE_DB=1 (set in CI) an unreachable database is a failure, not a
    skip, so the database tests cannot silently drop out of a green run.
    """
    import psycopg

    from app import db

    url = os.environ.get("DATABASE_URL", "postgresql://loi25:loi25@localhost:5433/loi25")
    try:
        conn = db.connect(url)
    except psycopg.OperationalError as exc:
        message = f"PostgreSQL not reachable at {url}: {exc}"
        if os.environ.get("REQUIRE_DB") == "1":
            pytest.fail(message)
        pytest.skip(message)
    yield conn
    conn.close()
