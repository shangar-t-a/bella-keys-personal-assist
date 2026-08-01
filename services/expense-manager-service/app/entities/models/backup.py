"""Domain models for backup and restore entities."""

from dataclasses import dataclass
from typing import Any


@dataclass
class BackupMetadata:
    """Domain representation of a backup file metadata."""

    filename: str
    created_at: str
    type: str  # 'manual' | 'pre_restore' | 'other'
    size_bytes: int
    formatted_size: str
    record_counts: dict[str, int]
    total_records: int


@dataclass
class BackupExportResult:
    """Domain result of an export operation."""

    filename: str
    file_path: str
    size_bytes: int
    formatted_size: str
    metadata: dict[str, Any]
    payload: dict[str, Any]


@dataclass
class RestoreResult:
    """Domain result of a restore operation."""

    status: str
    restored_records: int


@dataclass
class BackupConfig:
    """Domain model representing backup directory configuration."""

    backup_dir: str
    absolute_backup_dir: str
