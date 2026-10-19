"""Deterministic fake LLM for tests. No network, no key.

It answers with a fixed French sentence citing source [1] when the user message
contains sources, and with the refusal sentence otherwise. It also keeps the
last prompt it received so tests can assert what reached the model.
"""

from __future__ import annotations

from app.llm.base import LLMResult, ToolSpec
from app.prompting import REFUSAL_SENTENCE

STUB_ANSWER = "Réponse de démonstration fondée sur la source [1]."


class StubLLM:
    def __init__(self, reply: str | None = None) -> None:
        self.reply = reply
        self.last_system: str | None = None
        self.last_user: str | None = None
        self.last_tools: list[ToolSpec] = []

    def complete(self, system: str, user: str, tools: list[ToolSpec]) -> LLMResult:
        self.last_system, self.last_user, self.last_tools = system, user, list(tools)
        if self.reply is not None:
            return LLMResult(text=self.reply, stop_reason="stub")
        has_sources = "[1]" in user
        return LLMResult(text=STUB_ANSWER if has_sources else REFUSAL_SENTENCE, stop_reason="stub")
