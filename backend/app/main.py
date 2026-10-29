"""
app/main.py

FastAPI application factory and entry point.
Includes lifespan management, CORS configuration, request correlation ID
tracking, structured error handling, and API routing.
"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.api.v1 import v1_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.db.session import check_db_connection

log = get_logger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Assigns or propagates an X-Request-ID header and binds it to contextvars."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Bind to structlog context
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown events."""
    setup_logging(settings)
    log.info(
        "application_starting",
        environment=settings.APP_ENV,
        debug=settings.APP_DEBUG,
        ai_provider_tier=settings.EXTERNAL_AI_DATA_TIER,
    )

    # Probe DB connectivity on startup
    await check_db_connection()

    yield

    log.info("application_shutdown")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(
        title="RAG Project API",
        description="Multi-tenant public, personal, and enterprise AI/RAG knowledge platform API.",
        version="0.1.0",
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url="/redoc" if settings.APP_DEBUG else None,
        lifespan=lifespan,
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.APP_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Correlation ID Middleware
    app.add_middleware(RequestIdMiddleware)

    # 3. Centralized Exception Handling
    register_exception_handlers(app)

    # 4. Route Registration
    app.include_router(v1_router, prefix="/api")

    @app.get("/", tags=["Root"])
    async def root():
        return {
            "name": "RAG Project API",
            "version": "0.1.0",
            "docs": "/docs" if settings.APP_DEBUG else None,
        }

    return app


app = create_app()

