"""Qdrant vector store implementation."""

from time import sleep

from langchain_core.documents import Document
from langchain_qdrant import (
    QdrantVectorStore,
    RetrievalMode,
)
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)

from utilities.logger import GetAppLogger
from utilities.time_profile import log_exec_time


class CustomQdrantClient(QdrantClient):
    """Custom Qdrant client with additional handling if needed."""

    def __init__(self, url: str = "http://localhost:6333", **kwargs):
        """Initialize the Qdrant client with custom settings.

        Args:
            url (str): The URL of the Qdrant server. Defaults to "http://localhost:6333".
            **kwargs: Additional keyword arguments for QdrantClient.
        """
        super().__init__(url=url, **kwargs)
        self._logger = GetAppLogger(fallback_name="CustomQdrantClient").get_logger()
        self._logger.info("Initializing Qdrant client...")
        self._logger.info(f"Connecting to Qdrant at {url}...")

    @log_exec_time
    def create_collection(self, collection_name: str, embedding_dimension: int, force_recreate: bool = False, **kwargs):
        """Create a Qdrant collection with specified parameters.

        Args:
            collection_name (str): Name of the collection to create.
            embedding_dimension (int): Dimension of the embedding vectors.
            force_recreate (bool): If True, delete existing collection and recreate. Defaults to False.
            **kwargs: Additional keyword arguments for create_collection method.
        """
        if self.collection_exists(collection_name=collection_name):
            if force_recreate:
                self._logger.info(f"Deleting existing collection `{collection_name}`...")
                self.delete_collection(collection_name=collection_name)
                sleep(5)  # Wait for a moment to ensure deletion is processed
                self._logger.info(f"Recreating collection `{collection_name}`...")
            else:
                self._logger.info(f"Collection `{collection_name}` already exists.")
                return
        else:
            self._logger.info(f"Collection `{collection_name}` does not exist. Creating new collection...")

        # Create collection if it does not exist or if force_recreate is True
        super().create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=embedding_dimension,
                distance=Distance.COSINE,
            ),
            **kwargs,
        )
        self._logger.info(f"Collection `{collection_name}` created with embedding dimension {embedding_dimension}.")

    @log_exec_time
    def delete_collection(self, collection_name: str, **kwargs):
        """Delete a Qdrant collection.

        Args:
            collection_name (str): Name of the collection to delete.
            **kwargs: Additional keyword arguments for delete_collection method.
        """
        if self.collection_exists(collection_name=collection_name):
            self._logger.info(f"Deleting collection `{collection_name}`...")
            super().delete_collection(collection_name=collection_name, **kwargs)
        else:
            self._logger.info(f"Collection `{collection_name}` does not exist. No action taken.")

    @log_exec_time
    def get_collections(self, **kwargs) -> dict:
        """List all Qdrant collections.

        Args:
            **kwargs: Additional keyword arguments for get_collections method.

        Returns:
            dict: A dictionary containing the list of collections.
        """
        collections = super().get_collections(**kwargs)
        self._logger.info("Existing collections:")
        for collection in collections.collections:
            self._logger.info(f"- {collection.name}")
        return collections


class CustomQdrantVectorStore(QdrantVectorStore):
    """Custom Qdrant vector store with additional handling if needed."""

    def __init__(
        self,
        client: CustomQdrantClient,
        collection_name: str,
        embedding,
        retrieval_mode: RetrievalMode,
        **kwargs,
    ):
        """Initialize the Qdrant vector store.

        Args:
            client (CustomQdrantClient): An instance of the Qdrant client.
            collection_name (str): Name of the collection to use.
            embedding: An embedding function or model.
            retrieval_mode (RetrievalMode): The retrieval mode (e.g., DENSE, HYBRID).
            **kwargs: Additional keyword arguments for QdrantVectorStore.
        """
        super().__init__(
            client=client,
            collection_name=collection_name,
            embedding=embedding,
            retrieval_mode=retrieval_mode,
            **kwargs,
        )
        self._logger = GetAppLogger(fallback_name="CustomQdrantVectorStore").get_logger()
        self._logger.info(f"Initializing Qdrant vector store for collection `{collection_name}`...")

    @log_exec_time
    def add_documents(self, documents: list[Document], **kwargs) -> list[str]:
        """Add documents to the Qdrant collection.

        Args:
            documents (list[Document]): List of Document objects to add.
            **kwargs: Additional keyword arguments for add_documents method.

        Returns:
            list[str]: List of IDs of the added documents.
        """
        self._logger.info(f"Adding {len(documents)} documents to collection `{self.collection_name}`...")
        self._logger.debug(f"Documents adding to collection `{self.collection_name}`: {documents}")
        try:
            added_documents = super().add_documents(documents, **kwargs)
            self._logger.info(f"Successfully added {len(documents)} documents to collection `{self.collection_name}`.")
            return added_documents
        except Exception as err:
            self._logger.error(f"Failed to add documents to collection `{self.collection_name}`: {err}")
            raise err

    @log_exec_time
    def similarity_search(self, query: str, k: int = 5, **kwargs) -> list[tuple[Document, float]]:
        """Perform a similarity search in the Qdrant collection.

        Args:
            query (str): The query string to search for similar documents.
            k (int): The number of top similar documents to retrieve. Defaults to 5.
            **kwargs: Additional keyword arguments for similarity_search_with_score method.

        Returns:
            list[tuple[Document, float]]: A list of tuples containing the similar documents and their similarity scores.
        """
        self._logger.info(f"Performing similarity search in collection `{self.collection_name}`...")
        self._logger.info(f"Searching for top {k} similar documents to query: {query}")
        try:
            retrieved_documents = super().similarity_search_with_score(query, k=k, **kwargs)
            self._logger.info(f"Found {len(retrieved_documents)} similar documents.")
            self._logger.debug(f"Similar documents: {retrieved_documents}")
            return retrieved_documents
        except Exception as err:
            self._logger.error(f"Similarity search failed: {err}")
            raise err


if __name__ == "__main__":
    # Example usage
    # Imports
    from qdrant_client import models

    from app.core.embeddings import get_embedding_client

    # Get Logger
    logger = GetAppLogger().get_logger()

    # Initialize Embedding Client
    embedding_client = get_embedding_client(
        provider="huggingface",
        model_name="Qwen/Qwen3-Embedding-0.6B",
    )

    # Initialize Qdrant Client
    qdrant_client = CustomQdrantClient(url="http://localhost:6333")

    # Create Collection
    collection_name = "example_collection"
    embedding_dimension = 1024  # Example dimension, adjust based on your embedding model
    qdrant_client.create_collection(
        collection_name=collection_name,
        embedding_dimension=embedding_dimension,
        force_recreate=True,
    )

    # List Collections
    collections = qdrant_client.get_collections()
    logger.info(f"Current collections: {collections}")

    # Create Vector Store
    vector_store = CustomQdrantVectorStore(
        client=qdrant_client,
        collection_name=collection_name,
        embedding=embedding_client,
        retrieval_mode=RetrievalMode.DENSE,
    )

    # Add Documents
    documents = [
        Document(page_content="Bella is a personal assistant or chatbot.", metadata={"source": "admin"}),
        Document(
            page_content="Bella can help you with various tasks including managing expenses and retrieving "
            "knowledge base articles.",
            metadata={"source": "github"},
        ),
        Document(page_content="Bella is developed by Shangar Arivazhagan.", metadata={"source": "github"}),
        Document(page_content="Bella is open-source and available on GitHub.", metadata={"source": "github"}),
    ]
    vector_store.add_documents(documents)

    # Perform Similarity Search
    query = "Who created Bella?"
    results = vector_store.similarity_search(query, k=1)
    for idx, result in enumerate(results):
        logger.info(
            f"Result {idx + 1}: {result[0].page_content}; (Source: {result[0].metadata.get('source')})"
            f" with score {result[1]:.4f}"
        )

    # Metadata filtering example
    query = "What can Bella do?"
    results = vector_store.similarity_search(
        query,
        k=2,
        filter=models.Filter(
            should=[
                models.FieldCondition(
                    key="metadata.source",
                    match=models.MatchValue(value="github"),
                )
            ]
        ),
    )
    for idx, result in enumerate(results):
        logger.info(
            f"Filtered Result {idx + 1}: {result[0].page_content} (Source: {result[0].metadata.get('source')})"
            f" with score {result[1]:.4f}"
        )

    # Delete Collection
    qdrant_client.delete_collection(collection_name=collection_name)

    # List Collections Again
    collections = qdrant_client.get_collections()
    logger.info(f"Collections after deletion: {collections}")
