"""
SignSpeak API - Main Application Entry Point

This is the root FastAPI application that orchestrates:
- Database connections (PostgreSQL, MongoDB, Redis)
- Middleware setup (CORS, error handling)
- Route registration (API endpoints)
- Lifespan management (startup/shutdown)

Phase 1 includes basic health checks and dependency verification.
Phase 2+ will add NLP pipeline endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

from app.core.config import settings
from app.core.database import init_db, close_db, Base
from app.core.redis import init_redis, close_redis
from app.api.v1.health import router as health_router

# ════════════════════════════════════════════════════════════════════
# Logging Setup
# ════════════════════════════════════════════════════════════════════
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════
# Lifespan Management
# ════════════════════════════════════════════════════════════════════
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    
    Startup:
      1. Initialize PostgreSQL connection and create tables
      2. Initialize Redis connection
      3. Log startup success
    
    Shutdown:
      1. Close PostgreSQL connection
      2. Close Redis connection
      3. Log shutdown
    """
    
    # ──────────────────────────────────────────────────────────────
    # STARTUP
    # ──────────────────────────────────────────────────────────────
    logger.info("═" * 60)
    logger.info("🚀 SIGNSPEAK API STARTUP")
    logger.info("═" * 60)
    
    try:
        # Initialize database
        logger.info("📦 Initializing PostgreSQL...")
        used_sqlite = await init_db()
        if used_sqlite:
            logger.warning("✓ PostgreSQL unavailable; using local SQLite fallback")
        else:
            logger.info("✓ PostgreSQL ready")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        sys.exit(1)
    
    try:
        # Initialize Redis Cache
        logger.info("💾 Initializing Redis cache...")
        await init_redis()
        logger.info("✓ Redis cache ready")
        
    except Exception as e:
        logger.error(f"⚠ Redis initialization failed (continuing without cache): {e}")
        # Don't exit, cache is optional for Phase 1
    
    logger.info("═" * 60)
    logger.info("✓ SignSpeak API is running!")
    logger.info(f"  📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"  📍 Debug: {settings.DEBUG}")
    logger.info("═" * 60)
    
    yield
    
    # ──────────────────────────────────────────────────────────────
    # SHUTDOWN
    # ──────────────────────────────────────────────────────────────
    logger.info("═" * 60)
    logger.info("🛑 SIGNSPEAK API SHUTDOWN")
    logger.info("═" * 60)
    
    try:
        await close_db()
    except Exception as e:
        logger.error(f"✗ Error closing database: {e}")
    
    try:
        await close_redis()
    except Exception as e:
        logger.warning(f"⚠ Error closing Redis: {e}")
    
    logger.info("✓ Shutdown complete")
    logger.info("═" * 60)


# ════════════════════════════════════════════════════════════════════
# FastAPI Application
# ════════════════════════════════════════════════════════════════════
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="NLP-powered sign language translation system for deaf and mute communication",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# ════════════════════════════════════════════════════════════════════
# Middleware Setup
# ════════════════════════════════════════════════════════════════════
# CORS: Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ════════════════════════════════════════════════════════════════════
# Route Registration
# ════════════════════════════════════════════════════════════════════

# Health Check Routes (Phase 1)
app.include_router(
    health_router,
    prefix="",
    tags=["Health"]
)

from app.api.routes import translate
app.include_router(translate.router, prefix=settings.API_V1_STR)
