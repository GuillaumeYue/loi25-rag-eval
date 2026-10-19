"""The interface every generation provider implements.

Tools are part of the interface from the start so milestone 3 (send_email) only
adds a tool definition, not a new provider API. In milestone 2 `tools` is empty.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ToolSpec:
    """A tool offered to the model, in provider-neutral form (JSON Schema input)."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class LLMResult:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    # Provider-neutral: "end_turn", "tool_use", "max_tokens", "refusal", "stub".
    stop_reason: str = "end_turn"


class LLMError(RuntimeError):
    """Raised when the provider cannot produce an answer (network, quota, bad request)."""


class LLMProvider(Protocol):
    def complete(self, system: str, user: str, tools: list[ToolSpec]) -> LLMResult:
        """One system prompt, one user message, zero or more tools; one answer."""
        ...
