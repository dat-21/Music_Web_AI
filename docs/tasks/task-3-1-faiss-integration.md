# Task 3.1 - FAISS Vector Store Integration

## Status

Implemented.

## Goal

Introduce a FAISS-based vector store with HNSW + IVF-PQ to enable fast vector search with cosine similarity.

## Architecture Overview

- FAISS store: [src/vector_store/faiss_store.py](src/vector_store/faiss_store.py)
- Vector schemas: [src/vector_store/types.py](src/vector_store/types.py)
- API endpoints: [src/api/v1/vector_store.py](src/api/v1/vector_store.py)
- Router wiring: [src/main.py](src/main.py)

## Index Design

- Quantizer: HNSW
- Main index: IVF-PQ
- Similarity: cosine via L2-normalization + inner product
- Training: random float32 vectors at index build time

## API Endpoints

### POST /v1/vector-store/add

Body (list of VectorRecord):

```json
[
  {
    "song_id": "song-a",
    "embedding": [0.1, 0.2, ...],
    "metadata": {"genre": "rock"}
  }
]
```

Response:

```json
{
  "data": {"added": 1},
  "status": "success",
  "metadata": null
}
```

### POST /v1/vector-store/search

Body:

```json
{
  "query_embedding": [0.1, 0.2, ...],
  "limit": 10,
  "threshold": 0.7
}
```

Response:

```json
{
  "data": [
    {"song_id": "song-a", "score": 0.93, "metadata": {"genre": "rock"}}
  ],
  "status": "success",
  "metadata": null
}
```

### GET /v1/vector-store/health

Response:

```json
{
  "data": {"ready": true, "trained": true, "total_vectors": 100},
  "status": "success",
  "metadata": null
}
```

## Tests

- Add/search/health test: [tests/test_vector_store.py](tests/test_vector_store.py)

## Dependencies

- faiss-cpu 1.7.4 in [pyproject.toml](pyproject.toml)

## Performance Targets

- Index 1M vectors < 5 minutes
- Search < 50ms p95
- Recall@10 > 0.85

## Notes

- Embeddings are normalized before add/search to enable cosine similarity.
- Metadata is stored in memory alongside FAISS ids.
