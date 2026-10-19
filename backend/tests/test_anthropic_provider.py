"""Response parsing only. The real client is never built here (no key, no network)."""

from types import SimpleNamespace

import pytest

from app.llm import get_llm
from app.llm.anthropic_provider import parse_response


def test_text_blocks_are_joined_and_tool_calls_collected():
    response = SimpleNamespace(
        stop_reason="tool_use",
        content=[
            SimpleNamespace(type="text", text="Je vais envoyer le résumé."),
            SimpleNamespace(
                type="tool_use",
                name="send_email",
                input={"to": "a@b.example", "subject": "s", "body": "b"},
            ),
            SimpleNamespace(type="text", text="Voilà [1]."),
        ],
    )
    result = parse_response(response)
    assert result.text == "Je vais envoyer le résumé.\nVoilà [1]."
    assert result.stop_reason == "tool_use"
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "send_email"
    assert result.tool_calls[0].arguments["to"] == "a@b.example"


def test_unknown_blocks_are_ignored_and_missing_stop_reason_defaults():
    response = SimpleNamespace(
        stop_reason=None,
        content=[
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text="Ok"),
        ],
    )
    result = parse_response(response)
    assert result.text == "Ok"
    assert result.stop_reason == "end_turn"


def test_factory():
    from app.llm.stub import StubLLM

    assert isinstance(get_llm("stub"), StubLLM)
    with pytest.raises(NotImplementedError):
        get_llm("ollama")
    with pytest.raises(ValueError):
        get_llm("gpt")
