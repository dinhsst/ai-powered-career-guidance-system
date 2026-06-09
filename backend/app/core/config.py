from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Literal
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = Field(default="Hệ thống tư vấn hướng nghiệp AI", validation_alias="APP_NAME")
    APP_ENV: Literal["development", "staging", "production"] = Field(
        default="development",
        validation_alias="APP_ENV"
    )
    SECRET_KEY: str = Field(default="dev-secret-key", validation_alias="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", validation_alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    DATABASE_URL: str = Field(default="sqlite:///./career_guidance.db", validation_alias="DATABASE_URL")

    GOOGLE_API_KEY: str = Field(default="", validation_alias="GOOGLE_API_KEY")
    GEMINI_MODEL: str = Field(default="", validation_alias="GEMINI_MODEL")
    GEMINI_EMBEDDING_MODEL: str = Field(
        default="models/gemini-embedding-001",
        validation_alias="GEMINI_EMBEDDING_MODEL"
    )
    LLM_TEMPERATURE: float = Field(default=0.1, validation_alias="LLM_TEMPERATURE")

    CHROMA_PERSIST_DIRECTORY: str = Field(default="./data/vectorstore", validation_alias="CHROMA_PERSIST_DIRECTORY")

    GUARDRAILS_API_KEY: str = Field(default="", validation_alias="GUARDRAILS_API_KEY")

    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:4200"],
        validation_alias="CORS_ORIGINS"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @model_validator(mode="after")
    def validate_production_settings(self):
        if self.APP_ENV.lower() != "production":
            return self

        if not self.GOOGLE_API_KEY.strip():
            raise ValueError("GOOGLE_API_KEY không được để trống ở môi trường production")

        if not self.SECRET_KEY.strip() or self.SECRET_KEY == "dev-secret-key":
            raise ValueError("SECRET_KEY phải là giá trị mạnh và khác mặc định ở production")

        if any(origin == "*" for origin in self.CORS_ORIGINS):
            raise ValueError("CORS_ORIGINS không được dùng '*' ở production")

        if self.DATABASE_URL.startswith("sqlite"):
            raise ValueError("DATABASE_URL không được dùng SQLite ở production")

        return self


settings = Settings()
