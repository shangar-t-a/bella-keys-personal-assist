"""ETL pipeline to load contents from keys personal wiki GitHub repo."""

import asyncio

from app.core.embeddings import get_embedding_client
from app.core.vector_store.qdrant import CustomQdrantClient, CustomQdrantVectorStore, RetrievalMode
from etl_pipelines.github.loader import AsyncGitHubETL
from etl_pipelines.settings import settings


class GitHubKeysPersonalWikiETL:
    """ETL pipeline to load contents from keys personal wiki GitHub repo."""

    REPO = "shangar-t-a/keys-personal-wiki"
    FOLDERS = [
        "keys-wiki-site/docs",
    ]

    def __init__(self, git_pat: str, qdrant_url: str = "http://localhost:6333"):
        """Initialize the ETL pipeline with GitHub credentials.

        Args:
            git_pat (str): GitHub Personal Access Token.
        """
        self.qdrant_url = qdrant_url
        self.github_etl = AsyncGitHubETL(token=git_pat, repo=self.REPO)

    async def pipeline(self):
        """Run the ETL pipeline to load contents from specified folders into the vector store."""
        # Step 1: Create a Qdrant client
        qdrant_client = CustomQdrantClient(url=self.qdrant_url)

        # Step 2: Create an embedding client
        embedding = get_embedding_client(
            provider="ollama",
            model_name="qwen3-embedding:0.6b",
            enable_gpu=False,
        )

        # Step 3: Create collection if it does not exist
        qdrant_client.create_collection(
            collection_name="keys-personal-wiki-docs",
            embedding_dimension=1024,
            force_recreate=True,
        )

        # Step 4: Create a Qdrant vector store
        vector_store = CustomQdrantVectorStore(
            client=qdrant_client,
            collection_name="keys-personal-wiki-docs",
            embedding=embedding,
            retrieval_mode=RetrievalMode.DENSE,
        )

        # Step 5: Run the ETL process for each folder
        for folder in self.FOLDERS:
            await self.github_etl.run_etl(directory=folder, vector_store=vector_store)


if __name__ == "__main__":
    GIT_PAT = settings.GIT_PAT.get_secret_value()
    etl = GitHubKeysPersonalWikiETL(
        git_pat=GIT_PAT,
        qdrant_url="http://localhost:6333",
    )

    asyncio.run(etl.pipeline())
