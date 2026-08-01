"""FastAPI router endpoints for backup and restore management."""

import json
import os
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.infrastructures.postgres_db.backup import BACKUP_DIR, ensure_backup_dir
from app.routers.v1.services import get_backup_service
from app.use_cases.backup import BackupService

backup_router = APIRouter(prefix="/backup", tags=["backup"])


class RestoreSnapshotRequest(BaseModel):
    """Request schema for restoring a specific snapshot file."""

    filename: str


@backup_router.post("/export")
async def export_backup(
    backup_service: BackupService = Depends(get_backup_service),
) -> dict[str, Any]:
    """Export database state to timestamped JSON backup file in local folder."""
    try:
        result = await backup_service.export_backup()
        return {
            "status": "success",
            "filename": result.filename,
            "formatted_size": result.formatted_size,
            "size_bytes": result.size_bytes,
            "metadata": result.metadata,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export backup: {str(e)}",
        ) from e


@backup_router.get("/list")
async def list_backups(
    backup_service: BackupService = Depends(get_backup_service),
) -> list[dict[str, Any]]:
    """Retrieve list of all local backup snapshots."""
    try:
        snapshots = backup_service.list_backups()
        return [
            {
                "filename": snap.filename,
                "created_at": snap.created_at,
                "type": snap.type,
                "size_bytes": snap.size_bytes,
                "formatted_size": snap.formatted_size,
                "record_counts": snap.record_counts,
                "total_records": snap.total_records,
            }
            for snap in snapshots
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list backups: {str(e)}",
        ) from e


@backup_router.post("/restore/latest")
async def restore_latest_backup(
    backup_service: BackupService = Depends(get_backup_service),
) -> dict[str, Any]:
    """Restore database state from the most recent local backup snapshot."""
    snapshots = backup_service.list_backups()
    if not snapshots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No local backup snapshots available for restore.",
        )

    latest_filename = snapshots[0].filename
    backup_dir = ensure_backup_dir()
    file_path = os.path.join(backup_dir, latest_filename)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        result = await backup_service.restore_from_payload(payload)
        return {"status": result.status, "restored_records": result.restored_records}
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Restore operation failed: {str(e)}",
        ) from e


@backup_router.post("/restore/snapshot")
async def restore_specific_snapshot(
    request: RestoreSnapshotRequest,
    backup_service: BackupService = Depends(get_backup_service),
) -> dict[str, Any]:
    """Restore database state from a specific local snapshot filename."""
    safe_filename = os.path.basename(request.filename)
    backup_dir = ensure_backup_dir()
    file_path = os.path.join(backup_dir, safe_filename)

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup file '{safe_filename}' not found.",
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        result = await backup_service.restore_from_payload(payload)
        return {"status": result.status, "restored_records": result.restored_records}
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Restore operation failed: {str(e)}",
        ) from e


@backup_router.post("/restore/upload")
async def restore_from_upload(
    file: UploadFile = File(...),
    backup_service: BackupService = Depends(get_backup_service),
) -> dict[str, Any]:
    """Upload and restore database state from external JSON backup file."""
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only valid JSON backup files are accepted.",
        )

    try:
        content = await file.read()
        payload = json.loads(content.decode("utf-8"))
        result = await backup_service.restore_from_payload(payload)
        return {"status": result.status, "restored_records": result.restored_records}
    except json.JSONDecodeError as json_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File content is not valid JSON.",
        ) from json_err
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Uploaded backup restore failed: {str(e)}",
        ) from e


@backup_router.get("/download/{filename}")
async def download_backup_file(filename: str) -> FileResponse:
    """Download specified backup snapshot file."""
    safe_filename = os.path.basename(filename)
    backup_dir = ensure_backup_dir()
    file_path = os.path.join(backup_dir, safe_filename)

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backup snapshot '{safe_filename}' not found.",
        )

    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type="application/json",
    )


@backup_router.delete("/delete/{filename}")
async def delete_backup(
    filename: str,
    backup_service: BackupService = Depends(get_backup_service),
) -> dict[str, str]:
    """Delete a specific snapshot file from local backup directory."""
    try:
        backup_service.delete_backup(filename)
        return {"status": "success", "message": f"Deleted {filename}"}
    except FileNotFoundError as fnf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(fnf),
        ) from fnf
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        ) from val_err
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete backup file: {str(e)}",
        ) from e
