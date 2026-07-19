"""
Capture portfolio screenshots of the Bella Keys UI in both light and dark themes.

Output directories are derived automatically from the UI version in
keys-personal-assist-ui/package.json:
  - docs/screens/v<major>.<minor>/light/
  - docs/screens/v<major>.<minor>/dark/

After a successful capture, docs/screens/latest/ is replaced with a copy of
the versioned folder so that the portfolio page always reads the latest snapshot
without any manual pointer change.

The script refuses to overwrite an existing versioned folder. Bump the UI version
in package.json before re-running.

Prerequisites (one-time):
    uv sync
    uv run playwright install chromium

Usage (run from scripts/screenshots/ with the full dev stack already running):
    uv run capture_screens.py

Env var overrides:
    BASE_URL           default: http://localhost:3000
    SCREENSHOT_USER    default: demo
    SCREENSHOT_PASS    default: demo
"""

import asyncio
import json
import shutil
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import BrowserContext, Page, async_playwright

import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
USER     = os.getenv("SCREENSHOT_USER", "demo")
PASS_    = os.getenv("SCREENSHOT_PASS", "demo")

# Resolve repo root relative to this script
_SCRIPT_DIR = Path(__file__).parent
_REPO_ROOT  = _SCRIPT_DIR.parent.parent

# Read app version from the UI package.json
_PKG_JSON   = _REPO_ROOT / "keys-personal-assist-ui" / "package.json"
_UI_VERSION = json.loads(_PKG_JSON.read_text(encoding="utf-8"))["version"]
_MAJOR_MINOR = ".".join(_UI_VERSION.split(".")[:2])  # e.g. "1.9" from "1.9.0"

SCREENS_ROOT = _REPO_ROOT / "docs" / "screens"
OUT_DIR      = SCREENS_ROOT / f"v{_MAJOR_MINOR}"
LATEST_DIR   = SCREENS_ROOT / "latest"

# User journey declaration.
# Each section groups related screens under a named flow with a colour accent
# used on the portfolio page. Each step has:
#   slug        : semantic filename (no number prefix)
#   route       : client-side route to navigate to
#   tab         : MUI Tab label to click, or None
#   scroll_y    : pixels to scroll before capturing
#   description : human-readable caption shown on the portfolio page
JOURNEY = [
    {
        "id": "auth",
        "label": "Authentication",
        "color": "#6366f1",
        "steps": [
            {
                "slug": "login",
                "route": "/login",
                "tab": None,
                "scroll_y": 0,
                "description": "Secure OAuth 2.1 SSO login page — the first touchpoint of every session.",
            },
            {
                "slug": "login-consent",
                "route": "/login",
                "tab": None,
                "scroll_y": 0,
                "description": "OAuth 2.1 SSO Consent & Authorization portal.",
            },
        ],
    },
    {
        "id": "dashboard",
        "label": "Dashboard",
        "color": "#0ea5e9",
        "steps": [
            {
                "slug": "home",
                "route": "/",
                "tab": None,
                "scroll_y": 0,
                "description": "Hero landing page showing financial health at a glance.",
            },
            {
                "slug": "spending-accounts",
                "route": "/dashboard/accounts",
                "tab": None,
                "scroll_y": 0,
                "description": "Spending account summary with balance trends and quick-add transactions.",
            },
            {
                "slug": "savings-envelopes",
                "route": "/dashboard/envelopes",
                "tab": None,
                "scroll_y": 0,
                "description": "Savings envelope overview with allocation donut chart.",
            },
            {
                "slug": "savings-envelopes-transactions",
                "route": "/dashboard/envelopes",
                "tab": None,
                "scroll_y": 600,
                "description": "Savings envelope transaction ledger scrolled into view.",
            },
        ],
    },
    {
        "id": "budget",
        "label": "Monthly Budget",
        "color": "#10b981",
        "steps": [
            {
                "slug": "budget-checklist",
                "route": "/budget",
                "tab": None,
                "scroll_y": 0,
                "description": "Monthly budget checklist — planned vs actual spend per category.",
            },
            {
                "slug": "budget-visuals",
                "route": "/budget",
                "tab": "Visuals",
                "scroll_y": 0,
                "description": "Budget visualisation tab — pie chart breakdown of spending categories.",
            },
        ],
    },
    {
        "id": "wealth",
        "label": "Wealth Manager",
        "color": "#f59e0b",
        "steps": [
            {
                "slug": "wealth-assets",
                "route": "/wealth",
                "tab": "Assets",
                "scroll_y": 0,
                "description": "Assets tab — grouped table of investments with returns and allocation.",
            },
            {
                "slug": "wealth-liabilities",
                "route": "/wealth",
                "tab": "Liabilities",
                "scroll_y": 0,
                "description": "Liabilities tab — active loans with EMI schedules and outstanding balances.",
            },
            {
                "slug": "wealth-liabilities-charts",
                "route": "/wealth",
                "tab": "Liabilities",
                "scroll_y": 0,
                "description": "Payoff projection charts showing ideal vs actual debt reduction curves.",
            },
            {
                "slug": "wealth-liabilities-ledger",
                "route": "/wealth",
                "tab": "Liabilities",
                "scroll_y": 0,
                "description": "Transaction ledger modal for detailed liability repayment history.",
            },
            {
                "slug": "wealth-networth",
                "route": "/wealth",
                "tab": "Net Worth",
                "scroll_y": 0,
                "description": "Net worth timeline — composed chart of assets vs liabilities over time.",
            },
            {
                "slug": "wealth-allocation",
                "route": "/wealth",
                "tab": "Allocation",
                "scroll_y": 0,
                "description": "Portfolio allocation — category distribution, leverage, and health metrics.",
            },
        ],
    },
    {
        "id": "ai-chat",
        "label": "Bella AI Chat",
        "color": "#8b5cf6",
        "steps": [
            {
                "slug": "chat-empty",
                "route": "/chat",
                "tab": None,
                "scroll_y": 0,
                "description": "Bella AI chat in empty state — prompt suggestions and assistant branding.",
            },
            {
                "slug": "chat-conversation",
                "route": "/chat",
                "tab": None,
                "scroll_y": 0,
                "description": "Bella AI answering a financial query with context from the user's data.",
            },
        ],
    },
    {
        "id": "settings",
        "label": "Settings",
        "color": "#64748b",
        "steps": [
            {
                "slug": "settings-accounts",
                "route": "/settings",
                "tab": "Bank Accounts",
                "scroll_y": 0,
                "description": "Settings — bank accounts management panel.",
            },
            {
                "slug": "settings-categories",
                "route": "/settings?tab=categories",
                "tab": "Budget Categories",
                "scroll_y": 0,
                "description": "Settings — budget category configuration.",
            },
        ],
    },
]


async def set_theme(page: Page, theme: str) -> None:
    """Inject theme into localStorage so MUI ThemeProvider picks it up."""
    await page.evaluate(f"localStorage.setItem('theme-mode', '{theme}')")


async def shot(page: Page, out_dir: Path, slug: str, scroll_y: int = 0) -> None:
    """Wait for network idle, optionally scroll, then save a screenshot."""
    await page.wait_for_load_state("networkidle")
    if scroll_y:
        await page.evaluate(f"window.scrollTo(0, {scroll_y})")
        await page.wait_for_timeout(1000)
    else:
        await page.wait_for_timeout(500)
    dest = out_dir / f"{slug}.png"
    await page.screenshot(path=str(dest), full_page=False)
    print(f"  [OK]  {dest.relative_to(SCREENS_ROOT)}")


async def click_tab(page: Page, label: str) -> None:
    """Click a MUI Tab by its visible label and wait for repaint."""
    try:
        await page.get_by_role("tab").first.wait_for(state="attached", timeout=5000)
    except Exception:
        pass

    tabs = await page.get_by_role("tab").all()
    tab_names = []
    for t in tabs:
        try:
            name = await t.text_content()
            tab_names.append(name.strip() if name else "")
        except Exception:
            pass

    target = label.lower()
    clicked = False
    for i, t in enumerate(tabs):
        name = tab_names[i].lower() if i < len(tab_names) else ""
        if target in name:
            try:
                await t.click(timeout=5000)
                clicked = True
                break
            except Exception:
                pass

    if not clicked:
        try:
            await page.get_by_role("tab", name=label, exact=False).first.click(timeout=5000)
        except Exception:
            await page.get_by_text(label, exact=False).first.click()

    await page.wait_for_timeout(1200)


async def do_login(page: Page) -> None:
    """Perform SSO login and wait for the app home page to load."""
    await page.goto(f"{BASE_URL}/login")
    await page.wait_for_load_state("networkidle")
    await page.get_by_role("button", name="Sign In with SSO").click()
    await page.wait_for_url("**/oauth/authorize*", timeout=15000)
    await page.wait_for_load_state("networkidle")
    await page.locator('input[name="username"]').fill(USER)
    await page.locator('input[name="password"]').fill(PASS_)
    await page.locator("#authorize-submit-btn").click()
    await page.wait_for_url(
        lambda url: "/login" not in url and "/callback" not in url and "/oauth" not in url,
        timeout=15000,
    )
    await page.wait_for_load_state("networkidle")


def _navigate_to_section(section_id: str) -> dict:
    """Map a section id to its nav link label for UI-driven routing."""
    nav_labels = {
        "dashboard": None,       # handled per step
        "budget":    "Monthly Budget",
        "wealth":    "Wealth Manager",
        "ai-chat":   "Bella Chat",
        "settings":  None,       # handled specially (avatar menu)
    }
    return nav_labels.get(section_id)


async def capture_step(
    page: Page,
    out_dir: Path,
    section: dict,
    step: dict,
    theme: str,
    prev_section_id: str | None,
    prev_slug: str | None,
) -> bool:
    """Navigate to a step, capture the screenshot, and return True on success."""
    slug = step["slug"]
    section_id = section["id"]

    # Section-level navigation (only navigate when section changes or when
    # the step requires a different nav entry)
    if section_id == "dashboard":
        if slug == "home":
            await page.get_by_role("link", name="Home").first.click()
        elif slug == "spending-accounts":
            await page.get_by_role("link", name="Spending Accounts").first.click()
        elif slug in ("savings-envelopes", "savings-envelopes-transactions"):
            await page.get_by_role("link", name="Savings Envelopes").first.click()

    elif section_id == "budget":
        if prev_section_id != "budget":
            await page.get_by_role("link", name="Monthly Budget").first.click()

    elif section_id == "wealth":
        if prev_section_id != "wealth":
            await page.get_by_role("link", name="Wealth Manager").first.click()

    elif section_id == "ai-chat":
        if prev_section_id != "ai-chat":
            await page.get_by_role("link", name="Bella Chat").first.click()

    elif section_id == "settings":
        if "/settings" not in page.url:
            await page.locator(".MuiAvatar-root").first.click()
            await page.wait_for_timeout(300)
            await page.get_by_role("menuitem", name="Settings").first.click()

    await set_theme(page, theme)
    await page.wait_for_timeout(3000)

    if step["tab"]:
        await click_tab(page, step["tab"])
        await page.wait_for_timeout(4000)

    # Custom: expand Payoff Projections chart for the liabilities-charts step
    if slug == "wealth-liabilities-charts":
        try:
            await page.get_by_role("button", name="Toggle Payoff Projections").first.click()
            await page.wait_for_timeout(4000)
            await page.evaluate("""
                const el = [...document.querySelectorAll('p, span, h5, h6, div')].reverse()
                    .find(e => e.textContent.toLowerCase().includes('payoff curves: ideal vs actual'));
                if (el) {
                    el.scrollIntoView({ block: 'start', behavior: 'instant' });
                    window.scrollBy(0, -80);
                }
            """)
            await page.wait_for_timeout(1000)
        except Exception as exc:
            print(f"  [WARN] {slug}: failed to toggle payoff projections — {exc}")

    # Custom: open Transactions Ledger modal for the liabilities-ledger step
    elif slug == "wealth-liabilities-ledger":
        try:
            await page.get_by_role("button", name="Transactions Ledger").first.click()
            await page.wait_for_timeout(2000)
        except Exception as exc:
            print(f"  [WARN] {slug}: failed to open ledger modal — {exc}")

    # Custom: send a chat message and wait for the full AI response to stream in
    elif slug == "chat-conversation":
        # Mock the backend chat endpoint so we get a beautiful, reliable stream
        # without calling the actual LLM (which might fail due to placeholder keys)
        async def handle_chat_route(route):
            body = (
                'data: {"type": "thinking", "content": "Analyzing portfolio holdings..."}\n\n'
                'data: {"type": "tool_call", "id": "t1", "name": "get_wealth_summary", "label": "Querying Wealth Manager", "args": "{}", "is_sub_agent": false}\n\n'
                'data: {"type": "tool_result", "id": "t1", "name": "get_wealth_summary", "label": "Querying Wealth Manager", "content": "Success", "is_sub_agent": false}\n\n'
                'data: {"type": "response", "content": "Here is a quick summary of your portfolio:\\n\\n* **Current Net Worth:** \\u20b922,46,000 (INR)\\n* **Top Performing Assets:**\\n  - **HDFC Mid-Cap Fund:** +30.5% (Invested: \\u20b92,00,000, Current: \\u20b92,61,000)\\n  - **Nifty 50 Index Fund:** +28.4% (Invested: \\u20b95,00,000, Current: \\u20b96,42,000)\\n  - **Infosys Shares:** +26.0% (Invested: \\u20b91,50,000, Current: \\u20b91,89,000)\\n\\nYour overall asset allocation is healthy, with Equity leading growth and Debt/Real Estate providing stability."}\n\n'
                'data: {"type": "done"}\n\n'
            )
            await route.fulfill(
                status=200,
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive"
                },
                body=body
            )

        await page.route("**/v1/chat/", handle_chat_route)

        prompt = (
            "Give me a quick portfolio summary — "
            "what are my top performing assets and current net worth?"
        )
        await page.get_by_placeholder("Ask me anything...").fill(prompt)
        await page.keyboard.press("Enter")
        # Wait until the streaming pulse animation has stopped on all bubbles.
        # ChatMessage applies animation: pulse when isStreaming=true; once streaming
        # finishes the animation style is removed, so we poll for its absence.
        try:
            await page.wait_for_function(
                """() => {
                    const papers = document.querySelectorAll('.MuiPaper-root');
                    if (papers.length === 0) return false;
                    for (const el of papers) {
                        const anim = getComputedStyle(el).animationName;
                        if (anim && anim !== 'none' && anim.includes('pulse')) return false;
                    }
                    // Also ensure at least one non-empty assistant bubble exists
                    const bubbles = document.querySelectorAll('.MuiPaper-root p, .MuiPaper-root div');
                    return Array.from(bubbles).some(el => el.textContent && el.textContent.trim().length > 20);
                }""",
                timeout=45_000,
            )
            await page.wait_for_timeout(1_500)  # let final render settle
        except Exception as exc:
            print(f"  [WARN] {slug}: streaming wait timed out ({exc}); capturing current state")
            await page.wait_for_timeout(2_000)


    await shot(page, out_dir, slug, step["scroll_y"])

    # Dismiss ledger modal so it does not block subsequent screens
    if slug == "wealth-liabilities-ledger":
        try:
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(500)
        except Exception:
            pass

    return True


async def capture_theme(context: BrowserContext, theme: str) -> list[dict]:
    """Capture all journey steps for one theme. Returns list of step result dicts."""
    out_dir = OUT_DIR / theme
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n-- {theme.upper()} --")

    results = []

    # Capture the auth section (login and consent) before authenticating
    auth_section = next(s for s in JOURNEY if s["id"] == "auth")
    login_step = auth_section["steps"][0]
    consent_step = auth_section["steps"][1]
    
    login_page = await context.new_page()
    await login_page.goto(f"{BASE_URL}/login")
    await set_theme(login_page, theme)
    await login_page.reload()
    
    # Wait for the card selector to appear and zoom transition to finish
    await login_page.wait_for_selector(".MuiCard-root", state="visible", timeout=10000)
    await login_page.wait_for_timeout(1500)
    
    await shot(login_page, out_dir, login_step["slug"])
    
    # Click SSO button and wait for the consent (authorize) page
    await login_page.get_by_role("button", name="Sign In with SSO").click()
    await login_page.wait_for_url("**/oauth/authorize*", timeout=15000)
    await login_page.wait_for_load_state("networkidle")
    await login_page.wait_for_timeout(1500)  # Settle consent page rendering
    
    await shot(login_page, out_dir, consent_step["slug"])
    await login_page.close()
    
    results.append({"section_id": "auth", "slug": login_step["slug"], "captured": True})
    results.append({"section_id": "auth", "slug": consent_step["slug"], "captured": True})

    # Authenticate then capture all remaining sections
    page = await context.new_page()
    await page.goto(BASE_URL)
    await set_theme(page, theme)
    await do_login(page)

    prev_section_id: str | None = None
    prev_slug: str | None = None

    for section in JOURNEY:
        for step in section["steps"]:
            if section["id"] == "auth":
                continue  # already captured above

            try:
                captured = await capture_step(
                    page, out_dir, section, step, theme, prev_section_id, prev_slug
                )
                results.append({"section_id": section["id"], "slug": step["slug"], "captured": captured})
            except Exception as exc:
                print(f"  [ERR] {step['slug']}: {exc}")
                results.append({"section_id": section["id"], "slug": step["slug"], "captured": False})

            prev_section_id = section["id"]
            prev_slug = step["slug"]

    await page.close()
    return results


def _write_manifest(theme_results: dict[str, list[dict]]) -> None:
    """Write manifest.json summarising what was captured."""
    sections = []
    for section in JOURNEY:
        steps_out = []
        for step in section["steps"]:
            slug = step["slug"]
            files = {}
            captured = False
            for theme, results in theme_results.items():
                result = next((r for r in results if r["slug"] == slug), None)
                theme_captured = result["captured"] if result else False
                if theme_captured:
                    files[theme] = f"{theme}/{slug}.png"
                captured = captured or theme_captured
            steps_out.append({
                "slug": slug,
                "description": step["description"],
                "optional": step.get("optional", False),
                "captured": captured,
                "files": files,
            })
        sections.append({
            "id": section["id"],
            "label": section["label"],
            "color": section["color"],
            "steps": steps_out,
        })

    manifest = {
        "app": "Bella Keys",
        "version": _MAJOR_MINOR,
        "ui_version": _UI_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "themes": ["light", "dark"],
        "sections": sections,
    }
    manifest_path = OUT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\n[manifest] Written -> {manifest_path.relative_to(_REPO_ROOT)}")


def _write_readme(theme_results: dict[str, list[dict]]) -> None:
    """Write a generated README.md inside the versioned output folder."""
    total = sum(
        1 for results in theme_results.values()
        for r in results if r["captured"]
    )
    lines = [
        f"# Bella Keys v{_MAJOR_MINOR} — Screenshot Reference",
        "",
        f"> Auto-generated by `capture_screens.py` on "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"> UI version: `{_UI_VERSION}`  ",
        f"> Themes: light, dark  ",
        f"> Total screenshots: {total}",
        "",
        "## Screens",
        "",
        "| Slug | Section | Description |",
        "| --- | --- | --- |",
    ]
    for section in JOURNEY:
        for step in section["steps"]:
            lines.append(
                f"| `{step['slug']}` | {section['label']} | {step['description']} |"
            )
    lines += [
        "",
        "## File layout",
        "",
        "```",
        f"v{_MAJOR_MINOR}/",
        "├── light/",
        "│   └── <slug>.png",
        "├── dark/",
        "│   └── <slug>.png",
        "├── manifest.json",
        "└── README.md",
        "```",
    ]
    readme_path = OUT_DIR / "README.md"
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[readme]   Written -> {readme_path.relative_to(_REPO_ROOT)}")


def _refresh_latest() -> None:
    """Replace docs/screens/latest/ with a copy of the current versioned folder."""
    if LATEST_DIR.exists():
        shutil.rmtree(LATEST_DIR)
    shutil.copytree(OUT_DIR, LATEST_DIR)
    print(f"[latest]   Refreshed -> {LATEST_DIR.relative_to(_REPO_ROOT)}")


def _embed_manifest_in_html(manifest: dict) -> None:
    """Inject the manifest JSON inline into user-journey.html so the page works
    when opened directly from disk (file://) without any HTTP server."""
    import re
    html_path = SCREENS_ROOT / "user-journey.html"
    if not html_path.exists():
        print(f"[html]     Skipped — {html_path.name} not found at {html_path.parent}")
        return

    content = html_path.read_text(encoding="utf-8")
    manifest_json = json.dumps(manifest, ensure_ascii=False)
    new_line = f"const EMBEDDED_MANIFEST = {manifest_json};"
    updated = re.sub(
        r"const EMBEDDED_MANIFEST = \{.*?\};",
        new_line,
        content,
        flags=re.DOTALL,
    )
    html_path.write_text(updated, encoding="utf-8")
    print(f"[html]     Manifest embedded -> {html_path.relative_to(_REPO_ROOT)}")


async def main() -> None:
    # Guard: refuse to overwrite an existing versioned snapshot
    if OUT_DIR.exists():
        raise SystemExit(
            f"\n[ERROR] {OUT_DIR.relative_to(_REPO_ROOT)} already exists.\n"
            f"        Bump the UI version in keys-personal-assist-ui/package.json "
            f"before re-running, or delete the folder manually if this is intentional.\n"
        )
    OUT_DIR.mkdir(parents=True)

    theme_results: dict[str, list[dict]] = {}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        for theme in ("light", "dark"):
            ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
            theme_results[theme] = await capture_theme(ctx, theme)
            await ctx.close()
        await browser.close()

    _write_manifest(theme_results)
    _write_readme(theme_results)
    _refresh_latest()

    # Re-read the manifest we just wrote and embed it into user-journey.html
    manifest_data = json.loads((OUT_DIR / "manifest.json").read_text(encoding="utf-8"))
    _embed_manifest_in_html(manifest_data)

    total = len(list(OUT_DIR.rglob("*.png")))
    print(f"\nDone — {total} screenshots in {OUT_DIR.relative_to(_REPO_ROOT)}/")


if __name__ == "__main__":
    asyncio.run(main())
