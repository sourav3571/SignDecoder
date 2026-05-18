from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SignSpeak API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"
    
    # Security
    SECRET_KEY: str = "supersecretkey_please_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Relational Database (PostgreSQL)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "signspeak"
    POSTGRES_PORT: str = "5432"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # Use aiosqlite for local dev without needing PostgreSQL installed
        return "sqlite+aiosqlite:///./signspeak.db"
        
    # NoSQL Database (MongoDB)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "signspeak_db"
    
    # Caching (Redis)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Pinecone Vector DB
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "emoji-concepts"
    
    # ML Models
    SPACY_MODEL: str = "en_core_web_trf"
    SBERT_MODEL: str = "all-MiniLM-L6-v2"
    T5_MODEL_PATH: str = "t5-small"  # Will be replaced with local fine-tuned model path

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
