
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os

class Settings(BaseSettings):

    PROJECT_NAME: str = "SignSpeak API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    SECRET_KEY: str = "your-super-secret-key-min-32-chars-change-in-production-12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  

    DATABASE_URL: str = "sqlite+aiosqlite:///./signspeak.db"

    MONGODB_URL: str = "mongodb://mongo:27017"
    MONGODB_DB_NAME: str = "signspeak_db"

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  

    PINECONE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-west4-gcp"
    PINECONE_INDEX_NAME: str = "emoji-concepts"
    PINECONE_DIMENSION: int = 384  

    SPACY_MODEL: str = "en_core_web_trf"  
    SBERT_MODEL: str = "all-MiniLM-L6-v2"  
    T5_MODEL_PATH: str = "t5-small"  
    T5_DEVICE: str = "cpu"  

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:3001",
    ]
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 3600  

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/signspeak.log"

    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

settings = Settings()

def get_settings() -> Settings:

    return settings
