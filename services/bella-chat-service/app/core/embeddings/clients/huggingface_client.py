"""Huggingface embeddings client implementation."""

from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from app.core.embeddings.clients.base import EmbeddingsClientInterface
from utilities.logger import GetAppLogger
from utilities.time_profile import log_exec_time


class HuggingfaceEmbeddingsClient(HuggingFaceEmbeddings, EmbeddingsClientInterface):
    """Huggingface embeddings client implementation."""

    def __init__(self, model_name: str, **kwargs):
        """Initialize the Huggingface client with model name.

        Args:
            model_name (str): The Huggingface model to use.
            **kwargs: Additional keyword arguments for the HuggingFaceEmbeddings.

        Examples:
            ### Imports
            >>> from app.core.embeddings import HuggingfaceEmbeddingsClient

            ### Initialize the Huggingface client
            >>> client = HuggingfaceEmbeddingsClient(model_name="Qwen/Qwen3-Embedding-0.6B")

            ### Get embeddings for a list of texts
            >>> texts = ["Hello world", "How are you?"]
            >>> embeddings = client.embed_documents(texts)
            >>> print(embeddings)

            ### Get embedding for a single text
            >>> text = "Hello world"
            >>> embedding = client.embed_query(text)
            >>> print(embedding)
        """
        super().__init__(
            model_name=model_name,
            **kwargs,
        )
        self._logger = GetAppLogger().get_logger()

    @log_exec_time
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a list of texts."""
        self._logger.debug("Embedding documents: %s", texts)
        embeddings = super().embed_documents(texts)
        self._logger.debug("Generated embeddings: %s", embeddings)
        return embeddings

    @log_exec_time
    def embed_query(self, text: str) -> list[float]:
        """Get embedding for a single text."""
        self._logger.debug("Embedding query: %s", text)
        embedding = super().embed_query(text)
        self._logger.debug("Generated embedding: %s", embedding)
        return embedding


if __name__ == "__main__":
    # Example usage
    client = HuggingfaceEmbeddingsClient(model_name="Qwen/Qwen3-Embedding-0.6B")
    texts = ["Hello world", "How are you?"]
    embeddings = client.embed_documents(texts)
    print("Document Embeddings:", [emb[:5] for emb in embeddings])

    text = "How are you?"
    embedding = client.embed_query(text)
    print("Query Embedding:", embedding[:5])
