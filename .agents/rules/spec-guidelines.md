---
name: spec-guidelines
description: Workspace rules and standards for authoring feature specifications and architecture documents
---

# Feature Specification Guidelines

This document defines quality standards for writing feature specifications and architecture proposal documents.

---

## 1. Readability & Structure

- **5–10 Minute Reading Target**: Specifications must be structured, concise, and readable within 5 to 10 minutes.
- **Shallow Heading Hierarchy**: Limit heading levels to `##` and `###`. Avoid deep, clumsy nested sub-sections.
- **Problem-First Rationale**: Every feature specification must open with the core problem statement, risks, and intent.

---

## 2. Technical Presentation Standards

- **Mermaid Diagrams**: Use standard Mermaid diagrams (`graph TD` or `sequenceDiagram`) for components and sequence
  flows.
- **No ASCII Pseudo-Tables**: Never use box-drawing characters or ASCII text borders for UI wireframes.
- **No Implementation Code**: Do not include component source code (JSX/TSX) or backend code in specs.
- **Data & API Interfaces**: Specify API endpoint paths, HTTP methods, and payload JSON schemas cleanly.
