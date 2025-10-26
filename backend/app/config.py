#!/usr/bin/env python
"""Configuration management for Hurl."""

import os
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    hurl_env: Literal["dev", "staging", "prod"] = Field(default="dev", alias="HURL_ENV")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    require_auth: bool = Field(default=False, alias="HURL_REQUIRE_AUTH")
    persist: bool = Field(default=False, alias="HURL_PERSIST")

    # LLM configuration
    llm_provider: Literal["none", "openai", "ollama", "local"] = Field(
        default="none", alias="HURL_LLM_PROVIDER"
    )
    llm_api_key: str = Field(default="", alias="HURL_LLM_API_KEY")
    llm_timeout: float = Field(default=0.150, alias="HURL_LLM_TIMEOUT")  # 150ms budget

    # CORS
    allow_origins: str | list[str] = Field(
        default=["https://hurl.lol", "http://localhost:3000"],
        alias="HURL_ALLOW_ORIGINS",
    )

    # Rate limiting (requests per minute per token)
    rate_limit_rpm: int = Field(default=1000, alias="HURL_RATE_LIMIT_RPM")

    # Trend engine
    trend_tick_interval: float = Field(default=5.0, alias="HURL_TREND_TICK_INTERVAL")

    # Generation defaults
    default_seed: int | None = Field(default=None, alias="HURL_DEFAULT_SEED")
    max_batch_size: int = Field(default=1000, alias="HURL_MAX_BATCH_SIZE")

    @field_validator('allow_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins from environment variable."""
        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return []
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        # Already a list or other iterable
        return v

    class Config:
        """Pydantic config."""
        env_file = ".env"
        extra = "ignore"

    @property
    def is_dev(self) -> bool:
        """Check if running in dev mode."""
        return self.hurl_env == "dev"

    @property
    def is_prod(self) -> bool:
        """Check if running in prod mode."""
        return self.hurl_env == "prod"

    @property
    def llm_enabled(self) -> bool:
        """Check if LLM is enabled."""
        return self.llm_provider != "none" and bool(self.llm_api_key)


# Global settings instance
settings = Settings()
