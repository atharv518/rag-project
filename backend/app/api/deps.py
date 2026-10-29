"""
app/api/deps.py

Shared FastAPI dependency providers.
Includes database session dependency, future authentication dependencies,
and tenant context helpers.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous database session for a single request lifecycle."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

