"""send_email without a database: schema, unknown tools, and the no-mail rule."""

from pathlib import Path

from app.llm.base import ToolCall
from app.tools import BASELINE_TOOLS, SEND_EMAIL, execute_tool

APP_DIR = Path(__file__).resolve().parents[1] / "app"


def test_send_email_schema_requires_the_three_fields():
    schema = SEND_EMAIL.input_schema
    assert set(schema["properties"]) == {"to", "subject", "body"}
    assert schema["required"] == ["to", "subject", "body"]
    assert schema["additionalProperties"] is False
    assert BASELINE_TOOLS == [SEND_EMAIL]


def test_unknown_tool_is_an_error_and_never_touches_the_database():
    class ExplodingConn:
        def cursor(self):
            raise AssertionError("unknown tools must not be logged")

    result = execute_tool(ExplodingConn(), ToolCall("t1", "delete_everything", {}))
    assert result.is_error
    assert result.call_id == "t1"
    assert "delete_everything" in result.content


def test_no_mail_library_anywhere_in_the_app():
    """CLAUDE.md: send_email must never send anything. Keep every mail API out of the package."""
    forbidden = ("smtplib", "sendmail", "aiosmtplib", "sendgrid", "mailgun", "boto3")
    for path in APP_DIR.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for word in forbidden:
            assert word not in text, f"{path.name} mentions {word}"
