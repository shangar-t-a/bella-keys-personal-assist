"""ETL pipeline for loading GitHub data into the vector store.

Loads files of selected format from a GitHub repository folder into the vector store.
- Supports selected text file formats.
- Images and other binary files are not supported currently.

Depends on:
- GitHub Personal Access Token (PAT) with repo access.
- Uses GitHub REST API to fetch files from the repository.
"""

from typing import TYPE_CHECKING
from uuid import uuid4

import httpx
from etl_pipelines.settings import ETLSourceTypes
from langchain_core.documents import Document
from tqdm import tqdm
from utilities.logger import GetAppLogger

if TYPE_CHECKING:
    from langchain_core.vectorstores import VectorStore


class AsyncGitHubETL:
    """Async ETL pipeline to load files from a GitHub repository folder into a vector store."""

    HTTP_CLIENT_TIMEOUT_S = 30
    SUPPORTED_FILE_TYPES = [".md", ".txt", ".py"]

    def __init__(self, token: str, repo: str):
        """Initialize the AsyncGitHubETL instance.

        Args:
            token (str): GitHub Personal Access Token (PAT) with repo access.
            repo (str): GitHub repository in the format "user_name/repository_name".
        """
        self._api_url = f"https://api.github.com/repos/{repo}/contents"
        self._headers = {"Authorization": f"token {token}"}
        self._logger = GetAppLogger(fallback_name="GitHubETL").get_logger()
        self._aclient = httpx.AsyncClient(timeout=self.HTTP_CLIENT_TIMEOUT_S)

        self._logger.info(f"Initialized AsyncGitHubETL for repo: {repo}")

    async def extract_supported_files(self, directory: str) -> list[dict]:
        """Extract:

        - Recursively fetch supported files in the given GitHub repository folder.
        - Collects all files urls with extensions in SUPPORTED_FILE_TYPES.

        Args:
            directory (str): Path to the directory in the repository.

        Returns:
            list[dict]: List of supported files in the directory.
        """
        self._logger.info(f"Extracting supported files from folder: {directory}...")
        self._logger.debug(f"Supported file types: {self.SUPPORTED_FILE_TYPES}")

        files = []

        url = f"{self._api_url}/{directory}"
        resp = await self._aclient.get(url, headers=self._headers)
        resp.raise_for_status()
        contents = resp.json()
        for content_file in contents:
            if content_file["type"] == "file" and content_file["name"].endswith(tuple(self.SUPPORTED_FILE_TYPES)):
                files.append(content_file)
            elif content_file["type"] == "dir":
                sub_files = await self.extract_supported_files(content_file["path"])
                files.extend(sub_files)

        return files

    async def transform(self, files: list[dict]) -> list[Document]:
        """Transform:

        - Fetch file contents from the download URLs.
        - Create Document objects with file content and metadata.

        Args:
            files (list[dict]): List of files with download URLs.

        Returns:
            list[Document]: List of Document objects with file content and metadata.
        """
        self._logger.info(f"Transforming {len(files)} files...")

        docs = []
        for file in tqdm(files, desc="Transforming files:"):
            resp = await self._aclient.get(file["download_url"], headers=self._headers)
            resp.raise_for_status()
            docs.append(
                Document(
                    page_content=resp.text,
                    metadata={
                        "source": file["html_url"],
                        "source_type": ETLSourceTypes.GITHUB,
                        "path": file["path"],
                        "id": str(uuid4()),
                    },
                ),
            )

        return docs

    async def load_documents_in_batches(self, vector_store: "VectorStore", docs: list[Document], batch_size: int = 4):
        """Load:

        - Load documents to the vector store in batches to avoid GPU Overload.

        Args:
            vector_store (VectorStore): The vector store instance to load documents into.
            docs (list[Document]): List of Document objects to be loaded.
            batch_size (int, optional): Number of documents to load in each batch. Defaults to 4.

        """
        for start_idx in tqdm(range(0, len(docs), batch_size), desc="Loading documents:"):
            batch_docs = docs[start_idx : start_idx + batch_size]
            vector_store.add_documents(documents=batch_docs)

    async def run_etl(self, directory: str, vector_store: "VectorStore") -> list[Document]:
        """Run the ETL pipeline to load files from a GitHub repository directory into a vector store.

        Args:
            directory (str): Path to the directory in the repository.
            vector_store (VectorStore): The vector store instance to load documents into.

        Returns:
            list[Document]: List of Document objects loaded into the vector store.
        """
        self._logger.info(f"Starting ETL process for directory: {directory}...")

        files = await self.extract_supported_files(directory=directory)
        docs = await self.transform(files)
        await self.load_documents_in_batches(vector_store=vector_store, docs=docs)

        self._logger.info(f"Loaded {len(docs)} documents into the vector store.")

        return docs
