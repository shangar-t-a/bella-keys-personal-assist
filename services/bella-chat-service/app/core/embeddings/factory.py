"""Factory for creating embedding models."""

from typing import Literal

from app.core.embeddings.clients import (
    GoogleEmbeddingsClient,
    HuggingfaceEmbeddingsClient,
    OllamaEmbeddingsClient,
)
from utilities.logger import GetAppLogger


def get_embedding_client(
    provider: Literal["huggingface", "ollama", "google"],
    model_name: str,
    ollama_base_url: str | None = None,
    output_dimensionality: int | None = None,
    **kwargs,
):
    """Get an instance of the embeddings client based on the provider.

    Args:
        provider (Literal["huggingface", "ollama", "google"]): The name of the embedding model provider.
        model_name (str): The name of the model to use.
        ollama_base_url (str | None): The base URL for the Ollama server. Defaults to None.
            Applicable only if provider is "ollama".
        output_dimensionality (int | None): The custom dimension for Google embeddings.
        **kwargs: Additional keyword arguments for the embeddings client.

    Returns:
        EmbeddingsClientInterface: An instance of the embeddings client.
    """
    logger = GetAppLogger().get_logger()
    logger.info(f"Creating embedding client for provider: {provider}, model: {model_name}...")
    if provider == "huggingface":
        if HuggingfaceEmbeddingsClient is None:
            raise ImportError(
                "HuggingfaceEmbeddingsClient could not be loaded because local-llm dependencies are missing. "
                "Ensure local-llm dependencies are installed (e.g. `uv sync --extra local-llm` on host)."
            )
        return HuggingfaceEmbeddingsClient(model_name=model_name, **kwargs)
    elif provider == "ollama":
        return OllamaEmbeddingsClient(model_name=model_name, base_url=ollama_base_url, **kwargs)
    elif provider == "google":
        return GoogleEmbeddingsClient(
            model_name=model_name,
            output_dimensionality=output_dimensionality,
            **kwargs,
        )
    else:
        raise ValueError(f"Unsupported embedding model provider: {provider}")
