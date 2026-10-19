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

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def stub_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    """Unit tests always run with the stub embedder, whatever .env says."""
    monkeypatch.setenv("EMBEDDING_PROVIDER", "stub")


@pytest.fixture
def db_conn():
    """A connection to the test database, or skip."""
    import psycopg

    from app import db

    url = os.environ.get("DATABASE_URL", "postgresql://loi25:loi25@localhost:5433/loi25")
    try:
        conn = db.connect(url)
    except psycopg.OperationalError as exc:
        pytest.skip(f"PostgreSQL not reachable at {url}: {exc}")
    yield conn
    conn.close()
