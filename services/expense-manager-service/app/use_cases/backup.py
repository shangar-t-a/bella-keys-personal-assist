"""Use case and business logic for database backup and restore operations."""

from typing import Any

from app.entities.models.backup import BackupConfig, BackupExportResult, BackupMetadata, RestoreResult
from app.entities.repositories.backup import BackupRepositoryInterface


class BackupService:
    """Backup service handling business logic and repository delegation."""

    def __init__(self, backup_repository: BackupRepositoryInterface):
        """Initialize BackupService with repository interface."""
        self.backup_repository = backup_repository

    def get_backup_config(self) -> BackupConfig:
        """Get current backup directory configuration."""
        return self.backup_repository.get_backup_config()

    def set_backup_dir(self, new_dir: str) -> BackupConfig:
        """Update target backup directory path."""
        return self.backup_repository.set_backup_dir(new_dir)

    async def export_backup(self) -> BackupExportResult:

        """Export database state to timestamped JSON backup file."""
        return await self.backup_repository.export_backup()

    def list_backups(self) -> list[BackupMetadata]:
        """List all available backup snapshots in local folder."""
        return self.backup_repository.list_backups()

    async def restore_from_payload(self, payload: dict[str, Any]) -> RestoreResult:
        """Restore database state atomically from JSON payload."""
        return await self.backup_repository.restore_from_payload(payload)

    def delete_backup(self, filename: str) -> None:
        """Delete specific snapshot file from local backup directory."""
        self.backup_repository.delete_backup(filename)
