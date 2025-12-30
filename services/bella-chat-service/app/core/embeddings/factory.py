"""Factory for creating embedding models."""

from typing import Literal

from app.core.embeddings.clients import HuggingfaceEmbeddingsClient
from app.core.embeddings.clients.ollama_client import OllamaEmbeddingsClient
from utilities.logger import GetAppLogger


def get_embedding_client(
    provider: Literal["huggingface", "ollama"],
    model_name: str,
    ollama_base_url: str = "http://localhost:11434",
    **kwargs,
):
    """Get an instance of the embeddings client based on the provider.

    Args:
        provider (Literal["huggingface", "ollama"]): The name of the embedding model provider.
        model_name (str): The name of the model to use.
        ollama_base_url (str): The base URL for the Ollama server. Defaults to "http://localhost:11434".

            Applicable only if provider is "ollama".
        **kwargs: Additional keyword arguments for the embeddings client.

    Returns:
        HuggingfaceEmbeddingsClient: An instance of the embeddings client.
    """
    logger = GetAppLogger().get_logger()
    logger.info(f"Creating embedding client for provider: {provider}, model: {model_name}...")
    if provider == "huggingface":
        return HuggingfaceEmbeddingsClient(model_name=model_name, **kwargs)
    elif provider == "ollama":
        return OllamaEmbeddingsClient(model_name=model_name, base_url=ollama_base_url, **kwargs)
    else:
        raise ValueError(f"Unsupported embedding model provider: {provider}")
