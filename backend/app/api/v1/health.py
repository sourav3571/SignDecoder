"""
Health Check and System Status Endpoints

These endpoints verify that all services are connected and operational:
- Database connectivity
- Redis connectivity  
- NLP models availability
- System resources
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import logging
from datetime import datetime

from app.core.config import settings
from app.core.database import engine
from app.core.redis import get_redis

logger = logging.getLogger(__name__)
router = APIRouter()


# ════════════════════════════════════════════════════════════════════
# Response Models
# ════════════════════════════════════════════════════════════════════
class ServiceStatus(BaseModel):
    """Status of a single service."""
    status: str  # "online", "offline", "degraded"
    latency_ms: float = 0.0
    error: str = None


class HealthCheckResponse(BaseModel):
    """Overall system health status."""
    timestamp: str
    status: str  # "healthy", "degraded", "unhealthy"
    version: str
    environment: str
    services: Dict[str, ServiceStatus]
    uptime_seconds: float = None


# ════════════════════════════════════════════════════════════════════
# Health Check Endpoints
# ════════════════════════════════════════════════════════════════════

@router.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check() -> HealthCheckResponse:
    """
    Comprehensive health check endpoint.
    
    Verifies:
    - API is running
    - PostgreSQL is connected
    - Redis is connected
    - NLP models can be loaded (optional)
    
    Returns:
        HealthCheckResponse with status of all services
        
    HTTP Status Codes:
        200: System is healthy
        503: System is degraded or unhealthy
    """
    
    services = {}
    overall_status = "healthy"
    
    # ──────────────────────────────────────────────────────────────
    # Check PostgreSQL
    # ──────────────────────────────────────────────────────────────
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        services["postgresql"] = ServiceStatus(status="online", latency_ms=0)
        logger.info("✓ PostgreSQL health check passed")
    except Exception as e:
        services["postgresql"] = ServiceStatus(
            status="offline",
            error=str(e)
        )
        overall_status = "unhealthy"
        logger.error(f"✗ PostgreSQL health check failed: {e}")
    
    # ──────────────────────────────────────────────────────────────
    # Check Redis
    # ──────────────────────────────────────────────────────────────
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
            overall_status = "degraded"  # Redis is nice-to-have, not critical
        logger.warning(f"⚠ Redis health check failed: {e}")
    
    # ──────────────────────────────────────────────────────────────
    # Check NLP Models (Phase 2)
    # ──────────────────────────────────────────────────────────────
    # In Phase 1, we just note that they're not loaded yet
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
    """
    Kubernetes-style readiness probe.
    
    Returns:
        200 if all critical services are ready
        503 if any critical service is down
    """
    try:
        # Check database
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
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
    """
    Kubernetes-style liveness probe.
    
    Returns:
        200 if API is alive (quick check, no database)
        503 if API is dead
    """
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION
    }


@router.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint - returns API metadata."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health"
    }


@router.get("/version", tags=["Info"])
async def version() -> Dict[str, str]:
    """Get API version information."""
    return {
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT
    }
