"""
Capture portfolio screenshots of the Bella Keys UI in both light and dark themes.
Outputs to docs/screens/v6.0/light/ and docs/screens/v6.0/dark/.

Prerequisites (one-time):
    uv sync
    uv run playwright install chromium

Usage (run from scripts/screenshots/ with the UI dev server already on http://localhost:3000):
    uv run capture_screens.py

Env var overrides:
    BASE_URL           default: http://localhost:3000
    OUT_DIR            default: ../../docs/screens/v6.0
    SCREENSHOT_USER    default: demo
    SCREENSHOT_PASS    default: demo
"""

import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
OUT_DIR  = Path(os.getenv("OUT_DIR", "../../docs/screens/v6.0"))
USER     = os.getenv("SCREENSHOT_USER", "demo")
PASS_    = os.getenv("SCREENSHOT_PASS", "demo")

# Each entry: (output filename, route, tab label to click or None, scroll_y in px)
SCREENS = [
    ("01-login",                    "/login",                   None,          0),
    ("02-login-register",           "/login",                   "Sign Up",     0),
    ("03-home",                     "/",                        None,          0),
    ("04-spending-accounts",        "/dashboard/accounts",      None,          0),
    ("05-savings-envelopes",        "/dashboard/envelopes",     None,          0),
    ("06-savings-envelopes-txs",    "/dashboard/envelopes",     None,          600),
    ("07-budget-checklist",         "/budget",                  None,          0),
    ("08-budget-visuals",           "/budget",                  "Visuals",     0),
    ("09-wealth-assets",            "/wealth",                  "Assets",      0),
    ("10-wealth-liabilities",       "/wealth",                  "Liabilities", 0),
    ("11-wealth-liabilities-charts", "/wealth",                 "Liabilities", 0),  # Handled with custom payoff toggle
    ("12-wealth-liabilities-ledger", "/wealth",                 "Liabilities", 0),  # Handled with custom ledger toggle
    ("13-wealth-networth",          "/wealth",                  "Net Worth",   0),
    ("14-wealth-allocation",        "/wealth",                  "Allocation",  0),
    ("15-chat-empty",               "/chat",                    None,          0),
    ("16-chat-conversation",        "/chat",                    None,          0),  # handled separately
    ("17-settings-accounts",        "/settings",                "Bank Accounts",    0),
    ("18-settings-categories",      "/settings?tab=categories", "Budget Categories", 0),
]


async def set_theme(page: Page, theme: str) -> None:
    """Inject theme into localStorage so MUI ThemeProvider picks it up."""
    await page.evaluate(f"localStorage.setItem('theme-mode', '{theme}')")


async def shot(page: Page, out_dir: Path, name: str, scroll_y: int = 0) -> None:
    """Wait for network idle, optionally scroll, then save a screenshot."""
    await page.wait_for_load_state("networkidle")
    if scroll_y:
        await page.evaluate(f"window.scrollTo(0, {scroll_y})")
        await page.wait_for_timeout(1000)  # Wait for scrolling animation to settle
    else:
        await page.wait_for_timeout(500)   # Wait general render settle
    dest = out_dir / f"{name}.png"
    await page.screenshot(path=str(dest), full_page=False)
    print(f"  [OK]  {dest.relative_to(OUT_DIR.parent.parent)}")


async def click_tab(page: Page, label: str) -> None:
    """Click a MUI Tab by its visible label and wait for repaint."""
    try:
        # Wait a moment for tabs to be attached/visible
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
    
    # Check if the target label matches any tab name (case-insensitive substring)
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
        # Fallback to regular role selector or text selector
        try:
            await page.get_by_role("tab", name=label, exact=False).first.click(timeout=5000)
        except Exception:
            await page.get_by_text(label, exact=False).first.click()
            
    await page.wait_for_timeout(1200)  # Wait for tab transition/chart animations to finish completely


async def do_login(page: Page) -> None:
    await page.goto(f"{BASE_URL}/login")
    await page.wait_for_load_state("networkidle")
    await page.get_by_label("Username").fill(USER)
    await page.get_by_label("Password").fill(PASS_)
    await page.get_by_role("button", name="Log In").click()
    # App uses window.location.href with 800ms delay — wait for navigation to settle
    await page.wait_for_timeout(2500)
    await page.wait_for_load_state("networkidle", timeout=10_000)


async def capture_theme(context: BrowserContext, theme: str) -> None:
    out_dir = OUT_DIR / theme
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n-- {theme.upper()} --")

    # --- Login screenshots FIRST (context has no auth token yet) ---
    login_page = await context.new_page()
    # Visit root first to initialize origin/localStorage
    await login_page.goto(BASE_URL)
    await set_theme(login_page, theme)
    # Navigate to login so it mounts with the correct theme
    await login_page.goto(f"{BASE_URL}/login")
    await login_page.wait_for_load_state("networkidle")
    await shot(login_page, out_dir, "01-login")
    await click_tab(login_page, "Sign Up")
    await shot(login_page, out_dir, "02-login-register")
    await login_page.close()

    # --- Authenticate, then capture all remaining screens ---
    page = await context.new_page()
    await page.goto(BASE_URL)
    await set_theme(page, theme)
    await do_login(page)
    for name, route, tab, scroll_y in SCREENS:
        # Skip login files as they were done above
        if name.endswith("login") or name.endswith("login-register"):
            continue

        if name.endswith("chat-conversation"):
            try:
                await page.get_by_placeholder("Ask Bella anything...").fill("Give me a quick summary")
                await page.keyboard.press("Enter")
                await page.wait_for_timeout(5_000)
                await shot(page, out_dir, name)
            except Exception as exc:
                print(f"  [SKIP]  {name} skipped -- {exc}")
            continue

        # Navigate using UI link clicks for 100% reliable client-side routing
        if name.endswith("home"):
            await page.get_by_role("link", name="Home").first.click()
        elif name.startswith("04-spending"):
            await page.get_by_role("link", name="Spending Accounts").first.click()
        elif name.startswith("05-savings") or name.startswith("06-savings"):
            await page.get_by_role("link", name="Savings Envelopes").first.click()
        elif name.startswith("07-budget") or name.startswith("08-budget"):
            await page.get_by_role("link", name="Monthly Budget").first.click()
        elif name.startswith("09-wealth") or name.startswith("10-wealth") or name.startswith("11-wealth") or name.startswith("12-wealth") or name.startswith("13-wealth") or name.startswith("14-wealth"):
            await page.get_by_role("link", name="Wealth Manager").first.click()
        elif name.startswith("15-chat") or name.startswith("16-chat"):
            await page.get_by_role("link", name="Bella Chat").first.click()
        elif name.startswith("17-settings") or name.startswith("18-settings"):
            # Only navigate to settings if we aren't already there
            if "/settings" not in page.url:
                await page.locator(".MuiAvatar-root").first.click()
                await page.wait_for_timeout(300)
                await page.get_by_role("menuitem", name="Settings").first.click()
        
        # Settle theme & DOM updates
        await set_theme(page, theme)
        await page.wait_for_timeout(3000)  # Give enough time for chart animations to finish rendering completely

        if tab:
            await click_tab(page, tab)
            # Extra wait for tab-specific charts to fully render and animate
            await page.wait_for_timeout(4000)

        # Custom logic: expand Payoff Projections for the liabilities charts screen
        if name.startswith("11-wealth-liabilities-charts"):
            try:
                # Toggle payoff projections chart
                await page.get_by_role("button", name="Toggle Payoff Projections").first.click()
                await page.wait_for_timeout(4000)  # Wait for projections computation and chart animation
                
                # Scroll the Payoff Curves chart title into view to center the line chart
                await page.evaluate("""
                    const el = [...document.querySelectorAll('p, span, h5, h6, div')].reverse().find(e => e.textContent.toLowerCase().includes('payoff curves: ideal vs actual'));
                    if (el) {
                        el.scrollIntoView({ block: 'start', behavior: 'instant' });
                        window.scrollBy(0, -80);
                    }
                """)
                await page.wait_for_timeout(1000)  # Wait for scroll to settle
            except Exception as exc:
                print(f"  [WARN] Failed to toggle payoff projections: {exc}")

        # Custom logic: open Transactions Ledger modal for liabilities ledger screen
        elif name.startswith("12-wealth-liabilities-ledger"):
            try:
                # Open ledger modal
                await page.get_by_role("button", name="Transactions Ledger").first.click()
                await page.wait_for_timeout(2000)  # Wait for modal expansion animation
            except Exception as exc:
                print(f"  [WARN] Failed to open ledger modal: {exc}")

        await shot(page, out_dir, name, scroll_y)

        # Close ledger modal if opened so it does not block subsequent screens
        if name.startswith("12-wealth-liabilities-ledger"):
            try:
                # Click backdrop or escape key to dismiss modal
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(500)
            except Exception:
                pass

    await page.close()


async def main() -> None:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        for theme in ("light", "dark"):
            ctx = await browser.new_context(viewport={"width": 1440, "height": 900})
            await capture_theme(ctx, theme)
            await ctx.close()
        await browser.close()

    total = len(list(OUT_DIR.rglob("*.png")))
    print(f"\nDone — {total} screenshots in {OUT_DIR}/")


if __name__ == "__main__":
    asyncio.run(main())
