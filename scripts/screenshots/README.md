# bella-screenshots

Playwright script that captures all Bella Keys UI screens in light and dark
themes for portfolio / release documentation.

**Output:** `docs/screens/v6.0/light/` and `docs/screens/v6.0/dark/`

## Setup (one-time)

```bash
uv sync
uv run playwright install chromium
```

## Run

```bash
# From this directory, with the UI dev server already running on http://localhost:3000
uv run capture_screens.py
```

## Env var overrides

| Variable | Default |
| --- | --- |
| `BASE_URL` | `http://localhost:3000` |
| `OUT_DIR` | `../../docs/screens/v6.0` |
| `SCREENSHOT_USER` | `demo` |
| `SCREENSHOT_PASS` | `demo` |

## Screens captured (17 per theme, 34 total)

| File | What it shows |
| --- | --- |
| `login.png` | Login page — login tab |
| `login-register.png` | Login page — register tab |
| `home.png` | Hero landing page |
| `dashboard-accounts.png` | Account summary table |
| `dashboard-accounts-cards.png` | Account stat cards (scrolled) |
| `budget-table.png` | Monthly budget — table tab |
| `budget-visuals.png` | Monthly budget — pie chart tab |
| `savings-overview.png` | Savings envelopes — donut chart |
| `savings-table.png` | Savings envelopes — transaction table |
| `wealth-assets.png` | Wealth — assets tab |
| `wealth-liabilities.png` | Wealth — liabilities tab |
| `wealth-networth.png` | Wealth — net worth tab |
| `wealth-allocation.png` | Wealth — allocation tab |
| `chat-empty.png` | AI chat — empty state |
| `chat-conversation.png` | AI chat — with a response *(skipped gracefully if backend is down)* |
| `settings-accounts.png` | Settings — accounts tab |
| `settings-categories.png` | Settings — categories tab |
