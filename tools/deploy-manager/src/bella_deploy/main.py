"""CLI entry point and subcommand dispatcher for bella-deploy."""

import argparse
import sys
from pathlib import Path
from typing import List

from bella_deploy import __version__
from bella_deploy.config_ops import ensure_configs, sync_env_variables
from bella_deploy.constants import (
    CLI_COMMAND,
    COMPOSE_FILENAME,
    DEFAULT_DIR_NAME,
    ENV_EXAMPLE_FILENAME,
    ENV_FILENAME,
    PROFILE_AI_CHAT,
    PROFILE_MONITOR,
    PROFILE_UI,
    PROFILE_UI_EMS,
)
from bella_deploy.docker_ops import (
    check_docker_available,
    run_docker_command,
    stream_logs,
)
from bella_deploy.menu import run_interactive_menu


def parse_profiles(profile_arg: str, with_ui: bool, ui_scope: str) -> List[str]:
    """Resolve CLI profile and UI flags into Docker Compose profile arguments."""
    profiles: List[str] = []
    if profile_arg == PROFILE_AI_CHAT:
        profiles.append(PROFILE_AI_CHAT)
    elif profile_arg == PROFILE_MONITOR:
        profiles.extend([PROFILE_AI_CHAT, PROFILE_MONITOR])

    if with_ui:
        if ui_scope == "ems":
            profiles.append(PROFILE_UI_EMS)
        else:
            profiles.append(PROFILE_UI)
    return profiles


def get_default_deployment_dir() -> Path:
    """Resolve default deployment directory: cwd if docker-compose.prod.yaml exists, otherwise ~/.bella."""
    cwd = Path.cwd()
    if (cwd / COMPOSE_FILENAME).exists():
        return cwd
    default_dir = Path.home() / DEFAULT_DIR_NAME
    default_dir.mkdir(parents=True, exist_ok=True)
    return default_dir


def main() -> None:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog=CLI_COMMAND,
        description="Bella Keys - Production Deployment & Container Management CLI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=get_default_deployment_dir(),
        help="Target deployment directory (defaults to ~/.bella or current directory if compose file present)",
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Deployment subcommands"
    )

    # Common profile arguments
    def add_profile_args(sub: argparse.ArgumentParser) -> None:
        sub.add_argument(
            "--profile",
            choices=["ems", PROFILE_AI_CHAT, PROFILE_MONITOR],
            default="ems",
            help="Service profile (default: ems)",
        )
        sub.add_argument(
            "--with-ui",
            action="store_true",
            help="Enable Web UI container",
        )
        sub.add_argument(
            "--ui-scope",
            choices=["ems", "full"],
            default="full",
            help="Web UI exposure scope (default: full)",
        )

    # Subcommand: start
    p_start = subparsers.add_parser(
        "start", help="Start production containers"
    )
    add_profile_args(p_start)

    # Subcommand: stop
    p_stop = subparsers.add_parser("stop", help="Stop production containers")
    add_profile_args(p_stop)

    # Subcommand: restart
    p_restart = subparsers.add_parser(
        "restart", help="Restart production containers"
    )
    add_profile_args(p_restart)

    # Subcommand: status
    p_status = subparsers.add_parser(
        "status", help="Check active container status"
    )
    add_profile_args(p_status)

    # Subcommand: logs
    p_logs = subparsers.add_parser("logs", help="View service logs")
    add_profile_args(p_logs)
    p_logs.add_argument(
        "-f", "--follow", action="store_true", help="Follow live log stream"
    )
    p_logs.add_argument(
        "--tail",
        type=int,
        default=None,
        help="Number of recent lines to display",
    )

    # Subcommand: update
    p_update = subparsers.add_parser(
        "update",
        help="Download latest configs, sync .env, pull latest images, and restart containers",
    )
    add_profile_args(p_update)

    # Subcommand: menu
    subparsers.add_parser(
        "menu", help="Launch interactive production manager menu"
    )

    args = parser.parse_args()
    working_dir = args.dir.resolve()

    if not args.command or args.command == "menu":
        run_interactive_menu(working_dir)
        return

    docker_ok, docker_msg = check_docker_available()
    if not docker_ok:
        print(f"[ERROR] {docker_msg}")
        sys.exit(1)

    profiles = parse_profiles(
        getattr(args, "profile", "ems"),
        getattr(args, "with-ui", False),
        getattr(args, "ui_scope", "full"),
    )

    if args.command == "start":
        ensure_configs(working_dir)
        print(
            f"[LOG] Starting containers with profiles: {profiles or 'default ems'}..."
        )
        res = run_docker_command(working_dir, ["up", "-d"], profiles)
        sys.exit(res.returncode)

    elif args.command == "stop":
        print("[LOG] Stopping containers...")
        res = run_docker_command(working_dir, ["stop"], profiles)
        sys.exit(res.returncode)

    elif args.command == "restart":
        print("[LOG] Restarting containers...")
        res = run_docker_command(working_dir, ["restart"], profiles)
        sys.exit(res.returncode)

    elif args.command == "status":
        res = run_docker_command(working_dir, ["ps"], profiles)
        sys.exit(res.returncode)

    elif args.command == "logs":
        code = stream_logs(
            working_dir,
            profiles,
            follow=args.follow,
            tail=args.tail,
        )
        sys.exit(code)

    elif args.command == "update":
        print("[LOG] Step 1/3: Downloading latest production configuration...")
        ok, msg = ensure_configs(working_dir, force_download=True)
        if not ok:
            print(f"[ERROR] {msg}")
            sys.exit(1)

        print("[LOG] Step 2/3: Syncing .env configuration keys...")
        sync_env_variables(
            working_dir / ENV_FILENAME, working_dir / ENV_EXAMPLE_FILENAME
        )

        print("[LOG] Step 3/3: Pulling Docker images and recreating containers...")
        run_docker_command(working_dir, ["pull"], profiles)
        res = run_docker_command(
            working_dir, ["up", "-d", "--remove-orphans"], profiles
        )
        if res.returncode == 0:
            print("[SUCCESS] Production deployment updated successfully!")
        sys.exit(res.returncode)


if __name__ == "__main__":
    main()
