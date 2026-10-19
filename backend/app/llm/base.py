"""The interface every generation provider implements.

A call to the model is one system prompt, one user message and zero or more
tools. When the model asks for tools, the pipeline executes them and continues
the same exchange with `continue_after_tools`, which replays the model's own
previous content (`LLMResult.raw`) unchanged, followed by the tool results.
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
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    content: str
    is_error: bool = False


@dataclass(frozen=True)
class LLMResult:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    # Provider-neutral: "end_turn", "tool_use", "max_tokens", "refusal", "stub".
    stop_reason: str = "end_turn"
    # The provider's own assistant content (e.g. Anthropic content blocks, thinking
    # included). Opaque to the pipeline; passed back verbatim on continuation.
    raw: Any = None


class LLMError(RuntimeError):
    """Raised when the provider cannot produce an answer (network, quota, bad request)."""


class LLMProvider(Protocol):
    def complete(self, system: str, user: str, tools: list[ToolSpec]) -> LLMResult:
        """First turn: system prompt, user message, available tools."""
        ...

    def continue_after_tools(
        self,
        system: str,
        user: str,
        previous: LLMResult,
        tool_results: list[ToolResult],
        tools: list[ToolSpec],
    ) -> LLMResult:
        """Hand the tool results back and let the model finish (or ask for more tools)."""
        ...
