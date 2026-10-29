"""
app/api/v1/health.py

Health check and diagnostic endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.session import check_db_connection
from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Application & Database Health Probe",
    description="Probes API readiness and PostgreSQL connectivity.",
)
async def health_check() -> JSONResponse:
    """Perform health checks on backend services."""
    is_db_connected = await check_db_connection()

    app_status = "ok" if is_db_connected else "degraded"
    db_status = "ok" if is_db_connected else "error"
    http_code = (
        status.HTTP_200_OK if is_db_connected else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    content = {
        "status": app_status,
        "database": db_status,
        "version": "0.1.0",
        "environment": settings.APP_ENV,
        "ai_provider_tier": settings.EXTERNAL_AI_DATA_TIER,
    }

    return JSONResponse(status_code=http_code, content=content)

