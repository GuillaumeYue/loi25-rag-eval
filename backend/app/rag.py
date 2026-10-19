"""The /ask pipeline: retrieve -> prompt -> generate -> response."""

from __future__ import annotations

from collections.abc import Callable

from app.llm.base import LLMProvider, ToolSpec
from app.prompting import SYSTEM_PROMPT, build_user_message, excerpt
from app.retrieval import RetrievedChunk
from app.schemas import AskResponse, Source, ToolCallOut

# (question, k, role) -> chunks. A plain callable so tests can swap the database out.
Retriever = Callable[[str, int, str], list[RetrievedChunk]]

MAX_TOKENS_NOTICE = "\n\n[Réponse tronquée : limite de longueur atteinte.]"
REFUSAL_NOTICE = "Le modèle a refusé de répondre à cette demande."


def answer_question(
    question: str,
    role: str,
    *,
    retriever: Retriever,
    llm: LLMProvider,
    k: int,
    tools: list[ToolSpec] | None = None,
) -> AskResponse:
    chunks = retriever(question, k, role)
    result = llm.complete(SYSTEM_PROMPT, build_user_message(question, chunks), tools or [])

    answer = result.text
    if result.stop_reason == "max_tokens":
        answer += MAX_TOKENS_NOTICE
    elif result.stop_reason == "refusal" and not answer:
        answer = REFUSAL_NOTICE

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
    tool_calls = [ToolCallOut(tool=t.name, arguments=t.arguments) for t in result.tool_calls]
    return AskResponse(answer=answer, sources=sources, tool_calls=tool_calls)
