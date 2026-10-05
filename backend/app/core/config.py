import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # Database — PostgreSQL via docker-compose (see .env.example)
    DATABASE_URL: str = "postgresql+psycopg2://asthma:asthma@localhost:5432/asthma"

    # Supabase Auth (user authentication — NOT for ESP8266)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    # Service role key is server-only. NEVER expose to frontend/ESP8266.
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # App security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ML
    MODEL_PATH: str = "models/risk_model.pkl"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
