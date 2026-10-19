"""HTTP API. Run with: uvicorn app.api:app --reload (from backend/)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

import psycopg
from fastapi import Depends, FastAPI, HTTPException

from app import config, db
from app.embeddings import Embedder, get_embedder
from app.llm import LLMError, LLMProvider, get_llm
from app.rag import answer_question
from app.retrieval import retrieve
from app.schemas import AskRequest, AskResponse


@dataclass
class Services:
    """Everything /ask needs. Built once per process; tests override `get_services`."""

    conn: psycopg.Connection
    embedder: Embedder
    llm: LLMProvider

    def retriever(self, question: str, k: int, role: str):
        return retrieve(self.conn, self.embedder, question, k, role)


@lru_cache(maxsize=1)
def get_services() -> Services:
    return Services(conn=db.connect(), embedder=get_embedder(), llm=get_llm())


app = FastAPI(title="loi25-rag-eval", version="0.2.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, services: Annotated[Services, Depends(get_services)]) -> AskResponse:
    try:
        return answer_question(
            body.question,
            body.role,
            retriever=services.retriever,
            llm=services.llm,
            k=config.top_k(),
        )
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
