from __future__ import annotations

from fastapi.testclient import TestClient
from src.main import app
from src.vector_store.faiss_store import FAISSStore, get_vector_store


def build_vector(index: int, size: int = 384) -> list[float]:
    values = [0.0] * size
    values[index] = 1.0
    return values


def test_vector_store_add_search_and_health() -> None:
    store = FAISSStore(dimension=384, nlist=1)
    app.dependency_overrides[get_vector_store] = lambda: store
    try:
        with TestClient(app) as client:
            health = client.get("/v1/vector-store/health")
            assert health.status_code == 200
            assert health.json()["data"]["ready"] is False

            records = [
                {
                    "song_id": "song-a",
                    "embedding": build_vector(0),
                    "metadata": {"genre": "rock"},
                },
                {
                    "song_id": "song-b",
                    "embedding": build_vector(1),
                    "metadata": {"genre": "pop"},
                },
            ]
            add_response = client.post("/v1/vector-store/add", json=records)
            assert add_response.status_code == 200
            assert add_response.json()["data"]["added"] == 2

            search_payload = {
                "query_embedding": build_vector(0),
                "limit": 5,
                "threshold": 0.0,
            }
            search_response = client.post("/v1/vector-store/search", json=search_payload)
            assert search_response.status_code == 200
            results = search_response.json()["data"]
            assert results
            assert results[0]["song_id"] == "song-a"

            health = client.get("/v1/vector-store/health")
            assert health.status_code == 200
            assert health.json()["data"]["ready"] is True
    finally:
        app.dependency_overrides.pop(get_vector_store, None)
