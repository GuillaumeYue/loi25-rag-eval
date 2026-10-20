"""Request and response models for the HTTP API (contract in PROJECT_BRIEF.md)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

Role = Literal["public", "employe"]


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    role: Role = "public"


class Source(BaseModel):
    n: int
    title: str
    source: str
    classification: Literal["public", "interne"]
    excerpt: str


class ToolCallOut(BaseModel):
    tool: str
    arguments: dict[str, Any]


class BlockedToolCallOut(BaseModel):
    """A tool call the model attempted and TOOL_GUARD refused (never executed)."""

    tool: str
    arguments: dict[str, Any]
    reason: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    tool_calls: list[ToolCallOut] = []  # executed (logged to the mock outbox)
    # Added in milestone 7; both stay empty/false in the baseline.
    blocked_tool_calls: list[BlockedToolCallOut] = []
    output_filtered: bool = False


class ToolCallRecordOut(BaseModel):
    """One row of the mock outbox (GET /tool-calls)."""

    id: int
    tool: str
    arguments: dict[str, Any]
    created_at: datetime
