"""Deterministic fake embedder for tests.

It maps a text to a fixed pseudo-random unit vector seeded by the text's hash.
Same text -> same vector; different texts -> different vectors. There is no
notion of meaning, so retrieval quality cannot be tested with it, but every
database and API path can, with no model download and no network.
"""

from __future__ import annotations

import hashlib
import math
import random

from app.embeddings.base import EMBEDDING_DIM


class StubEmbedder:
    dim = EMBEDDING_DIM

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        seed = int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")
        rng = random.Random(seed)
        raw = [rng.gauss(0.0, 1.0) for _ in range(self.dim)]
        norm = math.sqrt(sum(x * x for x in raw))
        return [x / norm for x in raw]
