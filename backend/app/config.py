"""Settings read from environment variables.

A `.env` file at the repository root is loaded if present (see `.env.example`).
Plain `os.environ` is used on purpose: every variable is visible here, with
its default, and nothing is hidden behind a settings framework.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(REPO_ROOT / ".env")


def database_url() -> str:
    return os.environ.get("DATABASE_URL", "postgresql://loi25:loi25@localhost:5433/loi25")


def embedding_provider() -> str:
    """`stub` (tests, no model) or `fastembed` (local model)."""
    return os.environ.get("EMBEDDING_PROVIDER", "stub")


def embedding_model() -> str:
    return os.environ.get(
        "EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )


def llm_provider() -> str:
    """`stub` (tests), `anthropic` (Claude API) or `ollama` (not implemented yet)."""
    return os.environ.get("LLM_PROVIDER", "stub")


def anthropic_model() -> str:
    return os.environ.get("ANTHROPIC_MODEL", "claude-haiku-5-5")


def llm_max_tokens() -> int:
    return int(os.environ.get("LLM_MAX_TOKENS", "4096"))


def top_k() -> int:
    return int(os.environ.get("TOP_K", "5"))


SCHEMA_FILE = REPO_ROOT / "db" / "schema.sql"
DATA_DIR = REPO_ROOT / "data"
