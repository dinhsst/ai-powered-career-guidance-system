from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    APP_NAME: str = "AI Career Guidance System"
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = "sqlite:///./career_guidance.db"

    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    LLM_TEMPERATURE: float = 0.1  # Low temperature for factual, consistent responses

    CHROMA_PERSIST_DIRECTORY: str = "./data/vectorstore"

    GUARDRAILS_API_KEY: str = ""

    CORS_ORIGINS: List[str] = ["http://localhost:4200"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v


settings = Settings()
