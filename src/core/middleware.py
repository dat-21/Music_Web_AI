from __future__ import annotations

import logging
from uuid import uuid4

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from src.core.logging import request_id


class RequestIDMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.logger = logging.getLogger("ai-search")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        incoming_request_id = headers.get("X-Request-ID") or str(uuid4())
        token = request_id.set(incoming_request_id)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                mutable_headers = MutableHeaders(scope=message)
                mutable_headers["X-Request-ID"] = incoming_request_id
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id.reset(token)


def get_request_id() -> str | None:
    return request_id.get()


def build_cors_origins(raw_origins: str | None) -> list[str]:
    if not raw_origins:
        return ["http://localhost:3000", "http://127.0.0.1:3000"]
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
