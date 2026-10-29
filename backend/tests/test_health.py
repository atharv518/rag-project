"""
tests/test_health.py

Unit and integration tests for the /api/v1/health endpoint.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_health_check_healthy(client: AsyncClient, mock_db_healthy) -> None:
    """When DB is reachable, health check returns 200 OK and status 'ok'."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert "ai_provider_tier" in data

    # Verify Request ID middleware
    assert "x-request-id" in response.headers


@pytest.mark.anyio
async def test_health_check_degraded(client: AsyncClient, mock_db_unhealthy) -> None:
    """When DB is unreachable, health check returns 503 Service Unavailable and status 'degraded'."""
    response = await client.get("/api/v1/health")

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "degraded"
    assert data["database"] == "error"
    assert "x-request-id" in response.headers


@pytest.mark.anyio
async def test_root_endpoint(client: AsyncClient) -> None:
    """Root endpoint responds with service info and 200 OK."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data

