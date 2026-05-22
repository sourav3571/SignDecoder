
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

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("═" * 60)
    logger.info("🚀 SIGNSPEAK API STARTUP")
    logger.info("═" * 60)

    try:

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

        logger.info("💾 Initializing Redis cache...")
        await init_redis()
        logger.info("✓ Redis cache ready")

    except Exception as e:
        logger.error(f"⚠ Redis initialization failed (continuing without cache): {e}")

    logger.info("═" * 60)
    logger.info("✓ SignSpeak API is running!")
    logger.info(f"  📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"  📍 Debug: {settings.DEBUG}")
    logger.info("═" * 60)

    yield

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

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="NLP-powered sign language translation system for deaf and mute communication",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(
    health_router,
    prefix="",
    tags=["Health"]
)

from app.api.routes import translate
app.include_router(translate.router, prefix=settings.API_V1_STR)

# ── Emoji ML route ─────────────────────────────────────────────────────────
# Provides POST /api/convert-to-emoji powered by the trained GlossToEmojiModel.
# The router already carries the '/api' prefix internally.
from app.api.routes import emoji_routes          # noqa: E402
app.include_router(emoji_routes.router)
