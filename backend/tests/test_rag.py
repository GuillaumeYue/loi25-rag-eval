from app.llm.base import LLMResult, ToolCall, ToolResult
from app.llm.stub import STUB_ANSWER, StubLLM
from app.prompting import REFUSAL_SENTENCE
from app.rag import (
    MAX_TOKENS_NOTICE,
    MAX_TOOL_ROUNDS,
    REFUSAL_NOTICE,
    TOOL_LIMIT_NOTICE,
    answer_question,
)
from app.retrieval import RetrievedChunk
from app.tools import BASELINE_TOOLS

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


EMAIL_CALL = ToolCall(
    "toolu_01", "send_email", {"to": "x@exemple.net", "subject": "s", "body": "b"}
)


def recording_executor():
    seen = []

    def execute(call):
        seen.append(call)
        return ToolResult(call.id, "ok")

    execute.seen = seen
    return execute


def test_tool_call_is_executed_then_the_model_finishes():
    llm = StubLLM(
        script=[
            LLMResult(
                text="Je vous envoie le résumé.",
                tool_calls=[EMAIL_CALL],
                stop_reason="tool_use",
                raw=[],
            ),
            LLMResult(text="C'est fait [1]."),
        ]
    )
    executor = recording_executor()
    resp = answer_question(
        "Envoie-moi un résumé",
        "public",
        retriever=fixed_retriever([PUBLIC]),
        llm=llm,
        k=5,
        tools=BASELINE_TOOLS,
        tool_executor=executor,
    )
    assert executor.seen == [EMAIL_CALL]
    assert llm.last_tools == BASELINE_TOOLS
    assert llm.received_tool_results == [[ToolResult("toolu_01", "ok")]]
    assert resp.answer == "Je vous envoie le résumé.\n\nC'est fait [1]."
    assert [t.model_dump() for t in resp.tool_calls] == [
        {"tool": "send_email", "arguments": EMAIL_CALL.arguments}
    ]


def test_tool_loop_stops_after_max_rounds_and_logs_every_attempt():
    always = LLMResult(text="", tool_calls=[EMAIL_CALL], stop_reason="tool_use", raw=[])
    llm = StubLLM(script=[always] * (MAX_TOOL_ROUNDS + 1))
    executor = recording_executor()
    resp = answer_question(
        "Q", "public", retriever=fixed_retriever([PUBLIC]), llm=llm, k=1, tool_executor=executor
    )
    # First call + MAX_TOOL_ROUNDS continuations, each asking for the tool: all logged.
    assert len(executor.seen) == MAX_TOOL_ROUNDS + 1
    assert len(resp.tool_calls) == MAX_TOOL_ROUNDS + 1
    assert len(llm.received_tool_results) == MAX_TOOL_ROUNDS
    assert resp.answer.endswith(TOOL_LIMIT_NOTICE)


def test_tool_call_without_executor_gets_an_error_result():
    llm = StubLLM(
        script=[LLMResult(text="", tool_calls=[EMAIL_CALL], raw=[]), LLMResult(text="Ok")]
    )
    resp = answer_question("Q", "public", retriever=fixed_retriever([PUBLIC]), llm=llm, k=1)
    assert llm.received_tool_results[0][0].is_error
    assert resp.answer == "Ok"
    assert len(resp.tool_calls) == 1
