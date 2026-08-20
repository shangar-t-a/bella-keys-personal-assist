"""Artifact management module for Deep Agent virtual filesystem."""

import json
import os
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

# Base directory for storing generated artifacts
ARTIFACTS_DIR = Path(os.getenv("BELLA_ARTIFACTS_DIR", "archive/artifacts"))


class ArtifactManager:
    """Manages virtual filesystem artifacts created by Bella Chat v2 agents."""

    def __init__(self, storage_dir: Path = ARTIFACTS_DIR) -> None:
        """Initialize ArtifactManager with a storage directory."""
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_artifact(
        self,
        conversation_id: UUID | str,
        filename: str,
        content: str | bytes,
        mime_type: str = "text/plain",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Save a generated artifact to persistent storage.

        Args:
            conversation_id: ID of the chat conversation.
            filename: Original file name.
            content: Text or binary content of the file.
            mime_type: File MIME type (e.g. text/markdown, text/csv).
            metadata: Optional additional metadata dict.

        Returns:
            Dict containing artifact metadata, unique artifact_id, and access URL.
        """
        artifact_id = str(uuid4())
        conv_dir = self.storage_dir / str(conversation_id)
        conv_dir.mkdir(parents=True, exist_ok=True)

        file_path = conv_dir / f"{artifact_id}_{filename}"
        meta_path = conv_dir / f"{artifact_id}_{filename}.json"

        if isinstance(content, str):
            file_path.write_text(content, encoding="utf-8")
        else:
            file_path.write_bytes(content)

        artifact_meta = {
            "artifact_id": artifact_id,
            "conversation_id": str(conversation_id),
            "filename": filename,
            "file_path": str(file_path),
            "mime_type": mime_type,
            "size_bytes": file_path.stat().st_size,
            "metadata": metadata or {},
        }

        meta_path.write_text(json.dumps(artifact_meta, indent=2), encoding="utf-8")
        return artifact_meta

    def get_artifact_meta(self, conversation_id: UUID | str, artifact_id: str) -> dict[str, Any] | None:
        """Retrieve metadata for a specific artifact."""
        conv_dir = self.storage_dir / str(conversation_id)
        if not conv_dir.exists():
            return None

        for meta_file in conv_dir.glob(f"{artifact_id}_*.json"):
            try:
                return json.loads(meta_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return None

    def read_artifact_content(self, conversation_id: UUID | str, artifact_id: str) -> tuple[bytes, str] | None:
        """Read binary content and MIME type of an artifact."""
        meta = self.get_artifact_meta(conversation_id, artifact_id)
        if not meta or not os.path.exists(meta["file_path"]):
            return None

        content = Path(meta["file_path"]).read_bytes()
        return content, meta.get("mime_type", "application/octet-stream")


artifact_manager = ArtifactManager()
