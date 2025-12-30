"""Factory for creating embedding models."""

from typing import Literal

from app.core.embeddings.clients import HuggingfaceEmbeddingsClient
from app.core.embeddings.clients.ollama_client import OllamaEmbeddingsClient
from utilities.logger import GetAppLogger


def get_embedding_client(provider: Literal["huggingface", "ollama"], model_name: str, **kwargs):
    """Get an instance of the embeddings client based on the provider.

    Args:
        provider (Literal["huggingface", "ollama"]): The name of the embedding model provider.
        model_name (str): The name of the model to use.
        **kwargs: Additional keyword arguments for the embeddings client.

    Returns:
        HuggingfaceEmbeddingsClient: An instance of the embeddings client.
    """
    logger = GetAppLogger().get_logger()
    logger.info(f"Creating embedding client for provider: {provider}, model: {model_name}...")
    if provider == "huggingface":
        return HuggingfaceEmbeddingsClient(model_name=model_name, **kwargs)
    elif provider == "ollama":
        return OllamaEmbeddingsClient(model_name=model_name, **kwargs)
    else:
        raise ValueError(f"Unsupported embedding model provider: {provider}")
