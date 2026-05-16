# Task 2.1 - Song Embedding Model Integration

## Status
Implemented.

## Goal
Provide a stable embedding pipeline that accepts song metadata and returns a 384-dim vector using a SentenceTransformers model. Support startup warmup and batch-ready generation.

## Architecture Overview
- Embedding model wrapper: [src/embeddings/model.py](src/embeddings/model.py)
- Request/response schemas: [src/embeddings/types.py](src/embeddings/types.py)
- API endpoint: [src/api/v1/embeddings.py](src/api/v1/embeddings.py)
- App wiring and warmup: [src/main.py](src/main.py)

## Data Flow
1. Client POSTs to /v1/embeddings/generate.
2. Request is validated into SongEmbeddingRequest.
3. Text is composed as "artist - title lyrics".
4. EmbeddingModel.generate() returns a 384-dim vector.
5. Response returns embedding list with model_version.

## Warmup Behavior
- Warmup is executed at app startup via FastAPI lifespan.
- Set EMBEDDINGS_SKIP_WARMUP=1 to skip model warmup (useful for tests or CI).

## Batch Support
- generate_batch() is available for batch-ready usage in [src/embeddings/model.py](src/embeddings/model.py).

## API Contract
### POST /v1/embeddings/generate
Request JSON:
```json
{
  "song_id": "song-1",
  "title": "My Song",
  "artist": "My Artist",
  "lyrics": "...",
  "metadata": {}
}
```

Response JSON:
```json
{
  "song_id": "song-1",
  "embedding": [0.01, 0.02, ...],
  "model_version": "v1"
}
```

## Dependencies
- sentence-transformers, numpy, torch in [pyproject.toml](pyproject.toml)

## Tests
- Basic endpoint test and output shape: [tests/test_embeddings.py](tests/test_embeddings.py)

## Local Run
```bash
poetry install
poetry run uvicorn src.main:app --reload
```

## Quick Check
```bash
poetry run pytest
```

## Curl Example
```bash
curl -X POST http://localhost:8000/v1/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{"song_id":"s1","title":"Test Song","artist":"Test Artist","lyrics":"","metadata":{}}'
```

## Performance Targets
- Single embedding < 500ms
- Warmup < 5s
- Batch path available via generate_batch()

## Notes
- The model is initialized lazily on warmup to avoid import overhead in tests.
