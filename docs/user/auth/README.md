# Security and Authentication Guide

Bella Keys is built on a local-first, zero-trust security architecture. Personal financial data, chat records,
and credentials remain stored strictly on the local device and are not transmitted to external cloud servers.

---

## Documentation Index

1. **[Single Sign-On (SSO) and Session Management](./sso-login.md)**
   Step-by-step SSO login for the Web UI and Electron Desktop App, including session lifecycle rules, silent token
   refresh, and manual logout.

2. **[Permissions, Scopes and AI Delegation](./permissions-and-delegation.md)**
   Detailed descriptions of requested permissions and an explanation of how the AI Assistant accesses tools on your
   behalf using On-Behalf-Of (OBO) delegation.

---

## Core Security Principles

### Local Data Guarantee

All personal financial data managed by Expense Manager Service (EMS) and personal chat context managed by Bella Chat
Service remain inside local databases on your device.

### OAuth 2.1 and OIDC Standards

Authentication uses industry-standard OAuth 2.1 with PKCE (`S256`) SHA-256 protection against credential
interception attacks.

### Audience and Scope Restriction

Tokens issued for one service cannot be reused by another service without explicit, target-bounded authorization.
