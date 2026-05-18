from __future__ import annotations

from pydantic import BaseModel, Field


class VectorRecord(BaseModel):
    song_id: str
    embedding: list[float]
    metadata: dict[str, str] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    query_embedding: list[float]
    limit: int = 10
    threshold: float = 0.7


class SearchResult(BaseModel):
    song_id: str
    score: float
    metadata: dict[str, str] = Field(default_factory=dict)


class VectorStoreHealth(BaseModel):
    ready: bool
    trained: bool
    total_vectors: int
