"""
PostgreSQL Database connection and session management.
Uses SQLAlchemy with async support (asyncpg driver).
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

DEFAULT_SQLITE_URL = "sqlite+aiosqlite:///./signspeak.db"


def create_async_db_engine(database_url: str):
    """Create an async SQLAlchemy engine for the given URL."""
    connect_args = {"timeout": 10}
    if database_url.startswith("postgresql") or database_url.startswith("postgres+"):
        connect_args["command_timeout"] = 30

    return create_async_engine(
        database_url,
        echo=settings.DEBUG,
        poolclass=NullPool,
        connect_args=connect_args,
    )


def create_session_factory(engine):
    """Create an async session factory for the given engine."""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


# Create async engine for PostgreSQL by default
engine = create_async_db_engine(settings.DATABASE_URL)

# Create session factory
AsyncSessionLocal = create_session_factory(engine)

# Base class for all ORM models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency injection for database session.
    
    Usage in FastAPI endpoints:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def fallback_to_sqlite():
    """Switch to a local SQLite database when PostgreSQL is unavailable."""
    global engine, AsyncSessionLocal
    logger.warning("Falling back to local SQLite database for development.")
    engine = create_async_db_engine(DEFAULT_SQLITE_URL)
    AsyncSessionLocal = create_session_factory(engine)


async def init_db() -> bool:
    """Initialize database tables. Call this on startup."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ Database tables initialized")
        return False
    except Exception as e:
        logger.error(f"✗ Failed to initialize PostgreSQL database: {e}")
        try:
            await fallback_to_sqlite()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✓ SQLite tables initialized")
            return True
        except Exception as sqlite_error:
            logger.error(f"✗ Failed to initialize fallback SQLite database: {sqlite_error}")
            raise


async def close_db():
    """Close database connections. Call this on shutdown."""
    try:
        await engine.dispose()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Failed to close database: {e}")
        raise
