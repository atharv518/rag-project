"""
app/schemas/health.py

Pydantic schemas for the health-check API endpoints.
"""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Payload returned by GET /api/v1/health."""

    status: Literal["ok", "degraded", "down"] = Field(
        ...,
        description="Overall health status of the application.",
        examples=["ok"],
    )
    database: Literal["ok", "error"] = Field(
        ...,
        description="Connectivity state of the PostgreSQL database.",
        examples=["ok"],
    )
    version: str = Field(
        default="0.1.0",
        description="Semantic version of the running service.",
        examples=["0.1.0"],
    )
    environment: str = Field(
        ...,
        description="Current runtime environment (e.g. development, production).",
        examples=["development"],
    )
    ai_provider_tier: str = Field(
        default="free",
        description="Active AI external provider tier (free/paid).",
        examples=["free"],
    )

