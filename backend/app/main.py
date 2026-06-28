# Workaround for pyarrow/datasets initialization crash on Windows when imported after PyTorch/PEFT
try:
    import datasets
except ImportError:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys 
import nltk

try:
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
except Exception as e:
    print(f"NLTK download failed: {e}")


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

        logger.info("📦 Initializing SQLite database...")
        await init_db()
        logger.info("✓ SQLite database ready")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        sys.exit(1)

    try:

        logger.info("💾 Initializing Redis cache...")
        await init_redis()
        logger.info("✓ Redis cache ready")

    except Exception:
        logger.warning("⚠ Redis initialization skipped (continuing without cache)")

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




from app.api.routes import emoji_routes          
app.include_router(emoji_routes.router)

from app.api.routes import embeddings as embeddings_routes
app.include_router(embeddings_routes.router)

