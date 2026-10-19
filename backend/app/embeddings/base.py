"""The interface every embedding provider implements."""

from __future__ import annotations

from typing import Protocol

EMBEDDING_DIM = 384  # must match vector(384) in db/schema.sql


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...
