from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SignSpeak API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"

    SECRET_KEY: str = "supersecretkey_please_change_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "signspeak"
    POSTGRES_PORT: str = "5432"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:

        return "sqlite+aiosqlite:///./signspeak.db"

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "signspeak_db"

    REDIS_URL: str = "redis://localhost:6379/0"

    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "emoji-concepts"

    SPACY_MODEL: str = "en_core_web_trf"
    SBERT_MODEL: str = "all-MiniLM-L6-v2"
    T5_MODEL_PATH: str = "t5-small"  

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
