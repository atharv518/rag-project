"""
tests/conftest.py

Shared pytest fixtures for the backend test suite.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Set testing environment variables before importing app
os.environ["APP_ENV"] = "testing"
os.environ["APP_DEBUG"] = "false"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-must-be-at-least-32-characters-long"
os.environ["EXTERNAL_AI_DATA_TIER"] = "free"
os.environ["ALLOW_ORG_DATA_ON_FREE_TIER"] = "false"

from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous HTTP test client bound to the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_db_healthy():
    """Mock database connectivity as healthy."""
    with patch("app.api.v1.health.check_db_connection", new_callable=AsyncMock) as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_db_unhealthy():
    """Mock database connectivity as failing."""
    with patch("app.api.v1.health.check_db_connection", new_callable=AsyncMock) as mock:
        mock.return_value = False
        yield mock

