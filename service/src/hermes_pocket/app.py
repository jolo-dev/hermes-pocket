from __future__ import annotations

import logging
import re
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from hermes_pocket.errors import ErrorCategory, ErrorDetail, ErrorEnvelope
from hermes_pocket.facade import FacadeState, create_facade_router
from hermes_pocket.logging import configure_logging, safe_log_fields

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
logger = logging.getLogger("hermes_pocket.requests")


def _correlation_id(request: Request) -> str:
    return str(getattr(request.state, "correlation_id", uuid4().hex))


def _error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    category: ErrorCategory,
    message: str,
    retryable: bool = False,
) -> JSONResponse:
    detail = ErrorDetail(
        code=code,
        category=category,
        message=message,
        correlation_id=_correlation_id(request),
        retryable=retryable,
    )
    return JSONResponse(status_code=status_code, content=ErrorEnvelope(error=detail).model_dump())


class CorrelationAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        supplied_id = request.headers.get("x-request-id", "")
        request_id = supplied_id if REQUEST_ID_PATTERN.fullmatch(supplied_id) else uuid4().hex
        request.state.correlation_id = request_id
        started = time.monotonic()
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        logger.info(
            "request_complete",
            extra=safe_log_fields(
                request_id=request_id,
                event="request_complete",
                method=request.method,
                route=request.url.path,
                status_code=response.status_code,
                duration_ms=round((time.monotonic() - started) * 1000),
            ),
        )
        return response


def create_app(
    *,
    configure_service_logging: bool = True,
    facade: FacadeState | None = None,
) -> FastAPI:
    if configure_service_logging:
        configure_logging()

    app = FastAPI(title="Hermes Pocket Mobile Facade", version="0.1.0")
    app.add_middleware(CorrelationAndLoggingMiddleware)
    if facade is not None:
        app.include_router(create_facade_router(facade))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, _: RequestValidationError) -> JSONResponse:
        return _error_response(
            request,
            status_code=422,
            code="REQUEST_INVALID",
            category="validation",
            message="The request does not match the API contract.",
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exception: HTTPException) -> JSONResponse:
        categories: dict[int, ErrorCategory] = {
            401: "authentication",
            403: "authorization",
            406: "compatibility",
            409: "conflict",
            429: "rate_limit",
        }
        category = categories.get(exception.status_code, "validation")
        return _error_response(
            request,
            status_code=exception.status_code,
            code=f"HTTP_{exception.status_code}",
            category=category,
            message="The request was rejected.",
        )

    @app.exception_handler(Exception)
    async def internal_error(request: Request, _: Exception) -> JSONResponse:
        correlation_id = _correlation_id(request)
        logger.exception(
            "request_failed",
            extra=safe_log_fields(
                request_id=correlation_id,
                event="request_failed",
                error_category="internal",
            ),
        )
        return _error_response(
            request,
            status_code=500,
            code="INTERNAL_ERROR",
            category="internal",
            message="The service could not complete the request.",
            retryable=True,
        )

    @app.get("/health", tags=["operations"])
    async def health(request: Request) -> dict[str, str]:
        return {"status": "ok", "correlation_id": _correlation_id(request)}

    return app


app = create_app()
