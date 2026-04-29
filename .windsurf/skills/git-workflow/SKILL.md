---
name: git-workflow
description: Git workflow guidelines for branch setup, commits, and PR creation
---

## Starting a Feature

Branch naming format: `users/shangar/<description>`

Use gh cli to setup:

1. Checkout main: `git checkout main`
2. Pull latest: `git pull origin main`
3. Create branch: `git checkout -b users/shangar/<description>`

## Committing Changes

Use conventional commit format with signoff from git config user info:

1. Find and add relevant files: `git add <files>`
2. Get user info: `git config user.name` and `git config user.email`
3. Commit with signoff got from user info.
4. Get confirmation from user before pushing to remote.

Example:

```
feat(auth): add user login endpoint
- Implement JWT token generation
- Add password validation
- Signed-off-by: Shangar <shangar@example.com>
```

## Creating a PR

When ready, create PR by:

1. Check if a PR exists, if so, update it instead of creating a new one.
2. Get commits from feature branch after main: `git log main..HEAD`
3. Analyze commits and create descriptive title
4. Create PR: `gh pr create --title "<title>" --body "<summary>"`
   1. Use descriptive title and comprehensive PR summary based on the changes made. Title should not have conventional commit format.

The AI should analyze the commits and create a custom descriptive title and comprehensive PR summary based on the changes made.

## Updating a PR

When updating a PR, follow the same workflow as creating a PR, but use `gh pr edit` to update the PR.

1. Understand the changes made to the PR.
2. Get existing PR description: `gh pr view <pr-number> --json body --jq '.body'`
3. Update the PR description and title using `gh pr edit`.
