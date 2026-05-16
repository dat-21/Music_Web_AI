from __future__ import annotations

import redis.asyncio as redis


class RedisPool:
    def __init__(self, url: str = "redis://localhost:6379") -> None:
        self.pool = redis.ConnectionPool.from_url(url)
        self.client = redis.Redis(connection_pool=self.pool)
