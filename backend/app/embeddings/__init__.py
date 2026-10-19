"""Embedding provider factory, selected by EMBEDDING_PROVIDER."""

from __future__ import annotations

from app import config
from app.embeddings.base import EMBEDDING_DIM, Embedder

__all__ = ["EMBEDDING_DIM", "Embedder", "get_embedder"]


def get_embedder(name: str | None = None) -> Embedder:
    name = name or config.embedding_provider()
    if name == "stub":
        from app.embeddings.stub import StubEmbedder

        return StubEmbedder()
    if name == "fastembed":
        # Imported lazily so the stub path never loads onnxruntime.
        from app.embeddings.fastembed_provider import FastEmbedEmbedder

        return FastEmbedEmbedder()
    raise ValueError(f"unknown EMBEDDING_PROVIDER: {name!r} (expected 'stub' or 'fastembed')")
