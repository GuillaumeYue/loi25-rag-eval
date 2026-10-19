import pytest
from fastapi.testclient import TestClient

from app.api import Services, app, get_services
from app.llm.base import LLMError
from app.llm.stub import STUB_ANSWER, StubLLM
from app.retrieval import RetrievedChunk

CHUNK = RetrievedChunk(1, "Texte.", "Titre", "public/doc.md", "public", 0.9)


class FakeServices(Services):
    """Same shape as Services but with no database behind the retriever."""

    def __init__(self, llm):
        self.conn = None
        self.embedder = None
        self.llm = llm

    def retriever(self, question, k, role):
        return [CHUNK]


@pytest.fixture
def client():
    app.dependency_overrides[get_services] = lambda: FakeServices(StubLLM())
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


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
