# Task 3.1 - FAISS Vector Store Integration

## Status

Planned (not implemented in codebase yet).

## Goal

Introduce a FAISS-based vector store with HNSW + IVF-PQ to enable billion-scale vector search with low latency.

## Planned Components

- Vector record schema (song_id, embedding, metadata)
- Search request schema (query_embedding, limit, threshold)
- FAISS store class with:
  - Index build (HNSW + IVF-PQ)
  - Add vectors
  - Search with cosine similarity
- API endpoints:
  - POST /v1/vector-store/add
  - POST /v1/vector-store/search
  - GET /v1/vector-store/health

## Performance Targets

- Index 1M vectors < 5 minutes
- Search < 50ms p95
- Recall@10 > 0.85

## Test Plan

- Index build and search accuracy tests
- Load test with 100k vectors
- Health endpoint validation

## Dependencies

- faiss-cpu 1.7.4 (or faiss-gpu for production)

## Notes

- Design should use float32 embeddings and store metadata separately.
- Consider sharding or IVF tuning parameters for large-scale workloads.
