from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": getattr(record, "request_id", request_id.get()),
            "service": getattr(record, "service", "ai-search"),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = request_id.get() or str(uuid4())
        if not hasattr(record, "service"):
            record.service = "ai-search"
        return True


class StructuredLogger:
    def __init__(self, service_name: str = "ai-search") -> None:
        self.service_name = service_name
        self.logger = logging.getLogger()

    def init(self, level: str = "INFO") -> None:
        log_level = getattr(logging, level.upper(), logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        handler.addFilter(RequestIdFilter())

        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(log_level)
        root_logger.addHandler(handler)

        for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()
            logger.propagate = True

        self.logger = logging.getLogger(self.service_name)

    def get_logger(self, name: str | None = None) -> logging.Logger:
        return logging.getLogger(name or self.service_name)


def set_request_id(value: str | None = None) -> str:
    current_request_id = value or str(uuid4())
    request_id.set(current_request_id)
    return current_request_id


structured_logger = StructuredLogger()