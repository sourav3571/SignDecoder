
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

def create_async_db_engine(database_url: str):
    return create_async_engine(
        database_url,
        echo=False,
        poolclass=NullPool,
        connect_args={"timeout": 10},
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

async def init_db() -> bool:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✓ SQLite database tables initialized")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to initialize SQLite database: {e}")
        raise

async def close_db():

    try:
        await engine.dispose()
        logger.info("✓ Database connections closed")
    except Exception as e:
        logger.error(f"✗ Failed to close database: {e}")
        raise
