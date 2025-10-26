from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Optional


def _split(value: str | None, default: List[str]) -> List[str]:
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(slots=True)
class Settings:
    app_name: str = field(default_factory=lambda: os.getenv("HURL_APP_NAME", "Hurl REST API — hurl.rest"))
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    environment: str = field(default_factory=lambda: os.getenv("HURL_ENV", "dev"))
    allow_origins: List[str] = field(
        default_factory=lambda: _split(os.getenv("HURL_ALLOW_ORIGINS"), ["https://hurl.lol", "http://localhost:3000"])
    )
    require_auth: bool = field(default_factory=lambda: os.getenv("HURL_REQUIRE_AUTH", "0") == "1")
    persist: bool = field(default_factory=lambda: os.getenv("HURL_PERSIST", "0") == "1")
    llm_provider: str = field(default_factory=lambda: os.getenv("HURL_LLM_PROVIDER", "none"))
    llm_api_key: Optional[str] = field(default_factory=lambda: os.getenv("HURL_LLM_API_KEY"))
    log_json: bool = field(default_factory=lambda: os.getenv("HURL_LOG_JSON", "0") == "1")
    metrics_enabled: bool = field(default_factory=lambda: os.getenv("HURL_METRICS_ENABLED", "1") == "1")
    admin_token: Optional[str] = field(default_factory=lambda: os.getenv("HURL_ADMIN_TOKEN"))


@lru_cache()
def get_settings() -> Settings:
    return Settings()
