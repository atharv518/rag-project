"""
app/core/config.py

Centralised application configuration using pydantic-settings.
All environment variables are declared here with types, defaults, and
descriptions. A module-level singleton ``settings`` is exposed so every
other module can simply do ``from app.core.config import settings``.
"""

from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    # ------------------------------------------------------------------ #
    # Supabase
    # ------------------------------------------------------------------ #
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""

    # ------------------------------------------------------------------ #
    # Storage
    # ------------------------------------------------------------------ #
    STORAGE_BACKEND: str = "local"
    STORAGE_BUCKET_DOCUMENTS: str = "ragproject-documents"
    STORAGE_SIGNED_URL_EXPIRY_SECONDS: int = 900

    # ------------------------------------------------------------------ #
    # Gemini / LLM
    # ------------------------------------------------------------------ #
    GEMINI_API_KEY: str = ""
    GEMINI_LLM_MODEL: str = "gemini-2.0-flash"
    LLM_REQUEST_TIMEOUT_SECONDS: int = 30
    LLM_MAX_RETRIES: int = 3

    # ------------------------------------------------------------------ #
    # Embeddings
    # ------------------------------------------------------------------ #
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-001"
    EMBEDDING_DIMENSIONS: int = 768
    EMBEDDING_PROVIDER: str = "gemini"
    EMBEDDING_REQUEST_TIMEOUT_SECONDS: int = 20

    # ------------------------------------------------------------------ #
    # Privacy Gate & AI Provider Data Governance
    # ------------------------------------------------------------------ #
    EXTERNAL_AI_DATA_TIER: str = "free"  # "free" (unpaid/training eligible) | "paid" (contractual non-training)
    ALLOW_ORG_DATA_ON_FREE_TIER: bool = False  # NEVER allow real org confidential data on unpaid tier

    # ------------------------------------------------------------------ #
    # JWT / Auth
    # ------------------------------------------------------------------ #
    JWT_SECRET_KEY: str = "insecure-dev-secret-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #
    LOG_LEVEL: str = "DEBUG"

    # ------------------------------------------------------------------ #
    # Upload / Ingestion
    # ------------------------------------------------------------------ #
    MAX_UPLOAD_SIZE_MB: int = 20
    MAX_INGESTION_CONCURRENCY: int = 3
    INGESTION_TIMEOUT_SECONDS: int = 300

    # ------------------------------------------------------------------ #
    # Chunking
    # ------------------------------------------------------------------ #
    CHUNK_SIZE_TOKENS: int = 512
    CHUNK_OVERLAP_TOKENS: int = 100

    # ------------------------------------------------------------------ #
    # Quotas
    # ------------------------------------------------------------------ #
    GUEST_QUERY_QUOTA: int = 10


# Module-level singleton ------------------------------------------------- #
settings = Settings()
