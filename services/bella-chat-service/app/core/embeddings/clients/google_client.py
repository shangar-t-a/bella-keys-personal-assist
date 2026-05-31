"""Google embeddings client implementation."""


from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.embeddings.clients.base import EmbeddingsClientInterface
from utilities.logger import GetAppLogger
from utilities.time_profile import log_exec_time


class GoogleEmbeddingsClient(GoogleGenerativeAIEmbeddings, EmbeddingsClientInterface):
    """Google embeddings client implementation."""

    def __init__(self, model_name: str, output_dimensionality: int | None = None, **kwargs):
        """Initialize the Google client with model name.

        Args:
            model_name (str): The Google embedding model to use.
            output_dimensionality (Optional[int]): The custom dimension for the output embeddings.
            **kwargs: Additional keyword arguments for the GoogleGenerativeAIEmbeddings.
        """
        super().__init__(model=model_name, output_dimensionality=output_dimensionality, **kwargs)
        self._logger = GetAppLogger().get_logger()

    @log_exec_time
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a list of texts."""
        self._logger.debug("Embedding documents via Google: %s", texts)
        embeddings = super().embed_documents(texts)
        self._logger.debug("Generated embeddings: %s", embeddings)
        return embeddings

    @log_exec_time
    def embed_query(self, text: str) -> list[float]:
        """Get embedding for a single text."""
        self._logger.debug("Embedding query via Google: %s", text)
        embedding = super().embed_query(text)
        self._logger.debug("Generated embedding: %s", embedding)
        return embedding

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for a list of texts asynchronously."""
        return await super().aembed_documents(texts)

    async def aembed_query(self, text: str) -> list[float]:
        """Get embedding for a single text asynchronously."""
        return await super().aembed_query(text)
