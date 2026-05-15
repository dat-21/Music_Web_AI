from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    data: DataT | None = None
    status: str = "success"
    metadata: dict[str, Any] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "data": {"message": "ok"},
                    "status": "success",
                    "metadata": {"request_id": "test-123"},
                }
            ]
        }
    )


class APIError(BaseModel):
    error: dict[str, Any] = Field(default_factory=dict)
    status: str = "error"

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "error": {"message": "Invalid request", "code": 400},
                    "status": "error",
                }
            ]
        }
    )