from __future__ import annotations

from fastapi import APIRouter, Depends

from src.embeddings.model import EmbeddingModel, get_embedding_model
from src.embeddings.types import EmbeddingResponse, SongEmbeddingRequest

router = APIRouter(prefix="/v1/embeddings", tags=["embeddings"])


@router.post("/generate", response_model=EmbeddingResponse)
async def generate_embedding(
    request: SongEmbeddingRequest,
    model: EmbeddingModel = Depends(get_embedding_model),
) -> EmbeddingResponse:
    text = f"{request.artist} - {request.title} {request.lyrics}".strip()
    embedding = model.generate(text)
    return EmbeddingResponse(song_id=request.song_id, embedding=embedding.tolist())
