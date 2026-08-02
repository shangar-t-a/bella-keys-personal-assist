---
name: markdown-guidelines
description: Workspace rules and standards for Markdown syntax, line wrapping, heading spacing, and code fences
---

# Markdown Formatting Guidelines

This document defines mandatory Markdown formatting and syntax standards across all repositories in this workspace.

---

## 1. Line Length Limit

- Every line in a Markdown file must strictly remain under **120 characters**.
- Prefer short, concise sentences and bulleted lists over long paragraph lines.
- Long sentences must be wrapped across multiple lines.

---

## 2. Heading Spacing

- Always place a blank line directly **before** every heading (`#`, `##`, `###`).
- Always place a blank line directly **after** every heading (`#`, `##`, `###`).

---

## 3. Code Fences & Language Declarations

- Every fenced code block must explicitly specify a language identifier (e.g. `mermaid`, `json`, `bash`, `text`).
- Never use empty code fence delimiters without a language tag.

---

## 4. Table Formatting & Exceptions

- Tables are exempt from the 120-character line length limit.
- If a table becomes excessively wide or hard to read, refactor it into bullet lists or standard JSON payloads.

---

## 5. No Emphasis as Heading (MD036)

- Never use single lines of bold or italic emphasis (e.g., `**Heading Text:**`) as pseudo-headings.
- Always use standard Markdown heading tags (`###`, `####`) for section titles, or bullet items (`- **Label:** ...`) for inline field lists.

