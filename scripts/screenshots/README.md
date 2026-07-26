# bella-screenshots

Playwright script that captures all Bella Keys UI screens in light and dark
themes for portfolio and release documentation.

**Output:** `docs/screens/v<major>.<minor>/light/` and `dark/`  
**Portfolio page:** `docs/screens/user-journey.html`

## Setup (one-time)

```bash
uv sync
uv run playwright install chromium
```

## Run (Automated Orchestration)

The easiest way to run the entire pipeline is using the automated capture runner script. It starts the dev services in Docker, waits for them to be healthy, seeds portfolio-quality demo data directly to the database, runs the capture script, and stops the stack when finished:

```bash
# From the repo root, run the orchestrator:
bash scripts/screenshots/run_capture.sh
```

### Script Options

- `--keep-up`: Keep the docker-compose stack running after capture finishes (great for local testing and debugging).
- `--skip-seed`: Skip database seeding (use the existing database state).

## Manual Steps (Detailed Run)

If you already have your services running locally and want to run individual steps manually:

1. **Seed Demo Data** (idempotent seeder):
   ```bash
   # Make sure EMS database is accessible
   uv run scripts/screenshots/seed_demo_data.py
   ```

2. **Capture Screens**:
   ```bash
   # From scripts/screenshots/ directory
   uv run capture_screens.py
   ```


## Versioning behaviour

The script reads the version from `keys-personal-assist-ui/package.json` and
derives the output directory automatically (e.g. `1.9.0` → `docs/screens/v1.9/`).

- **Versioned snapshot** (`docs/screens/v1.9/`) — written once per version.
  The script raises an error if the folder already exists so you cannot
  accidentally overwrite a release snapshot. Bump the UI version in
  `package.json` before re-running.
- **Latest copy** (`docs/screens/latest/`) — replaced with a copy of the new
  versioned snapshot on every successful run. The portfolio HTML page always
  reads from `latest/`.

To pin a capture to a named release, copy `latest/` after the run:

```bash
cp -r docs/screens/latest docs/screens/v2.0
```

## Env var overrides

| Variable | Default |
| --- | --- |
| `BASE_URL` | `http://localhost:3000` |
| `SCREENSHOT_USER` | `demo` |
| `SCREENSHOT_PASS` | `demo` |

## Journey sections and slugs

Screens are declared in the `JOURNEY` list inside `capture_screens.py` as
structured sections. The table below reflects the current manifest.

| Section | Slug | Description |
| --- | --- | --- |
| Authentication | `login` | Secure SSO login page |
| Dashboard | `home` | Hero landing page |
| Dashboard | `spending-accounts` | Spending account summary |
| Dashboard | `savings-envelopes` | Savings envelope overview |
| Dashboard | `savings-envelopes-transactions` | Savings transaction ledger (scrolled) |
| Monthly Budget | `budget-checklist` | Planned vs actual spend |
| Monthly Budget | `budget-visuals` | Pie chart breakdown |
| Wealth Manager | `wealth-assets` | Investment assets grouped table |
| Wealth Manager | `wealth-liabilities` | Active loans and EMI schedules |
| Wealth Manager | `wealth-liabilities-charts` | Payoff projection charts |
| Wealth Manager | `wealth-liabilities-ledger` | Repayment ledger modal |
| Wealth Manager | `wealth-networth` | Net worth timeline chart |
| Wealth Manager | `wealth-allocation` | Portfolio allocation and health |
| Bella AI Chat | `chat-empty` | Chat empty state |
| Bella AI Chat | `chat-conversation` | Chat with AI response (backend required) |
| Settings | `settings-accounts` | Bank accounts panel |
| Settings | `settings-categories` | Budget categories panel |

## Generated outputs

After each run the script also writes inside the versioned folder:

- `manifest.json` — machine-readable journey metadata consumed by the
  portfolio HTML page.
- `README.md` — auto-generated screen reference table (always accurate).
