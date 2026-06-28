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
