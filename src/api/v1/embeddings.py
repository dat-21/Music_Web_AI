from __future__ import annotations

import time

from fastapi import APIRouter, Depends

from src.embeddings.cache import EmbeddingCache, get_embedding_cache
from src.embeddings.metrics import EMBED_CACHE_HITS, EMBED_CACHE_LATENCY, EMBED_CACHE_MISSES
from src.embeddings.model import EmbeddingModel, get_embedding_model
from src.embeddings.types import EmbeddingResponse, SongEmbeddingRequest

router = APIRouter(prefix="/v1/embeddings", tags=["embeddings"])
_embedding_model_dep = Depends(get_embedding_model)
_embedding_cache_dep = Depends(get_embedding_cache)


@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(
    request: SongEmbeddingRequest,
    cache: EmbeddingCache = _embedding_cache_dep,
    model: EmbeddingModel = _embedding_model_dep,
) -> EmbeddingResponse:
    started = time.perf_counter()
    cached = await cache.get(request)
    EMBED_CACHE_LATENCY.observe(time.perf_counter() - started)
    if cached is not None:
        EMBED_CACHE_HITS.inc()
        return EmbeddingResponse(song_id=request.song_id, embedding=cached.tolist())

    EMBED_CACHE_MISSES.inc()
    text = f"{request.artist} - {request.title} {request.lyrics}".strip()
    embedding = model.generate(text)
    await cache.set(request, embedding)
    return EmbeddingResponse(song_id=request.song_id, embedding=embedding.tolist())
