from __future__ import annotations

from fastapi import APIRouter, Depends

from src.core.schemas import APIResponse
from src.vector_store.faiss_store import FAISSStore, get_vector_store
from src.vector_store.types import SearchRequest, SearchResult, VectorRecord, VectorStoreHealth

router = APIRouter(prefix="/v1/vector-store", tags=["vector-store"])
_vector_store_dep = Depends(get_vector_store)


@router.post("/add", response_model=APIResponse[dict[str, int]])
async def add_vectors(
    records: list[VectorRecord],
    store: FAISSStore = _vector_store_dep,
) -> APIResponse[dict[str, int]]:
    added = await store.add_vectors(records)
    return APIResponse(data={"added": added})


@router.post("/search", response_model=APIResponse[list[SearchResult]])
async def search_vectors(
    request: SearchRequest,
    store: FAISSStore = _vector_store_dep,
) -> APIResponse[list[SearchResult]]:
    results = await store.search(
        request.query_embedding,
        limit=request.limit,
        threshold=request.threshold,
    )
    return APIResponse(data=results)


@router.get("/health", response_model=APIResponse[VectorStoreHealth])
async def health(store: FAISSStore = _vector_store_dep) -> APIResponse[VectorStoreHealth]:
    return APIResponse(data=store.health())
