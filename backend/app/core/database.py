
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

    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

engine = create_async_db_engine(settings.DATABASE_URL)

AsyncSessionLocal = create_session_factory(engine)

Base = declarative_base()

async def get_db() -> AsyncSession:

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

    global engine, AsyncSessionLocal
    logger.warning("Falling back to local SQLite database for development.")
    engine = create_async_db_engine(DEFAULT_SQLITE_URL)
    AsyncSessionLocal = create_session_factory(engine)

async def init_db() -> bool:

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

    try:
        await engine.dispose()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Failed to close database: {e}")
        raise
