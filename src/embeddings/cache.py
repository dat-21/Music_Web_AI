from __future__ import annotations

import hashlib

import numpy as np

from src.core.config import settings
from src.core.redis import RedisPool
from src.embeddings.types import SongEmbeddingRequest


class EmbeddingCache:
    def __init__(self, redis_pool: RedisPool) -> None:
        self.redis = redis_pool
        self.ttl = 60 * 60 * 24 * 30

    def _make_key(self, song: SongEmbeddingRequest) -> str:
        content = f"{song.artist}:{song.title}:{song.lyrics}"
        return f"embed:{hashlib.sha256(content.encode()).hexdigest()}"

    async def get(self, song: SongEmbeddingRequest) -> np.ndarray | None:
        key = self._make_key(song)
        data = await self.redis.client.get(key)
        if data:
            return np.frombuffer(bytes.fromhex(data.decode()), dtype=np.float32)
        return None

    async def set(self, song: SongEmbeddingRequest, embedding: np.ndarray) -> None:
        key = self._make_key(song)
        await self.redis.client.setex(key, self.ttl, embedding.tobytes().hex())


_redis_pool = RedisPool(settings.redis_url)
_embedding_cache = EmbeddingCache(_redis_pool)


def get_redis_pool() -> RedisPool:
    return _redis_pool


def get_embedding_cache() -> EmbeddingCache:
    return _embedding_cache
