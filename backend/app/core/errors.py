"""
app/core/errors.py

Custom application exceptions and FastAPI exception handlers.

All domain errors derive from ``AppError`` which carries:
  - ``status_code`` – HTTP status to return.
  - ``error_code``  – Machine-readable string constant (upper-case).
  - ``message``     – Human-readable description.

Every error response has the shape::

    {
        "error": {
            "code": "NOT_FOUND",
            "message": "The requested resource was not found.",
            "request_id": "abc-123"
        }
    }

The ``request_id`` is pulled from the structlog context-var bound by the
request-ID middleware (``app/main.py``).
"""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_502_BAD_GATEWAY,
)

log = structlog.get_logger(__name__)


# ------------------------------------------------------------------ #
# Custom exception hierarchy
# ------------------------------------------------------------------ #


class AppError(Exception):
    """Base class for all application-level errors."""

    status_code: int = HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if error_code is not None:
            self.error_code = error_code


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"


class AppValidationError(AppError):
    """Raised for domain-level validation failures (distinct from Pydantic's)."""

    status_code = HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "VALIDATION_ERROR"


class AuthenticationError(AppError):
    """Raised when credentials are missing or invalid."""

    status_code = HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"


class AuthorizationError(AppError):
    """Raised when an authenticated user lacks permission."""

    status_code = HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_ERROR"


class RateLimitError(AppError):
    """Raised when a client exceeds an enforced rate limit."""

    status_code = HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"


class ExternalServiceError(AppError):
    """Raised when an upstream / external service call fails."""

    status_code = HTTP_502_BAD_GATEWAY
    error_code = "EXTERNAL_SERVICE_ERROR"


class ConflictError(AppError):
    """Raised when the request conflicts with existing state (e.g. duplicate)."""

    status_code = HTTP_409_CONFLICT
    error_code = "CONFLICT"


class PrivacyPolicyViolationError(AppError):
    """Raised when an operation violates external AI provider data privacy policies
    (e.g., routing organization confidential data to an unpaid/training-eligible tier).
    """

    status_code = HTTP_403_FORBIDDEN
    error_code = "PRIVACY_POLICY_VIOLATION"


# ------------------------------------------------------------------ #
# Helper – build a standard error JSON response
# ------------------------------------------------------------------ #


def _error_response(
    status_code: int,
    error_code: str,
    message: str,
    request: Request,
) -> JSONResponse:
    request_id: str = getattr(request.state, "request_id", "")
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": message,
                "request_id": request_id,
            }
        },
    )


# ------------------------------------------------------------------ #
# Exception handlers
# ------------------------------------------------------------------ #


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handler for all ``AppError`` subclasses."""
    log.warning(
        "application error",
        error_code=exc.error_code,
        message=exc.message,
        status_code=exc.status_code,
    )
    return _error_response(exc.status_code, exc.error_code, exc.message, request)


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for FastAPI / Pydantic ``RequestValidationError``."""
    # Flatten Pydantic's error list into a single message for the client
    details = "; ".join(
        f"{'.'.join(str(l) for l in e['loc'])}: {e['msg']}"
        for e in exc.errors()
    )
    log.info("request validation error", details=details)
    return _error_response(
        HTTP_422_UNPROCESSABLE_CONTENT,
        "VALIDATION_ERROR",
        f"Request validation failed: {details}",
        request,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected 500 errors."""
    log.exception("unhandled exception", exc_info=exc)
    return _error_response(
        HTTP_500_INTERNAL_SERVER_ERROR,
        "INTERNAL_ERROR",
        "An unexpected internal error occurred. Please try again later.",
        request,
    )


# ------------------------------------------------------------------ #
# Registration helper
# ------------------------------------------------------------------ #


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to *app*.

    Call this once inside ``create_app()`` in ``app/main.py``.
    """
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_error_handler)  # type: ignore[arg-type]
