"""Interactive Terminal UI with Rich and Questionary."""

import os
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from bella_deploy import __version__
from bella_deploy.config_ops import (
    check_remote_tool_version,
    ensure_configs,
    sync_env_variables,
)
from bella_deploy.constants import (
    COMPOSE_FILENAME,
    ENV_EXAMPLE_FILENAME,
    ENV_FILENAME,
    LABEL_AI_CHAT,
    LABEL_AI_CHAT_MONITOR,
    LABEL_EMS_ONLY,
    LABEL_UI_EMS,
    LABEL_UI_FULL,
    PACKAGE_NAME,
    PROFILE_AI_CHAT,
    PROFILE_MONITOR,
    PROFILE_UI,
    PROFILE_UI_EMS,
)
from bella_deploy.docker_ops import (
    check_docker_available,
    get_formatted_status_table,
    run_docker_command,
    stream_logs,
)

console = Console()

# Custom Questionary styling matching Azure / Modern CLI palette
custom_style = Style(
    [
        ("qmark", "fg:#00bcd4 bold"),
        ("question", "bold"),
        ("answer", "fg:#4caf50 bold"),
        ("pointer", "fg:#00bcd4 bold"),
        ("highlighted", "fg:#00bcd4 bold"),
        ("selected", "fg:#4caf50"),
        ("separator", "fg:#6c757d"),
        ("instruction", "fg:#6c757d"),
        ("text", ""),
        ("disabled", "fg:#858585 italic"),
    ]
)


def print_banner(
    active_label: str = "",
    upgrade_version: str = "",
    working_dir: Optional[Path] = None,
) -> None:
    """Render rich header banner with metadata."""
    title = f"[bold cyan]Bella Deploy Manager[/bold cyan] [dim]v{__version__}[/dim]"

    body = Text()
    if active_label:
        body.append("Active Profile: ", style="dim")
        body.append(f"{active_label}\n", style="bold white")
    if working_dir:
        body.append("Working Directory: ", style="dim")
        body.append(f"{working_dir}\n", style="cyan")

    panel = Panel(
        body,
        title=title,
        title_align="left",
        border_style="cyan",
        padding=(0, 1),
    )
    console.print(panel)

    if upgrade_version:
        upgrade_text = Text()
        upgrade_text.append(
            f"A newer version is available: v{upgrade_version} (Current: v{__version__})\n",
            style="bold yellow",
        )
        upgrade_text.append("To upgrade, run: ", style="dim")
        upgrade_text.append(f"uv tool upgrade {PACKAGE_NAME}", style="bold green")

        notice_panel = Panel(
            upgrade_text,
            title="[bold yellow]Update Available[/bold yellow]",
            border_style="yellow",
            padding=(0, 1),
        )
        console.print(notice_panel)


def clear_screen() -> None:
    """Clear terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def select_profiles(working_dir: Path) -> Tuple[List[str], str]:
    """Interactive arrow-key wizard to configure service profile and Web UI scope."""
    clear_screen()
    print_banner(working_dir=working_dir)

    choice = questionary.select(
        "Select Service Profile:",
        choices=[
            questionary.Choice(
                "EMS only          - Auth Service + Expense Manager [Default]",
                value="1",
            ),
            questionary.Choice(
                "AI Chat           - Auth + EMS + Bella Chat + Qdrant [Experimental]",
                value="2",
            ),
            questionary.Choice(
                "AI Chat + Monitor - Everything above + Phoenix Observability [Experimental]",
                value="3",
            ),
        ],
        style=custom_style,
    ).ask()

    if choice is None:
        sys.exit(0)

    profiles: List[str] = []
    ai_chat_enabled = False
    service_label = ""

    if choice == "2":
        profiles.append(PROFILE_AI_CHAT)
        ai_chat_enabled = True
        service_label = LABEL_AI_CHAT
    elif choice == "3":
        profiles.extend([PROFILE_AI_CHAT, PROFILE_MONITOR])
        ai_chat_enabled = True
        service_label = LABEL_AI_CHAT_MONITOR
    else:
        service_label = LABEL_EMS_ONLY

    enable_ui = questionary.confirm(
        "Enable the Web UI container?",
        default=False,
        style=custom_style,
    ).ask()

    if enable_ui:
        if ai_chat_enabled:
            ui_scope = questionary.select(
                "Which services should the Web UI expose?",
                choices=[
                    questionary.Choice("EMS only", value="1"),
                    questionary.Choice("EMS + AI Chat", value="2"),
                ],
                style=custom_style,
            ).ask()
            if ui_scope == "1":
                profiles.append(PROFILE_UI_EMS)
                service_label += LABEL_UI_EMS
            else:
                profiles.append(PROFILE_UI)
                service_label += LABEL_UI_FULL
        else:
            profiles.append(PROFILE_UI_EMS)
            service_label += LABEL_UI_EMS

    console.print(
        f"\n[green][SUCCESS][/green] Active Profile configured: [bold]{service_label}[/bold]"
    )
    time.sleep(0.8)
    return profiles, service_label


def run_interactive_menu(working_dir: Path) -> None:
    """Run full interactive terminal UI loop."""
    docker_ok, docker_msg = check_docker_available()
    if not docker_ok:
        console.print(f"[red][ERROR][/red] {docker_msg}")
        sys.exit(1)

    # Check for remote tool version
    upgrade_version = check_remote_tool_version(__version__) or ""

    # Ensure deployment configs exist in working directory
    compose_file = working_dir / COMPOSE_FILENAME
    if not compose_file.exists():
        clear_screen()
        print_banner(upgrade_version=upgrade_version, working_dir=working_dir)
        console.print(
            f"[yellow][INFO][/yellow] `{COMPOSE_FILENAME}` not found in [cyan]{working_dir}[/cyan]"
        )
        console.print(
            "[dim][INFO] Initializing production configuration from repository...[/dim]"
        )
        ok, msg = ensure_configs(working_dir)
        if not ok:
            console.print(f"[red][ERROR][/red] {msg}")
            sys.exit(1)
        console.print(f"[green][SUCCESS][/green] {msg}")
        time.sleep(1)

    # Initial profile selection
    profiles, service_label = select_profiles(working_dir)

    while True:
        clear_screen()
        print_banner(
            active_label=service_label,
            upgrade_version=upgrade_version,
            working_dir=working_dir,
        )

        action = questionary.select(
            "Select an action:",
            choices=[
                questionary.Choice("🚀 Start Services", value="start"),
                questionary.Choice("🛑 Stop Services", value="stop"),
                questionary.Choice(
                    "📜 View Live Service Logs (Stream)", value="logs_live"
                ),
                questionary.Choice(
                    "📑 View Recent Service Logs (Last 100 lines)", value="logs_tail"
                ),
                questionary.Choice("🔄 Restart Services", value="restart"),
                questionary.Choice("📊 Check Service Status", value="status"),
                questionary.Choice(
                    "⚡ Update Deployment & Configs (Sync files, .env & pull images)",
                    value="update",
                ),
                questionary.Choice(
                    "⚙️  Change Service Profile / Web UI Scope", value="profile"
                ),
                questionary.Choice("🚪 Exit", value="exit"),
            ],
            style=custom_style,
        ).ask()

        if action is None or action == "exit":
            console.print(
                f"\n[cyan][LOG][/cyan] Exiting Bella Deploy Manager. Have a great day!\n"
            )
            break

        elif action == "start":
            console.print(
                f"\n[cyan][LOG][/cyan] Starting containers for profile: [bold]{service_label}[/bold]..."
            )
            with console.status("[bold green]Starting containers..."):
                res = run_docker_command(working_dir, ["up", "-d"], profiles)
            if res.returncode == 0:
                console.print("[green][SUCCESS][/green] Services started successfully.")
            else:
                console.print("[red][ERROR][/red] Failed to start services.")
            questionary.press_any_key_to_continue().ask()

        elif action == "stop":
            console.print(f"\n[cyan][LOG][/cyan] Stopping active containers...")
            with console.status("[bold yellow]Stopping containers..."):
                res = run_docker_command(working_dir, ["stop"], profiles)
            if res.returncode == 0:
                console.print("[green][SUCCESS][/green] Services stopped.")
            else:
                console.print("[red][ERROR][/red] Failed to stop services.")
            questionary.press_any_key_to_continue().ask()

        elif action == "logs_live":
            console.print(
                f"\n[cyan][LOG][/cyan] Streaming live service logs ([bold yellow]Press Ctrl+C to return[/bold yellow])...\n"
            )
            stream_logs(working_dir, profiles, follow=True)
            questionary.press_any_key_to_continue().ask()

        elif action == "logs_tail":
            console.print(f"\n[cyan][LOG][/cyan] Fetching last 100 log lines...\n")
            stream_logs(working_dir, profiles, follow=False, tail=100)
            questionary.press_any_key_to_continue().ask()

        elif action == "restart":
            console.print(f"\n[cyan][LOG][/cyan] Restarting services...")
            with console.status("[bold green]Restarting containers..."):
                res = run_docker_command(working_dir, ["restart"], profiles)
            if res.returncode == 0:
                console.print("[green][SUCCESS][/green] Services restarted.")
            else:
                console.print("[red][ERROR][/red] Failed to restart services.")
            questionary.press_any_key_to_continue().ask()

        elif action == "status":
            console.print(f"\n[cyan][LOG][/cyan] Active Container Status:\n")
            table = get_formatted_status_table(working_dir, profiles)
            console.print(table)
            console.print()
            questionary.press_any_key_to_continue().ask()

        elif action == "update":
            clear_screen()
            print_banner(
                active_label=service_label,
                upgrade_version=upgrade_version,
                working_dir=working_dir,
            )
            console.print(
                "[bold]Updating Production Deployment & Configurations[/bold]\n"
            )

            console.print(
                "[cyan][LOG][/cyan] Step 1/3: Downloading latest production configuration..."
            )
            with console.status("[bold cyan]Fetching remote configs..."):
                ok, msg = ensure_configs(working_dir, force_download=True)
            if not ok:
                console.print(f"[red][ERROR][/red] {msg}")
                questionary.press_any_key_to_continue().ask()
                continue
            console.print(
                f"[green][SUCCESS][/green] Latest configuration files downloaded.\n"
            )

            console.print(
                "[cyan][LOG][/cyan] Step 2/3: Syncing .env with new configuration keys..."
            )
            added = sync_env_variables(
                working_dir / ENV_FILENAME, working_dir / ENV_EXAMPLE_FILENAME
            )
            if added > 0:
                console.print(
                    f"[green][SUCCESS][/green] Updated .env with {added} new variables.\n"
                )
            else:
                console.print("[dim][INFO] .env is fully up to date.[/dim]\n")

            console.print(
                "[cyan][LOG][/cyan] Step 3/3: Pulling latest Docker images and recreating containers..."
            )
            with console.status(
                "[bold green]Pulling images & recreating containers..."
            ):
                run_docker_command(working_dir, ["pull"], profiles)
                up_res = run_docker_command(
                    working_dir, ["up", "-d", "--remove-orphans"], profiles
                )

            if up_res.returncode == 0:
                console.print(
                    "\n[green][SUCCESS][/green] Production deployment updated successfully!"
                )
            else:
                console.print(
                    "\n[red][ERROR][/red] Failed to recreate containers. Please check status or logs."
                )

            questionary.press_any_key_to_continue().ask()

        elif action == "profile":
            profiles, service_label = select_profiles(working_dir)
