# Git Workflow Standards

This is the project's single source of truth for Git operations. All AI agents and developers must follow these standards.

## 1. Starting a Feature

* **Branch Naming:** `users/shangar/<description>`
* **Workflow:**
    1. Checkout main: `git checkout main`
    2. Pull latest: `git pull origin main`
    3. Create branch: `git checkout -b users/shangar/<description>`

## 2. Committing Changes

Use the **Conventional Commit** format with a mandatory **Sign-off**.

1. Stage files: `git add <files>`
2. Get user info: `git config user.name` and `git config user.email`
3. Commit with sign-off:

    ```text
    feat(scope): descriptive title
    - Detailed bullet point 1
    - Detailed bullet point 2
    Signed-off-by: Name <email@example.com>
    ```

4. **Confirm with user** and push to remote.

## 3. Creating/Updating a PR

Always use the GitHub CLI (`gh`).

1. **Check existing:** `gh pr list` to see if a PR already exists for the branch.
2. **Analyze changes:** `git log main..HEAD` to understand the work.
3. **Action:**
    * **New PR:** `gh pr create --title "<Descriptive Title>" --body "<Comprehensive Summary>"`
    * **Edit PR:** `gh pr edit --title "<New Title>" --body "<Updated Summary>"`
4. **Formatting:** The PR title should be clean (no conventional commit prefix), but the body should be comprehensive.
