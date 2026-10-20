"""Settings read from environment variables.

A `.env` file at the repository root is loaded if present (see `.env.example`).
Plain `os.environ` is used on purpose: every variable is visible here, with
its default, and nothing is hidden behind a settings framework.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
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


def tool_allowed_domains() -> list[str]:
    """Recipient domains TOOL_GUARD accepts for send_email (comma-separated)."""
    raw = os.environ.get("TOOL_ALLOWED_DOMAINS", "energie-boreale.example")
    return [d.strip().lower() for d in raw.split(",") if d.strip()]


# --- Mitigation flags --------------------------------------------------------
# Each mitigation has its own flag and every flag defaults to OFF, so the
# baseline and each mitigation run on the same code and the same eval suites.

_TRUE = {"1", "true", "yes", "on"}


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUE


@dataclass(frozen=True)
class Flags:
    enforce_access_control: bool = False  # filter retrieval by role, in SQL
    isolate_context: bool = False  # delimited sources, "data, not instructions"
    tool_guard: bool = False  # policy check before any tool runs
    output_filter: bool = False  # withhold public answers carrying internal text

    def as_env(self) -> dict[str, bool]:
        """Same names as the environment variables, for /health and reports."""
        return {name.upper(): value for name, value in asdict(self).items()}


def flags() -> Flags:
    """Read on every call so a test (or a restarted server) sees the current env."""
    return Flags(
        enforce_access_control=_flag("ENFORCE_ACCESS_CONTROL"),
        isolate_context=_flag("ISOLATE_CONTEXT"),
        tool_guard=_flag("TOOL_GUARD"),
        output_filter=_flag("OUTPUT_FILTER"),
    )


SCHEMA_FILE = REPO_ROOT / "db" / "schema.sql"
DATA_DIR = REPO_ROOT / "data"
