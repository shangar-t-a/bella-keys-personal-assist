"""Unit tests for BackupService, PostgresBackupRepository, and local folder backup management."""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.entities.models.backup import BackupConfig, BackupExportResult, BackupMetadata, RestoreResult
from app.entities.repositories.backup import BackupRepositoryInterface
from app.infrastructures.postgres_db.backup import (
    PostgresBackupRepository,
    ensure_backup_dir,
    format_file_size,
    prune_manual_backups,
)
from app.use_cases.backup import BackupService


def test_ensure_backup_dir(tmp_path):
    """Test backup directory creation."""
    test_dir = str(tmp_path / "test_backups")
    d = ensure_backup_dir(test_dir)
    assert os.path.exists(d)


def test_format_file_size():
    """Test file size formatting logic."""
    assert format_file_size(500) == "500 B"
    assert format_file_size(2048) == "2.0 KB"
    assert format_file_size(2500000) == "2.38 MB"


def test_prune_manual_backups(tmp_path):
    """Test pruning of manual backup files when exceeding limit of 5."""
    test_dir = str(tmp_path / "prune_test")
    os.makedirs(test_dir, exist_ok=True)

    for i in range(7):
        fpath = os.path.join(test_dir, f"ems_backup_20260801_00000{i}.json")
        with open(fpath, "w") as f:
            f.write("{}")
        os.utime(fpath, (1000 + i * 10, 1000 + i * 10))

    safety_path = os.path.join(test_dir, "pre_restore_20260801_000000.json")
    with open(safety_path, "w") as f:
        f.write("{}")

    prune_manual_backups(test_dir, max_limit=5)

    remaining_files = os.listdir(test_dir)
    manual_files = [f for f in remaining_files if f.startswith("ems_backup_")]
    assert len(manual_files) == 5
    assert "pre_restore_20260801_000000.json" in remaining_files



@pytest.mark.asyncio
async def test_backup_service_delegation():
    """Test BackupService delegates properly to repository interface."""
    mock_repo = MagicMock(spec=BackupRepositoryInterface)
    mock_repo.export_backup = AsyncMock(
        return_value=BackupExportResult(
            filename="ems_backup_123.json",
            file_path="/tmp/ems_backup_123.json",
            size_bytes=100,
            formatted_size="100 B",
            metadata={},
            payload={},
        )
    )
    mock_repo.list_backups.return_value = [
        BackupMetadata(
            filename="ems_backup_123.json",
            created_at="2026-08-01T00:00:00Z",
            type="manual",
            size_bytes=100,
            formatted_size="100 B",
            record_counts={},
            total_records=0,
        )
    ]
    mock_repo.restore_from_payload = AsyncMock(return_value=RestoreResult(status="success", restored_records=10))

    service = BackupService(backup_repository=mock_repo)

    export_res = await service.export_backup()
    assert export_res.filename == "ems_backup_123.json"

    list_res = service.list_backups()
    assert len(list_res) == 1

    restore_res = await service.restore_from_payload({"tables": {}})
    assert restore_res.restored_records == 10

    service.delete_backup("ems_backup_123.json")
    mock_repo.delete_backup.assert_called_once_with("ems_backup_123.json")


@pytest.mark.asyncio
async def test_postgres_backup_repository_invalid_payload():
    """Test restore error handling for invalid payload in PostgresBackupRepository."""
    repo = PostgresBackupRepository()
    with pytest.raises(ValueError, match="Invalid backup payload envelope"):
        await repo.restore_from_payload({"invalid": "envelope"})
