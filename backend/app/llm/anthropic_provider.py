"""Claude API provider (official `anthropic` SDK, Messages API)."""

from __future__ import annotations

from typing import Any

import anthropic

from app import config
from app.llm.base import LLMError, LLMResult, ToolCall, ToolSpec


class AnthropicLLM:
    def __init__(self, model: str | None = None, max_tokens: int | None = None) -> None:
        # The client reads ANTHROPIC_API_KEY from the environment (loaded from .env by config).
        self._client = anthropic.Anthropic()
        self._model = model or config.anthropic_model()
        self._max_tokens = max_tokens or config.llm_max_tokens()

    def complete(self, system: str, user: str, tools: list[ToolSpec]) -> LLMResult:
        kwargs: dict[str, Any] = {}
        if tools:
            kwargs["tools"] = [
                {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                for t in tools
            ]
        try:
            # No temperature/top_p: current models reject non-default sampling parameters.
            # Thinking is left at the model default (adaptive on Haiku 5.5).
            response = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                **kwargs,
            )
        except anthropic.RateLimitError as exc:
            raise LLMError(f"rate limited by the Claude API: {exc.message}") from exc
        except anthropic.APIStatusError as exc:
            raise LLMError(f"Claude API error {exc.status_code}: {exc.message}") from exc
        except anthropic.APIConnectionError as exc:
            raise LLMError(f"cannot reach the Claude API: {exc}") from exc
        return parse_response(response)


def parse_response(response: Any) -> LLMResult:
    """Turn a Messages API response into an LLMResult.

    Takes any object with `.content` (blocks with `.type`) and `.stop_reason`, so
    tests can pass a plain stand-in instead of a real `anthropic.types.Message`.
    """
    texts: list[str] = []
    calls: list[ToolCall] = []
    for block in response.content:
        if block.type == "text":
            texts.append(block.text)
        elif block.type == "tool_use":
            # `input` is already parsed JSON (a dict) in the SDK.
            calls.append(ToolCall(name=block.name, arguments=dict(block.input)))
    return LLMResult(
        text="\n".join(texts).strip(),
        tool_calls=calls,
        stop_reason=response.stop_reason or "end_turn",
    )
