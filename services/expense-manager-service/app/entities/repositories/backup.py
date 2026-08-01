"""Abstract repository interface for database backup and restore operations."""

from abc import ABC, abstractmethod
from typing import Any

from app.entities.models.backup import BackupExportResult, BackupMetadata, RestoreResult


class BackupRepositoryInterface(ABC):
    """Interface defining database backup and restore infrastructure operations."""

    @abstractmethod
    async def export_backup(self) -> BackupExportResult:
        """Export database tables to local folder snapshot."""
        pass

    @abstractmethod
    def list_backups(self) -> list[BackupMetadata]:
        """List all available backup snapshots in local folder."""
        pass

    @abstractmethod
    async def restore_from_payload(self, payload: dict[str, Any]) -> RestoreResult:
        """Restore database state atomically from JSON payload."""
        pass

    @abstractmethod
    def delete_backup(self, filename: str) -> None:
        """Delete specific snapshot file from local backup directory."""
        pass
