<!-- markdownlint-disable MD024 -->

# Changelog

All notable changes to the services and applications in this monorepo are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Monorepo Release Notes Standard

This repository is a monorepo containing multiple independently versioned services and applications. Releases are tracked chronologically with component-specific version headers.

### Version Header Format

Each release entry must use the following header format:
`## [<component-name>@<version>] - YYYY-MM-DD`
Example: `## [expense-manager-service@1.4.0] - 2026-06-26`

### Change Categories

Changes under each header must be grouped into the following categories:

- **Added**: For new features.
- **Changed**: For changes in existing functionality.
- **Deprecated**: For soon-to-be-removed features.
- **Removed**: For now-removed features.
- **Fixed**: For any bug fixes.
- **Security**: In case of vulnerabilities or security updates.

## [bella-deploy-manager@1.0.0] - 2026-08-21

### Added

- **Evolution of `bella-keys-manager`**: Supersedes and evolves the legacy Windows batch script (`bella-keys-manager.bat`) into a standalone, cross-platform Python CLI/TUI package (`tools/deploy-manager/`).
- Introduced global CLI binary `bella-deploy`, installable anywhere via `uv tool install` without requiring local script maintenance in deployment directories.
- Added interactive Terminal User Interface (TUI) powered by `rich` and `questionary` with arrow-key navigation, branded panels, and structured status tables with color-coded container health badges.
- Added scriptable non-interactive CLI subcommands: `start`, `stop`, `restart`, `status`, `logs`, and `update`.
- Integrated automated remote production configuration downloading (`docker-compose.prod.yaml`, `.env.example`, `init-db-prod.sql`) and non-destructive `.env` key reconciliation.
- Added safe remote tool version comparison with `uv tool upgrade` user notifications (eliminating self-mutating file replacement bugs).

---

## [bella-keys-manager@1.0.1] - 2026-08-21

### Fixed

- Resolved `. was unexpected at this time` CMD batch parser error during manager script self-update checks caused by nested parenthesis delimiters and trailing periods.
- Guarded self-update file overwrite logic to only apply when the remote version is strictly newer than the currently executing script version.
- Prompt user to close and restart the manager script upon applying an update to ensure a clean execution lifecycle.

### Deprecated

- Deprecated Windows-only batch script (`scripts/deploy/bella-keys-manager.bat`) in favor of `bella-deploy-manager@1.0.0` (`tools/deploy-manager/`). Existing users are encouraged to install `bella-deploy` globally via `uv tool install`.

---

## [bella-keys-manager@1.0.0] - 2026-08-21

### Added

- Added unified Windows production runner and deployment manager script (`scripts/deploy/bella-keys-manager.bat`).
- Added interactive profile selection supporting EMS-only, AI Chat, and AI Chat + Monitor setups.
- Added self-updating configuration sync, automated Docker pull/restart, live log streaming, and environment key reconciliation.

---

## [keys-personal-assist-ui@1.13.0] - 2026-08-20

### Added

- Added interactive Human-in-the-Loop review and approval cards, enabling users to inspect proposed actions, edit parameters in place, approve, or reject actions before execution.
- Added live Deep Agent Task Execution Tree, visualizing hierarchical sub-agent delegation, reasoning steps, and tool executions in real time.
- Added Virtual Filesystem Artifact Drawer, allowing users to view generated code, documents, reports, and data files with full download support.
- Upgraded the AI Chat workspace to support Next-Gen Deep Agent real-time event streaming and interactive multi-turn threads.

---

## [bella-chat-service@1.2.0] - 2026-08-20

### Added

- Introduced Bella v2 Deep Agent orchestration architecture featuring specialized sub-agents for financial analysis and personal knowledge base retrieval.
- Added full real-time streaming for conversational responses, sub-agent transitions, tool invocations, and interactive human review interrupts.
- Added virtual filesystem artifact management for generating, storing, and serving persistent multi-format session artifacts.
- Integrated automated on-behalf-of token delegation for secure, seamless tool execution against backend services.

### Fixed

- Resolved authentication context loss during long-running tool execution sessions.

---

## [auth-service@2.2.0] - 2026-08-20

### Added

- Added OAuth 2.0 Token Exchange capability to support secure on-behalf-of service delegation and multi-service identity chaining.
- Enhanced session refresh workflows with secure HTTP-only cookies for improved web client security.

---

## [ems-mcp-server@1.2.0] - 2026-08-20

### Added

- Enhanced MCP tool execution with robust request-scoped Bearer token extraction for seamless backend communication.
- Added dynamic multi-target audience validation across container networks, local endpoints, and transport streams.

---

## [keys-personal-assist-ui@1.12.0] - 2026-08-19

### Added

- Added interactive Cost Breakdown Popover dialog (`AssetCostBreakdownPopover.tsx`) featuring 4 KPI tiles, visual cost composition bar, and grouped category accordions for carrying expenses and out-of-pocket outflow.
- Added 1-click `📊 Cost Breakdown` pie-chart icon button in Assets Overview table.
- Added support for transaction types `ANCILLARY_FEE`, `CAPITALIZED_INTEREST`, `INTEREST_REDUCTION`, and `IMPROVEMENT`.

---

## [expense-manager-service@1.8.0] - 2026-08-19

### Added

- Extended `AssetTransactionType` enum with `ANCILLARY_FEE`, `CAPITALIZED_INTEREST`, `INTEREST_REDUCTION`, and `IMPROVEMENT`.
- Added derived cost basis response fields to `AssetWithCalc` and `AssetResponse`: `base_asset_value`, `additional_spent`, `total_loan_interest`, and `total_cash_outflow`.
- Updated asset valuation engine to separate physical market valuation from total out-of-pocket cost basis.

---

## [keys-personal-assist-ui@1.11.0] - 2026-08-02

### Added

- Integrated application version (`v1.11.0`) and copyright notice (`© 2025 - 2026 Shangar Arivazhagan`) across sidebar navigation footer, user profile menu, and SSO login page.
- Added dedicated **About & System** tab under System Settings displaying application metadata, author details, license type, and runtime environment.
- Added interactive **Changelog & Release Notes** viewer modal and app-matching dark theme styling to GitHub Pages showcase.

---

## [keys-personal-assist-ui@1.10.0] - 2026-08-02

### Added

- Added **Backup & Restore** manager tab under Settings with folder configuration, snapshot list, export, download, deletion, and atomic restore operations.
- Integrated native Electron directory selection dialog (`dialog:selectDirectory`) via preload IPC for desktop mode, with fallback modal for web mode.
- Added unified path container pill component for desktop target directory selection.

---

## [expense-manager-service@1.7.0] - 2026-08-02

### Added

- Added user-configurable local database backup directory support (`~/.bella-keys/backups` by default).
- Added API endpoints `GET /v1/backup/config`, `PATCH /v1/backup/config`, `POST /v1/backup/export`, `GET /v1/backup/list`, and `POST /v1/backup/restore/snapshot`.
- Added automatic pre-restore safety snapshot generation (`pre_restore_<timestamp>.json`) prior to database clearing.

### Fixed

- Handled transaction `IntegrityError` in `get_or_create_period` and `get_or_create_account` to prevent race conditions and 500 errors under parallel UI requests.

---

## [expense-manager-service@1.6.0] - 2026-07-11

### Changed

- Integrated scope-based access controls enforcing the `bella-ems:read` scope dynamically on all v1 router endpoints.

### Fixed

- Updated integration test client token generator to inject valid `"scope"` claims, resolving all integration test failures under scope enforcement.

---

## [bella-chat-service@1.1.0] - 2026-07-11

### Changed

- Integrated scope-based access controls enforcing the `bella-chat:write` scope dynamically on all message endpoints.

---

## [utilities@1.1.0] - 2026-07-11

### Added

- Added reusable FastAPI scope enforcement dependency guard `require_scope` under `utilities.scope_guard` to perform authorization checks against JWT scope claims.

---

## [keys-personal-assist-ui@1.9.0] - 2026-07-11

### Changed

- Updated authentication client configuration to request full resource scopes (`openid`, `profile`, `email`, `bella-ems:read`, `bella-ems:write`, `bella-chat:read`, `bella-chat:write`) during login authorization.

---

## [auth-service@2.1.0] - 2026-07-11

### Added

- Introduced centralized scope registry `scopes.py` and integrated scope filtering / validation at authorization time.

---

## [expense-manager-service@1.5.3] - 2026-07-11

### Changed

- Upgraded shared `utilities` package dependency to `1.0.1`.

---

## [bella-chat-service@1.0.2] - 2026-07-11

### Changed

- Upgraded shared `utilities` package dependency to `1.0.1`.

---

## [utilities@1.0.1] - 2026-07-11

### Fixed

- Added manual CORS headers dynamically to raw responses returned from `JWTAuthMiddleware` (e.g. 401 Unauthorized errors) to prevent browser and Electron preflight blockages during cross-origin API operations.
- Added `verify_aud: False` option in `JWTAuthMiddleware` decryption step to prevent generic token verification claims failures across distributed services.

---

## [keys-personal-assist-ui@1.8.0] - 2026-07-11

### Added

- Registered `bella-app://` custom protocol deep-link listener inside Electron's main process.
- Implemented global React hook handler for incoming deep links to auto-route back to `/callback` exchange sequence.
- Added external system browser redirection for login flows inside desktop container.

### Changed

- Migrated authentication mechanism from standard credential submission to centralized OAuth 2.1 Single Sign-On (SSO) login flow.
- Added PKCE (`S256`) authorization code request sequence dynamically generated via Web Crypto API.
- Implemented `/callback` router handler (`OAuthCallback.tsx`) to perform secure token exchange and establish UI sessions.

---

## [auth-service@2.0.0] - 2026-07-11

### Added

- Added support for database-backed OAuth 2.1 authorization code flow with dynamic state and PKCE challenge verification.
- Introduced OIDC discovery metadata endpoint (`/.well-known/openid-configuration` / `/.well-known/oauth-authorization-server`) and `/oauth/userinfo` endpoints.
- Built dark glassmorphism consent/login UI template for authorization requests.
- Integrated `bella-app://callback` custom protocol deep-linking whitelist support.
- Added OIDC standard claims (`iss`, `aud`, `jti`, `scope`) to access token payloads and session propagation structures.

### Deprecated

- Marked the legacy `POST /login` endpoint as deprecated (`deprecated=True`).

### Fixed

- Resolved warnings inside test suites related to unawaited async-mock coroutines on synchronous SQLAlchemy session operations.

---

## [ems-mcp-server@1.1.0] - 2026-07-11

### Added

- Expanded Model Context Protocol (MCP) server with comprehensive financial query tools for accounts, reporting periods, spending entries, assets, liabilities, savings buckets, net wealth allocations, and monthly planner entries.
- Implemented extensive unit tests covering the new tools with 100% test coverage using respx mocks.

---

## [keys-personal-assist-ui@1.7.2] - 2026-06-28

### Fixed

- Resolved access violation crashes in packaged Electron production executable caused by absolute redirect paths starting with `/` or `/login` resolving to local directories (`file:///C:/`) rather than the application's relative index bundle path.

---

## [keys-personal-assist-ui@1.7.1] - 2026-06-28

### Fixed

- Implemented single-instance application lock check during startup to prevent concurrent app instances from locking disk cache directories and throwing access denied errors.
- Corrected Recharts chart rendering in Savings Envelopes page to initialize safely with fallback dimensions.
- Added explicit tab values to Material UI navigation tabs to suppress invalid value console warnings.

### Security

- Defined a robust Content Security Policy (CSP) to restrict remote origin access while permitting local API ports and hot-reload WebSockets in development.

---

## [keys-personal-assist-ui@1.7.0] - 2026-06-28

### Security

- Migrated refresh token storage from browser `localStorage` to secure, server-controlled `HttpOnly` cookies to protect Single-Page Application (SPA) sessions against Cross-Site Scripting (XSS) attacks.

### Changed

- Configured Axios client and Fetch authorization wrappers to transmit credentials/cookies and retrieve silent token refresh securely.
- Cleaned up token management flow inside `AuthContext` to skip storing refresh token in `localStorage`.

---

## [auth-service@1.1.0] - 2026-06-28

### Added

- Created `/logout` POST endpoint to delete and clear the client's `refresh_token` cookie.

### Security

- Updated `/login` and `/refresh` endpoints to set and rotate `refresh_token` in secure, HttpOnly cookies.

### Changed

- Configured CORS middleware dynamically to allow credential sharing for all local hosts (e.g. electron-vite dev environment) using a regex origin check.
- Updated FastAPI instance metadata to bind dynamically to the auth service package version.

---

## [expense-manager-service@1.5.1] - 2026-06-27

### Fixed

- Net worth double-counting when REVALUE transaction is backdated to the asset creation day.

### Changed

- Audited and cleaned up comments across service migrations and tests to follow simplified, undecorated commenting standards.

---

## [keys-personal-assist-ui@1.6.0] - 2026-06-27

### Changed

- Overhauled visual styling to a premium, desaturated Azure-like aesthetic with individual elevated card layouts, float transitions, and unified chart color palettes.
- Standardized user/assistant messaging bubbles with glassmorphism effects and modern gradient accents.
- Simplified comment blocks across all frontend TS/TSX/CSS files to use undecorated, clean commenting formats.
- Documented commenting guidelines and UI guidelines in `.agents/AGENTS.md` and `docs/developer/development-workflow.md`.

---

## [expense-manager-service@1.5.0] - 2026-06-27

### Added

- Portfolio Net Worth API endpoints with support for current summary calculation and historical timeline tracking.
- Portfolio Allocation API endpoints tracking asset/liability distribution, financing leverage, and health metrics (Debt-to-Asset and Liquidity ratios).

---

## [keys-personal-assist-ui@1.5.0] - 2026-06-27

### Added

- Interactive Net Worth dashboard tab featuring historical composed charts and ledger history.
- Portfolio Allocation dashboard tab displaying category distributions, financing leverage, and health metric gauges.
- Interactive explanatory tooltips for financial terms and metrics across all Wealth Manager dashboard tabs.

---

## [expense-manager-service@1.4.0] - 2026-06-26

### Added

- Support for interest-bearing liabilities without a scheduled EMI (non-EMI liabilities).
- Amortization calculation engine supporting daily, monthly, quarterly, semi-annual, and annual compounding frequencies.
- Support for absolute, interest-only, and interest-free moratorium periods in liability simulations.
- Amortization simulation endpoints to project outstanding balance and accumulated interest over time.

### Changed

- Refactored repository layer and database models for assets and liabilities to improve type safety and robustness.
- Decoupled database seeding logic from standard Alembic database migrations.

---

## [keys-personal-assist-ui@1.4.0] - 2026-06-26

### Added

- Comprehensive wealth manager liabilities tracking dashboard and input wizard.
- Amortization schedule charts, monthly payables tables, and summary metrics including total outstanding debt, active accounts, simple/compound distribution, and interest-free debt.
- Moratorium configurator and non-EMI mode toggle inside the liability addition flow.
- Theme-driven category chip styling and interactive delete confirmation dialogs.

### Fixed

- Silent JWT token refresh mechanism on initial application reload and request failure.

---

## [keys-personal-assist-ui@1.2.0] - 2026-06-21

### Added

- Initial user interface layouts for tracking liabilities within the Wealth Manager module.

---

## [expense-manager-service@1.2.0] - 2026-06-21

### Added

- Database models, schemas, and API routers for tracking personal liabilities.
- Core amortization simulation logic for standard EMI loans.

---

## [bella-chat-service@1.0.1] - 2026-06-21

### Fixed

- Qdrant connection refused error by ensuring proper hostname routing when running inside Docker container environments.
- Python package dependency constraints and environment configurations.

---

## [ems-mcp-server@1.0.1] - 2026-06-21

### Changed

- Secured the EMS MCP server by propagating and validating the client authentication token.

---

## [expense-manager-service@1.1.0] - 2026-06-07

### Added

- Database schemas and API routes for tracking wealth manager assets.
- Support for asset categories (Real Estate, Equity, Mutual Funds, Cash, Precious Metals).

### Changed

- Decoupled initial database seeding logic from database migrations.

---

## [keys-personal-assist-ui@1.1.0] - 2026-06-07

### Added

- Assets tracking wizard and customized dialog flows.
- Inline quick-add UI for dashboard transactions and account management.

### Changed

- Standardized Finance module sub-pages under a cohesive sidebar navigation.
- Consolidated settings interface and dark mode switcher inside user profile dropdown.

---

## [auth-service@1.0.0] - 2026-06-01

### Added

- Independent authentication service built on FastAPI.
- JWT token signing, verification endpoints, and silent refresh mechanisms.
- Docker build configurations and automated workflows.

### Changed

- Reset all monorepo service versions to 1.0.0 baselines to establish a clean production release tracking timeline.

---

## [expense-manager-service@3.0.0] - 2026-05-24

### Added

- Savings buckets feature allowing users to segregate savings across custom targets.
- Transaction cancellation rules and logic.
- Database tables for savings buckets and savings transactions.

---

## [keys-personal-assist-ui@3.0.0] - 2026-05-24

### Added

- Savings Fund Segregator dashboard layout.
- Integrations with backend savings buckets APIs.
- Automated Electron application packaging configurations and platform-specific installers (Windows, Linux, macOS).

---

## [ems-mcp-server@1.0.0] - 2026-04-04

### Added

- Read-only Model Context Protocol (MCP) server for retrieving information from the Expense Manager Service.

---

## [bella-chat-service@1.0.0] - 2025-10-21

### Added

- LangGraph workflow engine for orchestration.
- Arize Phoenix integration for LLM tracing.
- ETL pipeline for GitHub keys personal wiki integration utilizing Personal Access Tokens (PAT) and Qdrant.
- Chat interface UI and real-time streaming tools.

---

## [expense-manager-service@1.0.0] - 2025-08-16

### Added

- Initial version of the FastAPI expense manager backend service.
- PostgreSQL database integration and Alembic migrations system.
- Docker Compose local development environment setups.

---

## [keys-personal-assist-ui@1.0.0] - 2025-08-16

### Added

- React, TypeScript, and Vite-powered user interface replacing legacy frontend.
- App shell, navigation routing, and responsive dashboard.

---

## [keys-personal-assist-ui@0.0.3] - 2024-07-30

### Changed

- Removed redundant close button from header of Add Entry and Edit Entry modals.

---

## [keys-personal-assist-ui@0.0.2] - 2024-07-30

### Changed

- Adjusted dark mode CSS selectors to trigger based on `body.dark-mode` class toggles rather than system preferences.

---

## [keys-personal-assist-ui@0.0.1] - 2024-07-30

### Added

- Initial Bolt-generated React frontend codebase for tracking expenses.

---

## [expense-manager-service@0.0.1] - 2024-07-30

### Added

- Initial implementation of the Python FastAPI expense tracking API.
