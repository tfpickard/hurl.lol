#!/usr/bin/env python
"""Optional LLM adapter interface."""

import asyncio
from abc import ABC, abstractmethod
from typing import Any

from app.config import settings


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def generate(
        self, prompt: str, max_tokens: int = 50, temperature: float = 0.8, seed: int | None = None
    ) -> str:
        """Generate text from a prompt."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider (placeholder)."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        # In production, initialize the OpenAI client here
        # import openai
        # self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate(
        self, prompt: str, max_tokens: int = 50, temperature: float = 0.8, seed: int | None = None
    ) -> str:
        """Generate text using OpenAI API."""
        # Placeholder implementation
        # In production:
        # response = await self.client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": prompt}],
        #     max_tokens=max_tokens,
        #     temperature=temperature,
        # )
        # return response.choices[0].message.content

        # For now, return a placeholder
        await asyncio.sleep(0.05)  # Simulate API latency
        return f"[LLM: {prompt[:50]}...]"


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider (placeholder)."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    async def generate(
        self, prompt: str, max_tokens: int = 50, temperature: float = 0.8, seed: int | None = None
    ) -> str:
        """Generate text using Ollama."""
        # Placeholder implementation
        # In production, make HTTP request to Ollama API
        await asyncio.sleep(0.05)
        return f"[Ollama: {prompt[:50]}...]"


class LocalProvider(LLMProvider):
    """Local model provider (placeholder)."""

    def __init__(self):
        pass

    async def generate(
        self, prompt: str, max_tokens: int = 50, temperature: float = 0.8, seed: int | None = None
    ) -> str:
        """Generate text using local model."""
        # Placeholder implementation
        await asyncio.sleep(0.05)
        return f"[Local: {prompt[:50]}...]"


class LLMAdapter:
    """Adapter for optional LLM integration."""

    def __init__(self):
        self.provider: LLMProvider | None = None
        self._initialize_provider()

    def _initialize_provider(self) -> None:
        """Initialize LLM provider based on config."""
        if not settings.llm_enabled:
            return

        provider_type = settings.llm_provider

        if provider_type == "openai":
            self.provider = OpenAIProvider(settings.llm_api_key)
        elif provider_type == "ollama":
            self.provider = OllamaProvider()
        elif provider_type == "local":
            self.provider = LocalProvider()

    def is_enabled(self) -> bool:
        """Check if LLM is enabled."""
        return self.provider is not None

    async def enhance_text(
        self,
        base_text: str,
        persona_context: str,
        seed: int | None = None,
    ) -> str:
        """
        Optionally enhance text with LLM.

        Args:
            base_text: The template-generated text
            persona_context: Context about the persona's style
            seed: RNG seed

        Returns:
            Enhanced text (or original if LLM disabled/fails)
        """
        if not self.is_enabled():
            return base_text

        prompt = f"""Rewrite this social media post to be more natural and varied, matching this style: {persona_context}

Original: {base_text}

Rewritten (keep it under 50 words):"""

        try:
            # Timeout to respect latency budget
            enhanced = await asyncio.wait_for(
                self.provider.generate(prompt, max_tokens=50, seed=seed),
                timeout=settings.llm_timeout,
            )
            return enhanced.strip()
        except (asyncio.TimeoutError, Exception):
            # Fall back to original on error/timeout
            return base_text


# Global LLM adapter instance
llm_adapter = LLMAdapter()
