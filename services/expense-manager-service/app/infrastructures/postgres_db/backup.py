"""PostgreSQL implementation of BackupRepositoryInterface."""

import json
import os
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, select

from app.entities.models.backup import BackupExportResult, BackupMetadata, RestoreResult
from app.entities.repositories.backup import BackupRepositoryInterface
from app.infrastructures.postgres_db.database import Base, get_async_session

BACKUP_DIR = os.path.abspath("./backups")


def ensure_backup_dir() -> str:
    """Ensure local backup directory exists."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    return BACKUP_DIR


def format_file_size(size_bytes: int) -> str:
    """Format size in bytes to human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def serialize_value(val: Any) -> Any:
    """Serialize database column value to JSON-compatible type."""
    if isinstance(val, datetime):
        return val.isoformat()
    return val


def prune_manual_backups(max_limit: int = 5) -> None:
    """Prune oldest manual backup files when exceeding max_limit.

    Safety snapshots (pre_restore_*.json) are preserved and excluded from manual pruning.
    """
    backup_dir = ensure_backup_dir()
    files = []
    for f in os.listdir(backup_dir):
        if f.startswith("ems_backup_") and f.endswith(".json"):
            full_path = os.path.join(backup_dir, f)
            if os.path.isfile(full_path):
                files.append((full_path, os.path.getmtime(full_path)))

    files.sort(key=lambda x: x[1])
    while len(files) > max_limit:
        oldest_file, _ = files.pop(0)
        try:
            os.remove(oldest_file)
        except OSError:
            pass


class PostgresBackupRepository(BackupRepositoryInterface):
    """PostgreSQL implementation for backup export, listing, and atomic restore."""

    async def export_backup(self) -> BackupExportResult:
        """Export database tables to a JSON payload file in local backup folder."""
        backup_dir = ensure_backup_dir()
        table_data: dict[str, list[dict[str, Any]]] = {}
        record_counts: dict[str, int] = {}

        async_session_factory = get_async_session()
        async with async_session_factory() as session:
            for table in Base.metadata.sorted_tables:
                stmt = select(table)
                result = await session.execute(stmt)
                rows = result.mappings().all()

                serialized_rows = []
                for row in rows:
                    row_dict = {col: serialize_value(val) for col, val in row.items()}
                    serialized_rows.append(row_dict)

                table_data[table.name] = serialized_rows
                record_counts[table.name] = len(serialized_rows)

        timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"ems_backup_{timestamp_str}.json"
        file_path = os.path.join(backup_dir, filename)

        payload = {
            "metadata": {
                "version": "1.0",
                "service": "expense_manager",
                "exported_at": datetime.now(UTC).isoformat(),
                "record_counts": record_counts,
                "total_records": sum(record_counts.values()),
            },
            "tables": table_data,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        prune_manual_backups(max_limit=5)

        return BackupExportResult(
            filename=filename,
            file_path=file_path,
            size_bytes=os.path.getsize(file_path),
            formatted_size=format_file_size(os.path.getsize(file_path)),
            metadata=payload["metadata"],
            payload=payload,
        )

    def list_backups(self) -> list[BackupMetadata]:
        """List all available backup snapshots in the local backups folder."""
        backup_dir = ensure_backup_dir()
        snapshots = []

        for f in os.listdir(backup_dir):
            if not f.endswith(".json"):
                continue

            file_path = os.path.join(backup_dir, f)
            if not os.path.isfile(file_path):
                continue

            size_bytes = os.path.getsize(file_path)
            stat = os.stat(file_path)
            created_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat()

            backup_type = "manual"
            if f.startswith("pre_restore_"):
                backup_type = "pre_restore"

            metadata = None
            try:
                with open(file_path, "r", encoding="utf-8") as file_obj:
                    data = json.load(file_obj)
                    if isinstance(data, dict) and "metadata" in data:
                        metadata = data["metadata"]
            except Exception:
                pass

            snapshots.append(
                BackupMetadata(
                    filename=f,
                    created_at=metadata.get("exported_at", created_at) if metadata else created_at,
                    type=backup_type,
                    size_bytes=size_bytes,
                    formatted_size=format_file_size(size_bytes),
                    record_counts=metadata.get("record_counts", {}) if metadata else {},
                    total_records=metadata.get("total_records", 0) if metadata else 0,
                )
            )

        snapshots.sort(key=lambda x: x.created_at, reverse=True)
        return snapshots

    async def create_pre_restore_snapshot() -> str:
        """Create automatic safety snapshot before performing restore."""
        backup_dir = ensure_backup_dir()
        table_data: dict[str, list[dict[str, Any]]] = {}
        record_counts: dict[str, int] = {}

        async_session_factory = get_async_session()
        async with async_session_factory() as session:
            for table in Base.metadata.sorted_tables:
                stmt = select(table)
                result = await session.execute(stmt)
                rows = result.mappings().all()

                serialized_rows = []
                for row in rows:
                    row_dict = {col: serialize_value(val) for col, val in row.items()}
                    serialized_rows.append(row_dict)

                table_data[table.name] = serialized_rows
                record_counts[table.name] = len(serialized_rows)

        timestamp_str = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"pre_restore_{timestamp_str}.json"
        file_path = os.path.join(backup_dir, filename)

        payload = {
            "metadata": {
                "version": "1.0",
                "service": "expense_manager",
                "exported_at": datetime.now(UTC).isoformat(),
                "record_counts": record_counts,
                "total_records": sum(record_counts.values()),
                "is_pre_restore": True,
            },
            "tables": table_data,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return filename

    async def restore_from_payload(self, payload: dict[str, Any]) -> RestoreResult:
        """Restore database state inside an isolated transaction.

        Creates pre-restore safety snapshot prior to clearing tables.
        """
        if not isinstance(payload, dict) or "tables" not in payload:
            raise ValueError("Invalid backup payload envelope. Missing 'tables' dictionary.")

        await self.create_pre_restore_snapshot()

        tables_data = payload.get("tables", {})
        sorted_tables = Base.metadata.sorted_tables
        reversed_tables = list(reversed(sorted_tables))

        async_session_factory = get_async_session()
        async with async_session_factory() as session:
            for table in reversed_tables:
                await session.execute(table.delete())

            total_restored = 0
            for table in sorted_tables:
                t_name = table.name
                if t_name in tables_data and isinstance(tables_data[t_name], list) and tables_data[t_name]:
                    rows = tables_data[t_name]
                    processed_rows = []
                    for r in rows:
                        p_row = {}
                        for col in table.columns:
                            c_name = col.name
                            if c_name in r:
                                val = r[c_name]
                                if val is not None and isinstance(col.type, DateTime):
                                    if isinstance(val, str):
                                        try:
                                            p_row[c_name] = datetime.fromisoformat(val)
                                        except ValueError:
                                            p_row[c_name] = val
                                    else:
                                        p_row[c_name] = val
                                else:
                                    p_row[c_name] = val
                        processed_rows.append(p_row)

                    if processed_rows:
                        await session.execute(table.insert(), processed_rows)
                        total_restored += len(processed_rows)

            await session.commit()
            return RestoreResult(status="success", restored_records=total_restored)

    def delete_backup(self, filename: str) -> None:
        """Delete specific snapshot file from local backup directory."""
        safe_filename = os.path.basename(filename)
        if not safe_filename.endswith(".json"):
            raise ValueError("Invalid backup file extension.")

        backup_dir = ensure_backup_dir()
        file_path = os.path.join(backup_dir, safe_filename)

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Backup file '{safe_filename}' not found.")

        os.remove(file_path)
