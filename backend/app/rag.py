"""The /ask pipeline: retrieve -> prompt -> generate -> (tools) -> response."""

from __future__ import annotations

from collections.abc import Callable

from app import guards
from app.config import Flags
from app.llm.base import LLMProvider, LLMResult, ToolCall, ToolResult, ToolSpec
from app.prompting import build_user_message, excerpt, system_prompt
from app.retrieval import RetrievedChunk
from app.schemas import AskResponse, BlockedToolCallOut, Source, ToolCallOut

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
    flags: Flags | None = None,
    allowed_domains: list[str] | None = None,
) -> AskResponse:
    """Run one question through the pipeline.

    Access control (ENFORCE_ACCESS_CONTROL) lives in the retriever; the other
    three flags act here: ISOLATE_CONTEXT picks the prompts, TOOL_GUARD vets
    each tool call before it runs, OUTPUT_FILTER vets the final answer.
    """
    flags = flags or Flags()
    chunks = retriever(question, k, role)
    internal_chunks = [c for c in chunks if c.classification == "interne"]
    public_chunks = [c for c in chunks if c.classification != "interne"]
    system = system_prompt(flags.isolate_context)
    user = build_user_message(question, chunks, isolate=flags.isolate_context)
    tools = tools or []

    executed: list[ToolCall] = []
    blocked: list[BlockedToolCallOut] = []

    def run(call: ToolCall) -> ToolResult:
        if flags.tool_guard:
            reason = guards.check_tool_call(
                call, question, internal_chunks, allowed_domains or [], public_chunks
            )
            if reason:
                blocked.append(
                    BlockedToolCallOut(tool=call.name, arguments=call.arguments, reason=reason)
                )
                return ToolResult(
                    call.id, f"Appel refusé par la politique d'outils : {reason}", is_error=True
                )
        executed.append(call)
        return _execute(tool_executor, call)

    result = llm.complete(system, user, tools)
    answer = result.text
    for _round in range(MAX_TOOL_ROUNDS):
        if not result.tool_calls:
            break
        tool_results = [run(call) for call in result.tool_calls]
        result = llm.continue_after_tools(system, user, result, tool_results, tools)
        answer = _join(answer, result.text)
    else:
        if result.tool_calls:
            # The model still wants tools after the last round: run (or block) and
            # log them, but do not hand results back again.
            for call in result.tool_calls:
                run(call)
            answer += TOOL_LIMIT_NOTICE

    answer = _apply_stop_reason(answer, result)
    output_filtered = flags.output_filter and guards.should_filter(
        answer, role, internal_chunks, public_chunks
    )
    if output_filtered:
        answer = guards.FILTERED_ANSWER
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
    tool_calls = [ToolCallOut(tool=t.name, arguments=t.arguments) for t in executed]
    return AskResponse(
        answer=answer,
        sources=sources,
        tool_calls=tool_calls,
        blocked_tool_calls=blocked,
        output_filtered=output_filtered,
    )


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
