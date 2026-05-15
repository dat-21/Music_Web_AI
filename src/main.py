from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request, Response

from src.core.config import settings
from src.core.logging import request_id, set_request_id, structured_logger


def create_app() -> FastAPI:
    structured_logger.init(settings.log_level)
    app = FastAPI(
        title=settings.service_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    logger = logging.getLogger(settings.service_name)

    @app.middleware("http")
    async def add_request_context(request: Request, call_next):
        incoming_request_id = request.headers.get("X-Request-ID")
        current_request_id = set_request_id(incoming_request_id)
        started_at = time.perf_counter()
        response: Response | None = None

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = current_request_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            status_code = response.status_code if response is not None else 500
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id.get(),
                    "service": settings.service_name,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"service": settings.service_name, "environment": settings.environment}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy", "service": settings.service_name}

    @app.get("/ready")
    async def ready() -> dict[str, str]:
        return {"status": "ready"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=False)