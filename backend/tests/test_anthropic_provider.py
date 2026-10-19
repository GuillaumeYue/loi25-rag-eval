"""Response parsing only. The real client is never built here (no key, no network)."""

from types import SimpleNamespace

import pytest

from app.llm import get_llm
from app.llm.anthropic_provider import build_continuation_messages, parse_response, tool_definition
from app.llm.base import LLMResult, ToolCall, ToolResult
from app.tools import SEND_EMAIL


def test_text_blocks_are_joined_and_tool_calls_collected():
    response = SimpleNamespace(
        stop_reason="tool_use",
        content=[
            SimpleNamespace(type="text", text="Je vais envoyer le résumé."),
            SimpleNamespace(
                type="tool_use",
                id="toolu_01",
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
    assert result.tool_calls[0].id == "toolu_01"
    assert result.tool_calls[0].name == "send_email"
    assert result.tool_calls[0].arguments["to"] == "a@b.example"
    assert result.raw is response.content  # replayed verbatim on continuation


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


def test_continuation_replays_raw_content_and_returns_all_tool_results_in_one_message():
    raw = [{"type": "thinking", "thinking": ""}, {"type": "tool_use", "id": "toolu_01"}]
    previous = LLMResult(
        text="",
        tool_calls=[ToolCall("toolu_01", "send_email", {})],
        stop_reason="tool_use",
        raw=raw,
    )
    results = [ToolResult("toolu_01", "ok"), ToolResult("toolu_02", "boom", is_error=True)]
    messages = build_continuation_messages("Question ?", previous, results)

    assert [m["role"] for m in messages] == ["user", "assistant", "user"]
    assert messages[0]["content"] == "Question ?"
    assert messages[1]["content"] is raw
    blocks = messages[2]["content"]
    assert [b["tool_use_id"] for b in blocks] == ["toolu_01", "toolu_02"]
    assert blocks[0] == {
        "type": "tool_result",
        "tool_use_id": "toolu_01",
        "content": "ok",
        "is_error": False,
    }
    assert blocks[1]["is_error"] is True


def test_continuation_without_raw_content_is_refused():
    with pytest.raises(ValueError):
        build_continuation_messages("Q", LLMResult(text="x"), [])


def test_tool_definition_matches_the_messages_api_shape():
    d = tool_definition(SEND_EMAIL)
    assert set(d) == {"name", "description", "input_schema"}
    assert d["input_schema"]["required"] == ["to", "subject", "body"]
