from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.embeddings import router as embeddings_router
from src.api.v1.vector_store import router as vector_store_router
from src.core.config import settings
from src.core.exceptions import APIException, api_exception_handler, unhandled_exception_handler
from src.core.logging import structured_logger
from src.core.middleware import RequestIDMiddleware, build_cors_origins, get_request_id
from src.core.schemas import APIResponse
from src.embeddings.model import get_embedding_model, warmup_embedding_model
from src.vector_store.faiss_store import get_vector_store, set_vector_store
from src.vector_store.persistence import get_persistence


def create_app() -> FastAPI:
    structured_logger.init(settings.log_level)
    logger = logging.getLogger(settings.service_name)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        persistence = get_persistence()
        loaded_store = await persistence.load()
        set_vector_store(loaded_store)
        _.state.vector_store = loaded_store
        if os.getenv("EMBEDDINGS_SKIP_WARMUP") != "1":
            await warmup_embedding_model()
        logger.info(
            "service_startup",
            extra={
                "service": settings.service_name,
                "environment": settings.environment,
                "log_level": settings.log_level,
            },
        )
        yield
        await persistence.save(get_vector_store())

    app = FastAPI(
        title=settings.service_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=build_cors_origins(getattr(settings, "cors_origins", None)),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.include_router(embeddings_router)
    app.include_router(vector_store_router)
    app.dependency_overrides[get_embedding_model] = get_embedding_model

    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        started_at = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        request_id = request.scope.get("request_id") or get_request_id()
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "service": settings.service_name,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @app.get("/", response_model=APIResponse[dict[str, str]])
    async def root() -> APIResponse[dict[str, str]]:
        return APIResponse(
            data={"service": settings.service_name, "environment": settings.environment},
            metadata={"request_id": get_request_id()},
        )

    @app.get("/health", response_model=APIResponse[dict[str, str]])
    async def health() -> APIResponse[dict[str, str]]:
        return APIResponse(data={"status": "healthy", "service": settings.service_name})

    @app.get("/ready", response_model=APIResponse[dict[str, str]])
    async def ready() -> APIResponse[dict[str, str]]:
        return APIResponse(data={"status": "ready"})

    @app.get("/error")
    async def error() -> None:
        raise APIException("Invalid request", code=400, error_code="invalid_request")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=False)
