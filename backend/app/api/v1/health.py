
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import logging
from datetime import datetime

from app.core.config import settings
from app.core.database import engine
from app.core.redis import get_redis
from sqlalchemy import text

logger = logging.getLogger(__name__)
# FastAPI 0.110+ removed the legacy on_startup/on_shutdown params.
# No lifecycle callbacks are needed for the health router, so we instantiate it plainly.
router = APIRouter()

class ServiceStatus(BaseModel):

    status: str  
    latency_ms: float = 0.0
    error: str = None

class HealthCheckResponse(BaseModel):

    timestamp: str
    status: str  
    version: str
    environment: str
    services: Dict[str, ServiceStatus]
    uptime_seconds: float = None

@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check() -> HealthCheckResponse:

    services = {}
    overall_status = "healthy"

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        services["sqlite"] = ServiceStatus(status="online", latency_ms=0)
        logger.info("✓ SQLite health check passed")
    except Exception as e:
        services["sqlite"] = ServiceStatus(
            status="offline",
            error=str(e)
        )
        overall_status = "unhealthy"
        logger.error(f"✗ SQLite health check failed: {e}")

    try:
        redis_client = await get_redis()
        await redis_client.ping()
        services["redis"] = ServiceStatus(status="online", latency_ms=0)
        logger.info("✓ Redis health check passed")
    except Exception as e:
        services["redis"] = ServiceStatus(
            status="offline",
            error=str(e)
        )
        if overall_status == "healthy":
            overall_status = "degraded"  
        logger.warning(f"⚠ Redis health check failed: {e}")

    services["nlp_models"] = ServiceStatus(
        status="not_initialized",
        error="NLP models will be loaded in Phase 2"
    )

    return HealthCheckResponse(
        timestamp=datetime.utcnow().isoformat(),
        status=overall_status,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        services=services,
    )

@router.get("/health/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:

    try:

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.get("/health/live", tags=["Health"])
async def liveness_check() -> Dict[str, Any]:

    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }

@router.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:

    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health"
    }

@router.get("/version", tags=["Info"])
async def version() -> Dict[str, str]:

    return {
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }
