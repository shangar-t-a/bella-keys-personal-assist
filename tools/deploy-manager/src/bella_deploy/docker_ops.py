"""Docker Compose orchestration operations with Rich formatting."""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from rich.table import Table

from bella_deploy.constants import COMPOSE_FILENAME


def check_docker_available() -> Tuple[bool, str]:
    """Check if Docker and Docker Compose plugin are installed and reachable."""
    if not shutil.which("docker"):
        return False, "Docker CLI is not found in system PATH. Please install Docker."

    try:
        res = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            return False, "Docker Compose plugin is not installed or not working."
    except Exception as e:
        return False, f"Failed to invoke docker: {e}"

    return True, "Docker is available."


def build_compose_command(
    working_dir: Path,
    action: List[str],
    profiles: Optional[List[str]] = None,
) -> List[str]:
    """Construct docker compose command with compose file and active profiles."""
    cmd = ["docker", "compose", "-f", COMPOSE_FILENAME]
    if profiles:
        for profile in profiles:
            cmd.extend(["--profile", profile])
    cmd.extend(action)
    return cmd


def run_docker_command(
    working_dir: Path,
    action: List[str],
    profiles: Optional[List[str]] = None,
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    """Execute a Docker Compose command in the target working directory."""
    cmd = build_compose_command(working_dir, action, profiles)
    return subprocess.run(
        cmd,
        cwd=str(working_dir),
        capture_output=capture_output,
        text=True,
        check=False,
    )


def get_formatted_status_table(working_dir: Path, profiles: Optional[List[str]] = None) -> Table:
    """Run docker compose ps and format output into a Rich Table with colored status badges."""
    res = run_docker_command(
        working_dir,
        ["ps", "--format", "{{.Service}}\t{{.Name}}\t{{.Status}}\t{{.Ports}}"],
        profiles,
        capture_output=True,
    )

    table = Table(title="Production Service Status", header_style="bold cyan", border_style="dim")
    table.add_column("Service", style="bold white")
    table.add_column("Container Name", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Ports", style="dim cyan")

    if res.returncode != 0 or not res.stdout.strip():
        raw_res = run_docker_command(working_dir, ["ps"], profiles, capture_output=True)
        lines = [l for l in raw_res.stdout.splitlines() if l.strip()]
        if not lines:
            table.add_row("No active services", "-", "[yellow]Stopped / Not Created[/yellow]", "-")
            return table
        for line in lines[1:]:  # skip header
            parts = [p.strip() for p in line.split("   ") if p.strip()]
            if len(parts) >= 3:
                status_raw = parts[2]
                status_badge = _badge_for_status(status_raw)
                table.add_row(
                    parts[0],
                    parts[1] if len(parts) > 1 else "-",
                    status_badge,
                    parts[3] if len(parts) > 3 else "-",
                )
        return table

    for line in res.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            service = parts[0].strip()
            name = parts[1].strip()
            status_raw = parts[2].strip()
            ports = parts[3].strip() if len(parts) > 3 else "-"
            status_badge = _badge_for_status(status_raw)
            table.add_row(service, name, status_badge, ports)

    return table


def _badge_for_status(status_str: str) -> str:
    """Generate color badge string based on container status."""
    lower = status_str.lower()
    if "up" in lower or "running" in lower:
        return f"[bold green]● {status_str}[/bold green]"
    elif "exited" in lower or "dead" in lower:
        return f"[bold red]■ {status_str}[/bold red]"
    elif "restarting" in lower or "starting" in lower:
        return f"[bold yellow]▲ {status_str}[/bold yellow]"
    return f"[dim]{status_str}[/dim]"


def stream_logs(
    working_dir: Path,
    profiles: Optional[List[str]] = None,
    follow: bool = True,
    tail: Optional[int] = None,
) -> int:
    """Stream or tail docker compose logs with graceful Ctrl+C handling."""
    action = ["logs"]
    if follow:
        action.append("-f")
    if tail:
        action.extend(["--tail", str(tail)])

    cmd = build_compose_command(working_dir, action, profiles)
    try:
        proc = subprocess.Popen(cmd, cwd=str(working_dir))
        proc.wait()
        return proc.returncode
    except KeyboardInterrupt:
        print("\n[INFO] Stopped log streaming.")
        return 0
