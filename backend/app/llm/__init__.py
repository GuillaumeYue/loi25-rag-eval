"""Generation provider factory, selected by LLM_PROVIDER."""

from __future__ import annotations

from app import config
from app.llm.base import LLMError, LLMProvider, LLMResult, ToolCall, ToolSpec

__all__ = ["LLMError", "LLMProvider", "LLMResult", "ToolCall", "ToolSpec", "get_llm"]


def get_llm(name: str | None = None) -> LLMProvider:
    name = name or config.llm_provider()
    if name == "stub":
        from app.llm.stub import StubLLM

        return StubLLM()
    if name == "anthropic":
        from app.llm.anthropic_provider import AnthropicLLM

        return AnthropicLLM()
    if name == "ollama":
        raise NotImplementedError("LLM_PROVIDER=ollama is planned but not implemented yet")
    raise ValueError(f"unknown LLM_PROVIDER: {name!r} (expected 'stub', 'anthropic' or 'ollama')")
