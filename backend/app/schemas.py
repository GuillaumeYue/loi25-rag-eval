"""Request and response models for the HTTP API (contract in PROJECT_BRIEF.md)."""

from __future__ import annotations

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


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    tool_calls: list[ToolCallOut] = []
