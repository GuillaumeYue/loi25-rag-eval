"""The /ask pipeline: retrieve -> prompt -> generate -> (tools) -> response."""

from __future__ import annotations

from collections.abc import Callable

from app.llm.base import LLMProvider, LLMResult, ToolCall, ToolResult, ToolSpec
from app.prompting import SYSTEM_PROMPT, build_user_message, excerpt
from app.retrieval import RetrievedChunk
from app.schemas import AskResponse, Source, ToolCallOut

# (question, k, role) -> chunks. A plain callable so tests can swap the database out.
Retriever = Callable[[str, int, str], list[RetrievedChunk]]
# One tool call -> its result. Executing send_email means logging it (see app.tools).
ToolExecutor = Callable[[ToolCall], ToolResult]

# How many times the model may call tools before we stop handing results back.
# Enough for "answer, then email the summary"; small enough to bound cost and loops.
MAX_TOOL_ROUNDS = 2

MAX_TOKENS_NOTICE = "\n\n[Réponse tronquée : limite de longueur atteinte.]"
TOOL_LIMIT_NOTICE = "\n\n[Limite d'appels d'outils atteinte.]"
REFUSAL_NOTICE = "Le modèle a refusé de répondre à cette demande."


def answer_question(
    question: str,
    role: str,
    *,
    retriever: Retriever,
    llm: LLMProvider,
    k: int,
    tools: list[ToolSpec] | None = None,
    tool_executor: ToolExecutor | None = None,
) -> AskResponse:
    chunks = retriever(question, k, role)
    user = build_user_message(question, chunks)
    tools = tools or []

    result = llm.complete(SYSTEM_PROMPT, user, tools)
    all_calls: list[ToolCall] = []
    answer = result.text
    for _round in range(MAX_TOOL_ROUNDS):
        if not result.tool_calls:
            break
        all_calls.extend(result.tool_calls)
        tool_results = [_execute(tool_executor, call) for call in result.tool_calls]
        result = llm.continue_after_tools(SYSTEM_PROMPT, user, result, tool_results, tools)
        answer = _join(answer, result.text)
    else:
        if result.tool_calls:
            # The model still wants tools after the last round: log them, do not loop again.
            all_calls.extend(result.tool_calls)
            for call in result.tool_calls:
                _execute(tool_executor, call)
            answer += TOOL_LIMIT_NOTICE

    answer = _apply_stop_reason(answer, result)
    sources = [
        Source(
            n=n,
            title=c.title,
            source=c.source,
            classification=c.classification,
            excerpt=excerpt(c),
        )
        for n, c in enumerate(chunks, start=1)
    ]
    tool_calls = [ToolCallOut(tool=t.name, arguments=t.arguments) for t in all_calls]
    return AskResponse(answer=answer, sources=sources, tool_calls=tool_calls)


def _execute(executor: ToolExecutor | None, call: ToolCall) -> ToolResult:
    if executor is None:
        return ToolResult(call.id, "Aucun outil n'est disponible.", is_error=True)
    return executor(call)


def _join(before: str, after: str) -> str:
    """Text the model wrote before calling the tool, then what it wrote after."""
    if before and after:
        return f"{before}\n\n{after}"
    return before or after


def _apply_stop_reason(answer: str, result: LLMResult) -> str:
    if result.stop_reason == "max_tokens":
        return answer + MAX_TOKENS_NOTICE
    if result.stop_reason == "refusal" and not answer:
        return REFUSAL_NOTICE
    return answer
