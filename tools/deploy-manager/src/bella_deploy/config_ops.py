"""Configuration and remote synchronization operations."""

import re
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

from bella_deploy.constants import (
    COMPOSE_FILENAME,
    ENV_EXAMPLE_FILENAME,
    ENV_FILENAME,
    REPO_COMPOSE_URL,
    REPO_ENV_URL,
    REPO_PYPROJECT_URL,
    REPO_SQL_URL,
    SQL_INIT_FILENAME,
)


def fetch_url(url: str, timeout: int = 10, retries: int = 3) -> bytes:
    """Fetch content from a remote URL with retries."""
    headers = {"User-Agent": "bella-deploy-tool"}
    req = urllib.request.Request(url, headers=headers)
    last_error: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    return response.read()
        except Exception as e:
            last_error = e

    if last_error:
        raise last_error
    raise RuntimeError(f"Failed to fetch {url}")


def download_file(url: str, destination: Path) -> bool:
    """Download a remote file atomically using a temporary file."""
    tmp_path = destination.with_suffix(destination.suffix + ".tmp")
    try:
        data = fetch_url(url)
        with open(tmp_path, "wb") as f:
            f.write(data)
        shutil.move(str(tmp_path), str(destination))
        return True
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        return False


def check_remote_tool_version(current_version: str) -> Optional[str]:
    """Check if a newer version of bella-deploy-manager exists remotely."""
    try:
        raw_data = fetch_url(REPO_PYPROJECT_URL, timeout=5, retries=1).decode("utf-8")
        match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', raw_data)
        if match:
            remote_version = match.group(1).strip()
            if _parse_version(remote_version) > _parse_version(current_version):
                return remote_version
    except Exception:
        pass
    return None


def _parse_version(v: str) -> Tuple[int, ...]:
    """Parse semver-like string into tuple of ints for comparison."""
    clean = re.sub(r"[^\d.]", "", v)
    parts = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def sync_env_variables(env_path: Path, example_path: Path) -> int:
    """Sync missing configuration keys from .env.example into .env without overwriting existing values."""
    if not env_path.exists() or not example_path.exists():
        return 0

    with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
        existing_lines = f.readlines()

    with open(example_path, "r", encoding="utf-8", errors="ignore") as f:
        example_lines = f.readlines()

    existing_keys = set()
    for line in existing_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            existing_keys.add(key)

    added_count = 0
    lines_to_append = []
    for line in example_lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key not in existing_keys:
                lines_to_append.append(line)
                existing_keys.add(key)
                added_count += 1

    if lines_to_append:
        with open(env_path, "a", encoding="utf-8") as f:
            if existing_lines and not existing_lines[-1].endswith("\n"):
                f.write("\n")
            f.write("\n# --- Automatically added by bella-deploy update ---\n")
            for line in lines_to_append:
                f.write(line if line.endswith("\n") else line + "\n")

    return added_count


def ensure_configs(working_dir: Path, force_download: bool = False) -> Tuple[bool, str]:
    """Ensure production deployment files are present in the target directory."""
    compose_path = working_dir / COMPOSE_FILENAME
    env_example_path = working_dir / ENV_EXAMPLE_FILENAME
    env_path = working_dir / ENV_FILENAME
    sql_path = working_dir / SQL_INIT_FILENAME

    # Download compose file
    if force_download or not compose_path.exists():
        if not download_file(REPO_COMPOSE_URL, compose_path):
            return False, f"Failed to download {COMPOSE_FILENAME}"

    # Download env.example
    if force_download or not env_example_path.exists():
        if not download_file(REPO_ENV_URL, env_example_path):
            return False, f"Failed to download {ENV_EXAMPLE_FILENAME}"

    # Initialize .env if missing
    if not env_path.exists():
        if env_example_path.exists():
            shutil.copyfile(str(env_example_path), str(env_path))

    # Download init-db-prod.sql if missing
    if not sql_path.exists():
        download_file(REPO_SQL_URL, sql_path)

    return True, "Configuration files synchronized."
