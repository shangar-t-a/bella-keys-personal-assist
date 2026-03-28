"""Factory for creating LLM clients."""

from typing import Literal

from app.core.llms.clients import (
    GeminiClient,
    OllamaClient,
)
from utilities.logger import GetAppLogger


def get_llm_client(
    provider: Literal["google", "ollama"],
    model_name: str,
    temperature: float,
    ollama_base_url: str = "http://localhost:11434",
    context_window: int | None = None,
    **kwargs,
):
    """Get an instance of the LLM client based on the provider.

    Args:
        provider (Literal["google", "ollama"]): The name of the model provider.
        model_name (str): The name of the model to use.
        temperature (float): The temperature to use for the model.
        ollama_base_url (str): The base URL for the Ollama server. Defaults to "http://localhost:11434".

            Applicable only if provider is "ollama".
        context_window (int | None): The context window size for the model. Mapped to provider-specific
            parameters (e.g. ``num_ctx`` for Ollama). Ignored if None.
        **kwargs: Additional keyword arguments for the LLM client.

    Returns:
        GeminiClient | OllamaClient: An instance of the LLM client.
    """
    logger = GetAppLogger().get_logger()
    logger.info(f"Creating LLM client for provider: {provider}, model: {model_name}, temperature: {temperature}...")
    if provider == "google":
        return GeminiClient(model=model_name, temperature=temperature, **kwargs)
    elif provider == "ollama":
        if context_window is not None:
            kwargs["num_ctx"] = context_window
        return OllamaClient(model=model_name, temperature=temperature, base_url=ollama_base_url, **kwargs)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")
