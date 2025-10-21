"""Embeddings clients module."""

from .huggingface_client import HuggingfaceEmbeddingsClient
from .ollama_client import OllamaEmbeddingsClient

__all__ = [
    "HuggingfaceEmbeddingsClient",
    "OllamaEmbeddingsClient",
]
