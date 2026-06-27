---
name: release-guidelines
description: Operational guidelines for releasing monorepo components and version syncing
---

# Monorepo Release Guidelines

All AI agents and developers must follow these rules when performing releases:

## 1. Release Types (Semantic Versioning)

- **Major Update (X.0.0):** Triggered by breaking architectural changes, backwards-incompatible API updates, or core system rewrites (e.g., `1.5.0` -> `2.0.0`).
- **Minor Update (0.Y.0):** Triggered by new backward-compatible features, layout overhauls, design system updates, or significant UI design changes (e.g., `1.5.0` -> `1.6.0`).
- **Patch (Fix) Update (0.0.Z):** Triggered by backward-compatible bug fixes, optimizations, comment formatting audits, tests, or documentation updates (e.g., `1.5.0` -> `1.5.1`).

## 2. Version Checklist

When bumping the version of any component, locate and update all relevant version definitions within that component's directory:

- **Python Services:** Update the version in the `VERSION` file, `__init__.py` file, and any schema/OpenAPI JSON documentation.
- **Node.js/UI Applications:** Update the version in `package.json`.

## 3. Unified Changelog

Always log releases chronologically in [CHANGELOG.md](file:///c:/Users/shang/sandbox/repos/bella-keys-personal-assist/CHANGELOG.md) using the header format:
`## [<component-name>@<version>] - YYYY-MM-DD`
Group items under standard Keep a Changelog categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`. Do not use emojis.
