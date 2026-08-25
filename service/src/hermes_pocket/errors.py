from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

ErrorCategory = Literal[
    "validation",
    "authentication",
    "authorization",
    "compatibility",
    "policy",
    "conflict",
    "rate_limit",
    "backend",
    "internal",
]


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    category: ErrorCategory
    message: str
    correlation_id: str
    retryable: bool = False


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: ErrorDetail
