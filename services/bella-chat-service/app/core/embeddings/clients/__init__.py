"""Embeddings clients module."""

from .google_client import GoogleEmbeddingsClient
from .ollama_client import OllamaEmbeddingsClient

try:
    from .huggingface_client import HuggingfaceEmbeddingsClient
except ImportError:
    HuggingfaceEmbeddingsClient = None  # type: ignore

__all__ = [
    "HuggingfaceEmbeddingsClient",
    "OllamaEmbeddingsClient",
    "GoogleEmbeddingsClient",
]
