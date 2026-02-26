"""
AI Provider Abstraction Layer
==============================
Eliminates vendor lock-in by abstracting AI model calls behind a common interface.
Swap providers by changing the AI_PROVIDER environment variable:
  - "gemini"  → Google Gemini (default)
  - "openai"  → OpenAI GPT
  - "ollama"  → Self-hosted Ollama (zero vendor dependency)

Usage:
    provider = get_ai_provider()
    response = await provider.generate(prompt)
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers. All providers must implement generate()."""

    @abstractmethod
    async def generate(self, prompt: str, system_instruction: str = "") -> str:
        """Generate a response from the AI model."""
        raise NotImplementedError


class GeminiProvider(AIProvider):
    """Google Gemini AI provider."""

    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.model_name = os.environ.get("AI_MODEL", "gemini-1.5-flash")
        if not self.api_key:
            logger.warning("GOOGLE_API_KEY not set. Gemini provider will fail.")

    async def generate(self, prompt: str, system_instruction: str = "") -> str:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)

        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        response = model.generate_content(full_prompt)
        return response.text


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider (drop-in replacement for Gemini)."""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model_name = os.environ.get("AI_MODEL", "gpt-4o")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set. OpenAI provider will fail.")

    async def generate(self, prompt: str, system_instruction: str = "") -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)

        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content


class OllamaProvider(AIProvider):
    """Self-hosted Ollama provider (ZERO external vendor dependency)."""

    def __init__(self):
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model_name = os.environ.get("AI_MODEL", "llama3")

    async def generate(self, prompt: str, system_instruction: str = "") -> str:
        import httpx

        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["response"]


class FallbackProvider(AIProvider):
    """Fallback provider that returns empty responses. Used when no AI is configured."""

    async def generate(self, prompt: str, system_instruction: str = "") -> str:
        logger.warning("Using FallbackProvider — no AI model configured.")
        return "{}"


# ── Factory ──────────────────────────────────────────────────
_PROVIDERS = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "ollama": OllamaProvider,
    "fallback": FallbackProvider,
}


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Factory function to get the configured AI provider.
    Reads from AI_PROVIDER env var, or accepts an explicit name.
    """
    name = (provider_name or os.environ.get("AI_PROVIDER", "gemini")).lower()

    provider_class = _PROVIDERS.get(name)
    if not provider_class:
        logger.error(f"Unknown AI provider: {name}. Falling back to FallbackProvider.")
        return FallbackProvider()

    logger.info(f"Initializing AI provider: {name} (model: {os.environ.get('AI_MODEL', 'default')})")
    return provider_class()
