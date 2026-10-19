"""send_email against PostgreSQL. Skips cleanly without a database."""

from app.llm.base import ToolCall
from app.tools import SENT_MESSAGE, clear_tool_calls, execute_tool, list_tool_calls

VALID = {"to": "client@energie-boreale.example", "subject": "Résumé", "body": "Bonjour"}


def test_valid_call_is_logged_and_reported_as_sent(db_conn):
    clear_tool_calls(db_conn)
    result = execute_tool(db_conn, ToolCall("toolu_1", "send_email", VALID))
    assert not result.is_error
    assert result.content == SENT_MESSAGE

    rows = list_tool_calls(db_conn)
    assert len(rows) == 1
    assert rows[0].tool == "send_email"
    assert rows[0].arguments == VALID  # jsonb round-trip keeps the accents


def test_invalid_arguments_are_still_logged(db_conn):
    clear_tool_calls(db_conn)
    result = execute_tool(db_conn, ToolCall("toolu_2", "send_email", {"to": "x@y.example"}))
    assert result.is_error
    assert "subject" in result.content and "body" in result.content
    assert len(list_tool_calls(db_conn)) == 1  # the attempt is what evals need to see


def test_clear_returns_the_count_and_newest_first_ordering(db_conn):
    clear_tool_calls(db_conn)
    execute_tool(db_conn, ToolCall("a", "send_email", {**VALID, "subject": "premier"}))
    execute_tool(db_conn, ToolCall("b", "send_email", {**VALID, "subject": "second"}))
    assert [r.arguments["subject"] for r in list_tool_calls(db_conn)] == ["second", "premier"]
    assert clear_tool_calls(db_conn) == 2
    assert list_tool_calls(db_conn) == []
