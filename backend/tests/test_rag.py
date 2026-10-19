from app.llm.stub import STUB_ANSWER, StubLLM
from app.prompting import REFUSAL_SENTENCE
from app.rag import MAX_TOKENS_NOTICE, REFUSAL_NOTICE, answer_question
from app.retrieval import RetrievedChunk

PUBLIC = RetrievedChunk(
    1, "Article 8 fictif.", "Loi 25, article 8", "public/loi-25/art-8.md", "public", 0.9
)
INTERNE = RetrievedChunk(
    2,
    "Incident INC-2026-0117, identifiant CANARY-QC-7F3A91.",
    "Note interne",
    "internal/note-interne-incident.md",
    "interne",
    0.8,
)


def fixed_retriever(chunks):
    calls = []

    def retriever(question, k, role):
        calls.append((question, k, role))
        return chunks[:k]

    retriever.calls = calls
    return retriever


def test_response_follows_the_contract():
    llm = StubLLM()
    retriever = fixed_retriever([PUBLIC, INTERNE])
    resp = answer_question("Q ?", "public", retriever=retriever, llm=llm, k=5)

    assert resp.answer == STUB_ANSWER
    assert [s.n for s in resp.sources] == [1, 2]
    assert resp.sources[0].source == "public/loi-25/art-8.md"
    assert resp.sources[1].classification == "interne"
    assert resp.tool_calls == []
    assert retriever.calls == [("Q ?", 5, "public")]


def test_prompt_received_by_the_model_contains_the_sources():
    llm = StubLLM()
    answer_question("Q ?", "public", retriever=fixed_retriever([PUBLIC]), llm=llm, k=5)
    assert "[1] Loi 25, article 8" in llm.last_user
    assert "Article 8 fictif." in llm.last_user
    assert llm.last_tools == []


def test_baseline_leaks_internal_chunks_to_public_role():
    """Documents the baseline: no access control yet, so an interne chunk reaches a public user.

    Milestone 7 adds ENFORCE_ACCESS_CONTROL; this test pins the unmitigated behaviour."""
    llm = StubLLM()
    resp = answer_question("Q ?", "public", retriever=fixed_retriever([INTERNE]), llm=llm, k=5)
    assert resp.sources[0].classification == "interne"
    assert "CANARY-QC-7F3A91" in llm.last_user


def test_no_chunks_gives_refusal():
    resp = answer_question("Q ?", "public", retriever=fixed_retriever([]), llm=StubLLM(), k=5)
    assert resp.answer == REFUSAL_SENTENCE
    assert resp.sources == []


def test_stop_reasons_are_surfaced():
    class FixedStop:
        def __init__(self, text, stop):
            self.text, self.stop = text, stop

        def complete(self, system, user, tools):
            from app.llm.base import LLMResult

            return LLMResult(text=self.text, stop_reason=self.stop)

    r = fixed_retriever([PUBLIC])
    truncated = answer_question(
        "Q", "public", retriever=r, llm=FixedStop("Début", "max_tokens"), k=1
    )
    assert truncated.answer == "Début" + MAX_TOKENS_NOTICE
    refused = answer_question("Q", "public", retriever=r, llm=FixedStop("", "refusal"), k=1)
    assert refused.answer == REFUSAL_NOTICE
