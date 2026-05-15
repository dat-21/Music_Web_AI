# AI Search Service

[![CI Pipeline](https://github.com/your-org/ai-search-service/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/ai-search-service/actions/workflows/ci.yml)

Semantic search microservice for the music platform, built with FastAPI, Poetry, structured JSON logging, correlation IDs, standardized error handling, Docker, and GitHub Actions.

## Quick Start

```bash
cp .env.example .env
poetry install
poetry run uvicorn src.main:app --reload
```

## Local Development

```bash
make dev-up
```

Expected output:

```text
Uvicorn running on http://0.0.0.0:8000
Application startup complete.
```

## Testing

```bash
make test
pytest tests/ -v
pytest --cov=src tests/
```

Expected output:

```text
All tests pass
```

## Linting

```bash
make lint
```

## Docker

Build:

```bash
docker build -t ai-search:latest .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env ai-search:latest
```

Compose:

```bash
docker-compose up --build
```

Expected output:

```text
Service healthy
```

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | / | Service metadata |
| GET | /health | Health check |
| GET | /ready | Readiness check |
| GET | /error | Demo standardized error response |

## Curl Examples

```bash
curl -H "X-Request-ID: test-123" http://localhost:8000/health
```

Expected output:

Headers:

```text
X-Request-ID: test-123
```

Body:

```json
{"data":{"status":"healthy","service":"ai-search"},"status":"success","metadata":null}
```

```bash
curl http://localhost:8000/error
```

Expected output:

```json
{"error":{"message":"Invalid request","code":400,"error_code":"invalid_request"},"status":"error"}
```

## Environment Variables

See [.env.example](.env.example).

## Docker Optimization Notes

The Docker image uses a multi-stage build, Poetry export for runtime-only dependencies, a non-root user, a healthcheck, and minimal OS packages to keep the runtime image smaller and safer.

## CI/CD Notes

The GitHub Actions pipeline installs Poetry, caches dependencies, runs Ruff, Pytest with coverage, a Docker build smoke test, and a Bandit security scan.
