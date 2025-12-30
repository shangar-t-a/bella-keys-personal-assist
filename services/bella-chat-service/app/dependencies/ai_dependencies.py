"""AI related dependencies."""

from functools import lru_cache
from typing import TYPE_CHECKING

from langchain_qdrant import RetrievalMode

from app.core.embeddings import get_embedding_client
from app.core.llms import get_llm_client
from app.core.vector_store import (
    CustomQdrantClient,
    CustomQdrantVectorStore,
)
from app.settings import get_settings

if TYPE_CHECKING:
    from app.core.embeddings.clients import HuggingfaceEmbeddingsClient
    from app.core.llms.clients import (
        GeminiClient,
        OllamaClient,
    )


@lru_cache(maxsize=1)
def get_app_synthesis_llm_client() -> "GeminiClient | OllamaClient":
    """Get the synthesis LLM client."""
    settings = get_settings()
    synthesis_llm_client = get_llm_client(
        provider=settings.SYNTHESIS_MODEL_PROVIDER,
        model_name=settings.SYNTHESIS_MODEL_NAME,
        ollama_base_url=settings.OLLAMA_URL,
        temperature=0.1,
    )
    return synthesis_llm_client


@lru_cache(maxsize=1)
def get_app_embedding_client() -> "HuggingfaceEmbeddingsClient":
    """Get the embedding client."""
    settings = get_settings()
    embedding_client = get_embedding_client(
        provider=settings.EMBEDDING_MODEL_PROVIDER,
        model_name=settings.EMBEDDING_MODEL_NAME,
        ollama_base_url=settings.OLLAMA_URL,
    )
    return embedding_client


@lru_cache(maxsize=1)
def get_app_vector_db_client() -> "CustomQdrantClient":
    """Get the vector DB client."""
    settings = get_settings()
    vector_db_client = CustomQdrantClient(
        url=settings.QDRANT_URL,
    )
    return vector_db_client


@lru_cache(maxsize=1)
def get_app_vector_store() -> "CustomQdrantVectorStore":
    """Get the vector store."""
    settings = get_settings()
    vector_store = CustomQdrantVectorStore(
        client=get_app_vector_db_client(),
        collection_name=settings.QDRANT_COLLECTION_NAME,
        embedding=get_app_embedding_client(),
        retrieval_mode=RetrievalMode.DENSE,
    )
    return vector_store
