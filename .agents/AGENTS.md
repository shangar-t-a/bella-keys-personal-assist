# Workspace Agent Rules

- **Development Standards:** Follow guidelines in [development-workflow.md](../docs/developer/development-workflow.md). Keep imports at the top, logic modularized, and comments clean and undecorated (`# comment`, `// comment`).
- **UI & Aesthetics:** Adhere to [ui-guidelines.md](../docs/developer/ui-guidelines.md) for a modern, desaturated Azure aesthetic with clean cards, typography, and elevation.
- **Git & Release Protocols:** Follow [git-guidelines.md](./rules/git-guidelines.md) for feature branches (`users/shangar/<desc>`), Conventional Commits with DCO sign-off, and `gh` CLI PR workflow. Follow [release-guidelines.md](./rules/release-guidelines.md) for version updates.
- **Documentation & Specs:** Follow [markdown-guidelines.md](./rules/markdown-guidelines.md) and [spec-guidelines.md](./rules/spec-guidelines.md). Store specs and tools in `.ai-assets/` and core protocols in `docs/` or `.agents/rules/`.
- **Testing & App Runner:** Always run automated tests (`pytest` / `npx tsc`) before committing. Use `bash scripts/run-dev.sh [profile]` or `docker compose` as the single entry point to launch the app locally, and prompt the user for visual sign-off before making git commits or PRs.
