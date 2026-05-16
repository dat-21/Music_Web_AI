from __future__ import annotations

import asyncio
import time

import numpy as np
from src.embeddings.cache import EmbeddingCache
from src.embeddings.types import SongEmbeddingRequest


class FakeRedisClient:
    def __init__(self) -> None:
        self.store: dict[str, bytes] = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value.encode()


class FakeRedisPool:
    def __init__(self) -> None:
        self.client = FakeRedisClient()


def run(coro):
    return asyncio.run(coro)


def test_cache_hit_and_miss_timing() -> None:
    cache = EmbeddingCache(FakeRedisPool())
    request = SongEmbeddingRequest(
        song_id="song-1",
        title="Cache Test",
        artist="Cache Artist",
        lyrics="Cache lyrics",
    )

    started = time.perf_counter()
    cached = run(cache.get(request))
    miss_ms = (time.perf_counter() - started) * 1000

    assert cached is None
    assert miss_ms < 500

    embedding = np.zeros(384, dtype=np.float32)
    run(cache.set(request, embedding))

    started = time.perf_counter()
    cached = run(cache.get(request))
    hit_ms = (time.perf_counter() - started) * 1000

    assert cached is not None
    assert cached.shape[0] == 384
    assert hit_ms < 10
