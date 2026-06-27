---
name: git-guidelines
description: Git guidelines for branch setup, commits, and PR creation
---

# Git Guidelines

This document defines the Git branching, commit, and pull request standards that must be followed by developers and AI agents in this workspace.

---

## 1. Feature Branch Setup

All new work must be performed in a dedicated feature branch.

- **Branch Naming Convention:** `users/shangar/<description>`

**Branch Creation Flow:**

```bash
git checkout main
git pull origin main
git checkout -b users/shangar/<description>
```

---

## 2. Commit Standards

Commits must follow the Conventional Commits specification and include a mandatory Developer Certificate of Origin (DCO) Sign-off.

### Commit Process

**Step 1: Stage modified files**

```bash
git add <files>
```

**Step 2: Retrieve the git user configuration**

```bash
git config user.name
git config user.email
```

**Step 3: Create the commit using the template**

Replace the placeholder details with the retrieved user configuration:

```text
feat(scope): descriptive title

- Detailed explanation of changes
- Impact of changes

Signed-off-by: Name <email@example.com>
```

**Step 4: Confirm changes**

Confirm the staged changes and commit metadata with the user before pushing the branch to the remote repository.

---

## 3. Pull Request Management

All Pull Requests (PRs) must be created and managed using the GitHub CLI (`gh`).

### Pull Request Process

**Step 1: Check for an existing pull request for the active branch**

```bash
gh pr list
```

**Step 2: Review the commit log to construct a summary of proposed changes**

```bash
git log main..HEAD
```

**Step 3: Create or update the pull request**

- **New Pull Request:**

  ```bash
  gh pr create --title "Descriptive Title" --body "Comprehensive Summary"
  ```

- **Update Existing Pull Request:**

  ```bash
  gh pr edit --title "Updated Descriptive Title" --body "Updated Comprehensive Summary"
  ```

### Pull Request Title and Body Formatting

- **Title:** Use a clean, professional description. Do not include Conventional Commit prefixes (such as `feat:` or `fix:`) in the pull request title.
- **Body:** Provide a detailed description of all changes introduced by the pull request.
