# Task 2.2 - Redis Embedding Cache

## Status
Implemented.

## Goal
Add a Redis cache layer to reduce repeated embedding computation and track cache hit/miss metrics.

## Architecture Overview
- Redis pool: [src/core/redis.py](src/core/redis.py)
- Redis settings: [src/core/config.py](src/core/config.py)
- Cache logic: [src/embeddings/cache.py](src/embeddings/cache.py)
- Metrics: [src/embeddings/metrics.py](src/embeddings/metrics.py)
- Endpoint integration: [src/api/v1/embeddings.py](src/api/v1/embeddings.py)

## Cache Key Strategy
- Key format: embed:<sha256>
- Hash input: artist:title:lyrics
- TTL: 30 days

## Flow (Hit/Miss)
1. Endpoint calls cache.get().
2. If hit: return cached embedding, increment hit counter.
3. If miss: generate embedding, write cache, increment miss counter.
4. Cache latency recorded via histogram.

## Metrics
Counters and histogram are defined in [src/embeddings/metrics.py](src/embeddings/metrics.py):
- embedding_cache_hits_total
- embedding_cache_misses_total
- embedding_cache_latency_seconds

Note: These are in-process metrics. If you want to expose them, add a Prometheus endpoint in the web app.

## Configuration
- redis_url is read from settings in [src/core/config.py](src/core/config.py)
- Default: redis://localhost:6379

## Tests
- Cache hit/miss timing and shape checks: [tests/test_embeddings_cache.py](tests/test_embeddings_cache.py)
- Endpoint test uses dependency override for cache: [tests/test_embeddings.py](tests/test_embeddings.py)

## Local Run
```bash
poetry install
poetry run uvicorn src.main:app --reload
```

## Performance Targets
- Cache hit < 10ms
- Cache miss < 500ms
- Identical song payloads should yield cache hit

## Notes
- Cache uses float32 byte serialization to minimize storage size.
- Redis dependency is required at runtime for real cache usage.
