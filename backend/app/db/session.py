"""
app/db/session.py

Async SQLAlchemy engine and session factory.

Pool strategy is selected automatically from the DATABASE_URL port:
  - Port 5432  (direct connection) → QueuePool (persistent connections).
  - Port 6543  (Supabase transaction pooler) → NullPool + prepared-
    statement caching disabled (pgbouncer compatibility).

Exports
-------
engine              – AsyncEngine instance (created at import time).
async_session_maker – AsyncSession factory bound to ``engine``.
get_db()            – FastAPI dependency yielding a session per request.
check_db_connection() – Startup health probe.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.core.config import settings

log = structlog.get_logger(__name__)

# ------------------------------------------------------------------ #
# Detect pool mode from DATABASE_URL
# ------------------------------------------------------------------ #

_IS_SUPABASE: bool = "supabase." in settings.DATABASE_URL
_USE_NULL_POOL: bool = ":6543" in settings.DATABASE_URL or _IS_SUPABASE

connect_args: dict[str, Any] = {}
if _IS_SUPABASE:
    connect_args["ssl"] = "require"
    connect_args["statement_cache_size"] = 0
    connect_args["prepared_statement_cache_size"] = 0

if _USE_NULL_POOL:
    # Supabase connection pooler
    engine: AsyncEngine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        connect_args=connect_args,
        echo=settings.APP_DEBUG,
    )
    log.debug("database engine created", pool="NullPool", reason="Supabase pooler detected")
else:
    # Direct local connection
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        connect_args=connect_args,
        echo=settings.APP_DEBUG,
    )
    log.debug("database engine created", pool="QueuePool", reason="local connection detected")

# ------------------------------------------------------------------ #
# Session factory
# ------------------------------------------------------------------ #

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ------------------------------------------------------------------ #
# FastAPI dependency
# ------------------------------------------------------------------ #


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an ``AsyncSession`` for the duration of a single request.

    Usage in a route::

        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


# ------------------------------------------------------------------ #
# Startup connectivity probe
# ------------------------------------------------------------------ #


async def check_db_connection() -> bool:
    """Run a lightweight query to verify the database is reachable.

    Returns ``True`` on success, ``False`` (and logs the error) on failure.
    Intended to be called during application startup and from the health
    endpoint.
    """
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        log.info("database connection check passed")
        return True
    except Exception as exc:  # noqa: BLE001
        log.error("database connection check failed", error=str(exc))
        return False
