"""HTTP API. Run with: uvicorn app.api:app --reload (from backend/)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, HTTPException

from app import config, db, tools
from app.embeddings import Embedder, get_embedder
from app.llm import LLMError, LLMProvider, ToolCall, ToolResult, get_llm
from app.rag import answer_question
from app.retrieval import retrieve
from app.schemas import AskRequest, AskResponse, ToolCallRecordOut


@dataclass
class Services:
    """Everything the endpoints need. Built once per process; tests override `get_services`."""

    conn: psycopg.Connection
    embedder: Embedder
    llm: LLMProvider

    def retriever(self, question: str, k: int, role: str):
        return retrieve(self.conn, self.embedder, question, k, role)

    def execute_tool(self, call: ToolCall) -> ToolResult:
        return tools.execute_tool(self.conn, call)

    def list_tool_calls(self) -> list[tools.ToolCallRecord]:
        return tools.list_tool_calls(self.conn)

    def clear_tool_calls(self) -> int:
        return tools.clear_tool_calls(self.conn)


@lru_cache(maxsize=1)
def get_services() -> Services:
    return Services(conn=db.connect(), embedder=get_embedder(), llm=get_llm())


ServicesDep = Annotated[Services, Depends(get_services)]

app = FastAPI(title="loi25-rag-eval", version="0.3.0")


@app.get("/health")
def health() -> dict[str, object]:
    """Liveness plus the configuration under test, so eval reports can record it."""
    return {
        "status": "ok",
        "llm_provider": config.llm_provider(),
        "model": config.anthropic_model() if config.llm_provider() == "anthropic" else None,
        "embedding_provider": config.embedding_provider(),
        "top_k": config.top_k(),
        # Mitigation flags arrive in milestone 7; an empty dict means "baseline".
        "flags": {},
    }


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, services: ServicesDep) -> AskResponse:
    try:
        return answer_question(
            body.question,
            body.role,
            retriever=services.retriever,
            llm=services.llm,
            k=config.top_k(),
            tools=tools.BASELINE_TOOLS,
            tool_executor=services.execute_tool,
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/tool-calls", response_model=list[ToolCallRecordOut])
def tool_calls(services: ServicesDep) -> list[ToolCallRecordOut]:
    """The mock outbox, newest first. Nothing listed here was ever sent."""
    return [
        ToolCallRecordOut(id=r.id, tool=r.tool, arguments=r.arguments, created_at=r.created_at)
        for r in services.list_tool_calls()
    ]


@app.delete("/tool-calls")
def clear_tool_calls(services: ServicesDep) -> dict[str, int]:
    """Empty the mock outbox, so an eval run starts clean."""
    return {"deleted": services.clear_tool_calls()}
