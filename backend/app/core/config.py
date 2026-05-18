"""
Configuration management for SignSpeak API.
Loads from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ────────────────────────────────────────────────────────────────
    # Application Metadata
    # ────────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "SignSpeak API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ────────────────────────────────────────────────────────────────
    # Security
    # ────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "your-super-secret-key-min-32-chars-change-in-production-12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days

    # ────────────────────────────────────────────────────────────────
    # PostgreSQL (Primary Database)
    # ────────────────────────────────────────────────────────────────
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "signspeak"
    POSTGRES_PORT: str = "5432"

    @property
    def DATABASE_URL(self) -> str:
        """Construct PostgreSQL connection URL."""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # ────────────────────────────────────────────────────────────────
    # MongoDB (NoSQL for Translation History & Logs)
    # ────────────────────────────────────────────────────────────────
    MONGODB_URL: str = "mongodb://mongo:27017"
    MONGODB_DB_NAME: str = "signspeak_db"

    # ────────────────────────────────────────────────────────────────
    # Redis (Cache & Task Queue)
    # ────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour default

    # ────────────────────────────────────────────────────────────────
    # Pinecone Vector Database (Phase 3: Emoji Mapping)
    # ────────────────────────────────────────────────────────────────
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-west4-gcp"
    PINECONE_INDEX_NAME: str = "emoji-concepts"
    PINECONE_DIMENSION: int = 384  # For all-MiniLM-L6-v2

    # ────────────────────────────────────────────────────────────────
    # NLP Models
    # ────────────────────────────────────────────────────────────────
    SPACY_MODEL: str = "en_core_web_trf"  # Transformer-based for better accuracy
    SBERT_MODEL: str = "all-MiniLM-L6-v2"  # Lightweight semantic search
    T5_MODEL_PATH: str = "t5-small"  # Will be fine-tuned for gloss generation
    T5_DEVICE: str = "cpu"  # Use "cuda" if GPU available

    # ────────────────────────────────────────────────────────────────
    # Celery Task Queue (Phase 5: Async Processing)
    # ────────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # ────────────────────────────────────────────────────────────────
    # API Configuration
    # ────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:3001",
    ]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  # per hour

    # ────────────────────────────────────────────────────────────────
    # Logging
    # ────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/signspeak.log"

    # ────────────────────────────────────────────────────────────────
    # AWS Configuration (for Phase 10: Deployment)
    # ────────────────────────────────────────────────────────────────
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # ────────────────────────────────────────────────────────────────
    # Pydantic Configuration
    # ────────────────────────────────────────────────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get current settings. Used as dependency injection in FastAPI."""
    return settings
