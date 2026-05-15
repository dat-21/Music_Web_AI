from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class SongEmbeddingRequest(BaseModel):
    song_id: str
    title: str
    artist: str
    lyrics: str = ""
    metadata: dict = Field(default_factory=dict)


class EmbeddingResponse(BaseModel):
    song_id: str
    embedding: List[float]
    model_version: str = "v1"
