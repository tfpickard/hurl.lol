from __future__ import annotations

from ...config import get_settings


async def generate_with_llm(prompt: str, *, seed: int | None = None, max_tokens: int = 120, temperature: float = 0.8) -> str:
    """Placeholder implementation that echoes the prompt when no provider configured."""

    settings = get_settings()
    if settings.llm_provider.lower() == "none" or not settings.llm_api_key:
        return prompt
    # In this offline environment we cannot call external services, so we simply tag the prompt.
    return f"[LLM:{settings.llm_provider}] {prompt}"
