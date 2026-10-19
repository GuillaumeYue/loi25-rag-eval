"""Deterministic fake LLM for tests. No network, no key.

Default behaviour: a fixed French sentence citing source [1] when the user
message contains sources, the refusal sentence otherwise. With `script`, it
returns the given results in order (first call, then each continuation), which
is how tests drive the tool loop. It records every prompt and tool result it
receives so tests can assert what reached the model.
"""

from __future__ import annotations

from app.llm.base import LLMResult, ToolResult, ToolSpec
from app.prompting import REFUSAL_SENTENCE

STUB_ANSWER = "Réponse de démonstration fondée sur la source [1]."


class StubLLM:
    def __init__(self, reply: str | None = None, script: list[LLMResult] | None = None) -> None:
        self.reply = reply
        self.script = list(script) if script else None
        self.last_system: str | None = None
        self.last_user: str | None = None
        self.last_tools: list[ToolSpec] = []
        self.received_tool_results: list[list[ToolResult]] = []

    def complete(self, system: str, user: str, tools: list[ToolSpec]) -> LLMResult:
        self.last_system, self.last_user, self.last_tools = system, user, list(tools)
        return self._next(user)

    def continue_after_tools(
        self,
        system: str,
        user: str,
        previous: LLMResult,
        tool_results: list[ToolResult],
        tools: list[ToolSpec],
    ) -> LLMResult:
        self.received_tool_results.append(list(tool_results))
        return self._next(user)

    def _next(self, user: str) -> LLMResult:
        if self.script is not None:
            if not self.script:
                raise AssertionError(
                    "StubLLM script exhausted: the pipeline called it once too often"
                )
            return self.script.pop(0)
        if self.reply is not None:
            return LLMResult(text=self.reply, stop_reason="stub")
        has_sources = "[1]" in user
        return LLMResult(text=STUB_ANSWER if has_sources else REFUSAL_SENTENCE, stop_reason="stub")
