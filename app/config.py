from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    DEBUG: bool = False
    APP_NAME: str = "ChopperCare"

    # Groq
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # PostgreSQL
    DATABASE_URL: str  # postgresql://user:pass@localhost:5432/dbname

    # CORS — frontend URL
    ALLOWED_ORIGINS: List[str] = [
        "https://choppercare.toeanmuda.id",
        "http://localhost:3001",  # dev
    ]

    # RAG
    EMBED_MODEL: str = "nomic-ai/nomic-embed-text-v1"
    TOP_K_RESULTS: int = 5
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # Rate limiting
    RATE_LIMIT: str = "30/minute"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()