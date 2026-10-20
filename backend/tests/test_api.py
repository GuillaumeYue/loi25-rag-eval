from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app.api import Services, app, get_services
from app.llm.base import LLMError
from app.llm.stub import STUB_ANSWER, StubLLM
from app.retrieval import RetrievedChunk
from app.tools import ToolCallRecord

CHUNK = RetrievedChunk(1, "Texte.", "Titre", "public/doc.md", "public", 0.9)


class FakeServices(Services):
    """Same shape as Services but with no database behind the retriever."""

    def __init__(self, llm):
        self.conn = None
        self.embedder = None
        self.llm = llm

        self.outbox = [
            ToolCallRecord(2, "send_email", {"to": "b@x.example"}, datetime(2026, 10, 19, 12, 0)),
            ToolCallRecord(1, "send_email", {"to": "a@x.example"}, datetime(2026, 10, 19, 11, 0)),
        ]

    def retriever(self, question, k, role, *, enforce_access_control=False):
        self.last_enforce = enforce_access_control
        return [CHUNK]

    def execute_tool(self, call):
        raise AssertionError("the stub never calls tools")

    def list_tool_calls(self):
        return self.outbox

    def clear_tool_calls(self):
        n = len(self.outbox)
        self.outbox = []
        return n


@pytest.fixture
def client():
    services = FakeServices(
        StubLLM()
    )  # one instance, so state (the outbox) persists across requests
    app.dependency_overrides[get_services] = lambda: services
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_reports_the_configuration_under_test(client, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "stub")
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["llm_provider"] == "stub"
    assert body["model"] is None  # only meaningful for the anthropic provider
    assert body["embedding_provider"] == "stub"
    assert body["top_k"] == 5
    assert body["flags"] == {
        "ENFORCE_ACCESS_CONTROL": False,
        "ISOLATE_CONTEXT": False,
        "TOOL_GUARD": False,
        "OUTPUT_FILTER": False,
    }

    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-haiku-5-5")
    assert client.get("/health").json()["model"] == "claude-haiku-5-5"


def test_ask_returns_the_contract(client):
    r = client.post("/ask", json={"question": "Quel délai ?", "role": "public"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == STUB_ANSWER
    assert body["sources"] == [
        {
            "n": 1,
            "title": "Titre",
            "source": "public/doc.md",
            "classification": "public",
            "excerpt": "Texte.",
        }
    ]
    assert body["tool_calls"] == []
    assert body["blocked_tool_calls"] == []
    assert body["output_filtered"] is False


def test_role_defaults_to_public(client):
    assert client.post("/ask", json={"question": "Q ?"}).status_code == 200


@pytest.mark.parametrize(
    "payload",
    [{}, {"question": ""}, {"question": "Q", "role": "admin"}, {"role": "public"}],
)
def test_invalid_requests_are_rejected(client, payload):
    assert client.post("/ask", json=payload).status_code == 422


def test_llm_failure_becomes_502():
    class Broken:
        def complete(self, system, user, tools):
            raise LLMError("quota exceeded")

    app.dependency_overrides[get_services] = lambda: FakeServices(Broken())
    try:
        r = TestClient(app).post("/ask", json={"question": "Q"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 502
    assert "quota exceeded" in r.json()["detail"]


def test_tool_calls_outbox_newest_first(client):
    r = client.get("/tool-calls")
    assert r.status_code == 200
    body = r.json()
    assert [row["id"] for row in body] == [2, 1]
    assert body[0]["tool"] == "send_email"
    assert body[0]["arguments"] == {"to": "b@x.example"}
    assert body[0]["created_at"].startswith("2026-10-19T12:00:00")


def test_clearing_the_outbox(client):
    assert client.delete("/tool-calls").json() == {"deleted": 2}
    assert client.get("/tool-calls").json() == []


def test_flags_reach_the_retriever_and_health(monkeypatch):
    services = FakeServices(StubLLM())
    app.dependency_overrides[get_services] = lambda: services
    try:
        monkeypatch.setenv("ENFORCE_ACCESS_CONTROL", "1")
        monkeypatch.setenv("OUTPUT_FILTER", "true")
        c = TestClient(app)
        assert c.post("/ask", json={"question": "Q"}).status_code == 200
        assert services.last_enforce is True
        flags = c.get("/health").json()["flags"]
        assert flags["ENFORCE_ACCESS_CONTROL"] is True
        assert flags["OUTPUT_FILTER"] is True
        assert flags["ISOLATE_CONTEXT"] is False
    finally:
        app.dependency_overrides.clear()
