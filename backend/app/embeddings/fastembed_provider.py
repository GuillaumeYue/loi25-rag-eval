"""Local embeddings with fastembed (ONNX, CPU, no API key).

The model is downloaded once into `.fastembed_cache/` at the repository root.
"""

from __future__ import annotations

from fastembed import TextEmbedding

from app import config
from app.embeddings.base import EMBEDDING_DIM


class FastEmbedEmbedder:
    dim = EMBEDDING_DIM

    def __init__(self, model_name: str | None = None) -> None:
        self._model = TextEmbedding(
            model_name=model_name or config.embedding_model(),
            cache_dir=str(config.REPO_ROOT / ".fastembed_cache"),
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = [v.tolist() for v in self._model.embed(texts)]
        if vectors and len(vectors[0]) != self.dim:
            raise ValueError(
                f"model returned {len(vectors[0])} dimensions, schema expects {self.dim}"
            )
        return vectors
