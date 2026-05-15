from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model = None
        self.model_name = model_name

    async def warmup(self) -> None:
        """Warmup model on startup."""
        if self.model is None:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)

    def generate(self, text: str) -> np.ndarray:
        """Generate 384-dim embedding."""
        if self.model is None:
            raise ValueError("Model not warmed up")
        return self.model.encode(text)

    def generate_batch(self, texts: Iterable[str]) -> list[np.ndarray]:
        """Generate embeddings for a batch of texts."""
        if self.model is None:
            raise ValueError("Model not warmed up")
        return list(self.model.encode(list(texts)))


_embedding_model = EmbeddingModel()


def get_embedding_model() -> EmbeddingModel:
    return _embedding_model


async def warmup_embedding_model() -> None:
    await _embedding_model.warmup()
