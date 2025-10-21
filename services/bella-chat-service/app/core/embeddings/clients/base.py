"""Base embeddings client for Embedding engines."""

from abc import ABC, abstractmethod


class EmbeddingsClientInterface(ABC):
    """Abstract base class for embeddings clients."""

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a list of texts."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Get embedding for a single text."""
        pass
