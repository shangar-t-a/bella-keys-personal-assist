"""Ollama embeddings client implementation."""

from langchain_ollama import OllamaEmbeddings

from app.core.embeddings.clients.base import EmbeddingsClientInterface
from utilities.logger import GetAppLogger
from utilities.time_profile import log_exec_time


class OllamaEmbeddingsClient(OllamaEmbeddings, EmbeddingsClientInterface):
    """Ollama embeddings client implementation."""

    def __init__(self, model_name: str, enable_gpu: bool = False, **kwargs):
        """Initialize the Ollama client with model name.

        Args:
            model_name (str): The Ollama model to use.
            enable_gpu (bool): Whether to enable GPU acceleration. Defaults to False.

                **Warning: GPU support is currently disabled due to known issues.**
            **kwargs: Additional keyword arguments for the OllamaEmbeddings.

        Examples:
            ### Imports
            >>> from app.core.embeddings import OllamaEmbeddingsClient

            ### Initialize the Ollama client
            >>> client = OllamaEmbeddingsClient(model_name="llama2")

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
            model=model_name,
            # num_gpu=1 if enable_gpu else 0,  # Disabled as faced some issues (Debugging needed)
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
    client = OllamaEmbeddingsClient(
        model_name="qwen3-embedding:0.6b",
        enable_gpu=False,
    )

    text = "How are you?"
    embedding = client.embed_query(text)
    print("Query Embedding:", embedding[:5])

    texts = ["Hello world", "How are you?"]
    embeddings = client.embed_documents(texts)
    print("Document Embeddings:", [emb[:5] for emb in embeddings])
