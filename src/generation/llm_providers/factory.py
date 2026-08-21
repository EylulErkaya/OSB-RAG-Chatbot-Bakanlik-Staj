import os

from .base import LLMProvider
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .ollama_provider import OllamaProvider


def get_provider() -> LLMProvider:

    provider_name = os.getenv(
        "LLM_PROVIDER",
        "ollama",
    ).lower()

    if provider_name == "gemini":

        return GeminiProvider(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash-lite",
            ),
            api_key=os.getenv(
                "GEMINI_API_KEY"
            ),
        )
        
        
    if provider_name == "groq":

        return GroqProvider(
            model=os.getenv(
                "GROQ_MODEL",
                "llama-3.1-8b-instant",
            ),
            api_key=os.getenv(
                "GROQ_API_KEY"
            ),
        )
    if provider_name == "ollama":

        return OllamaProvider(
            model=os.getenv(
                "OLLAMA_MODEL",
                "qwen3:4b-instruct",
            )
        )

    raise ValueError(
        f"Bilinmeyen LLM_PROVIDER: "
        f"{provider_name}"
    )