from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.schemas import APIError


class APIException(Exception):
    def __init__(
        self,
        message: str,
        code: int = 400,
        *,
        error_code: str | None = None,
        metadata: dict[str, Any] | None = None,
        details: Any | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.error_code = error_code
        self.metadata = metadata
        self.details = details
        super().__init__(message)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    error_payload: dict[str, Any] = {
        "message": exc.message,
        "code": exc.code,
    }

    if exc.error_code is not None:
        error_payload["error_code"] = exc.error_code

    if exc.metadata is not None:
        error_payload["metadata"] = exc.metadata

    if exc.details is not None:
        error_payload["details"] = exc.details

    body = APIError(error=error_payload)
    return JSONResponse(status_code=exc.code, content=body.model_dump())


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger("ai-search").exception(
        "unhandled_exception",
        extra={"path": request.url.path, "method": request.method},
    )
    body = APIError(error={"message": "Internal server error", "code": 500})
    return JSONResponse(status_code=500, content=body.model_dump())


ExceptionHandler = Callable[[Request, Exception], JSONResponse]