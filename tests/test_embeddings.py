from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.embeddings.model import get_embedding_model
from src.embeddings.types import SongEmbeddingRequest
from src.main import app


class DummyEmbedding:
    def __init__(self, size: int = 384) -> None:
        self._values = [0.0] * size

    def tolist(self) -> list[float]:
        return list(self._values)


class DummyEmbeddingModel:
    def generate(self, text: str) -> DummyEmbedding:
        return DummyEmbedding()


@pytest.mark.asyncio
async def test_embedding_generation() -> None:
    app.dependency_overrides[get_embedding_model] = lambda: DummyEmbeddingModel()
    try:
        request = SongEmbeddingRequest(
            song_id="test1",
            title="Test Song",
            artist="Test Artist",
        )
        with TestClient(app) as client:
            response = client.post("/v1/embeddings/generate", json=request.model_dump())
        assert response.status_code == 200
        assert len(response.json()["embedding"]) == 384
    finally:
        app.dependency_overrides.pop(get_embedding_model, None)
