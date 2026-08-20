# Identity and Authorization Architecture Suite

This documentation suite contains technical specifications for the authentication, authorization, and token
delegation infrastructure in Bella Keys.

---

## Technical Specifications Sitemap

1. **[OAuth 2.1 and OpenID Connect (OIDC) Core Specification](./oauth2.1-oidc-spec.md)**
   Authorization Server (`auth-service`) architecture, PKCE `S256` SHA-256 validation (RFC 7636), OIDC metadata
   discovery (`/.well-known/openid-configuration`), UserInfo endpoint, and SPA in-memory token storage strategy.

2. **[Service-to-Service Delegation: RFC 8693 Token Exchange (OBO)](./mcp-token-exchange.md)**
   On-Behalf-Of (OBO) token exchange grant (`grant_type=urn:ietf:params:oauth:grant-type:token-exchange`), Resource
   Indicator (RFC 8707) audience restriction (`aud`), delegation actor claims (`act: {"sub": "client_id"}`), and FastMCP
   native integration.

3. **[Scopes, Roles and Scope Guard Enforcement](./scopes-and-rbac.md)**
   Scope registry (`VALID_SCOPES`, `CLIENT_ALLOWED_SCOPES`), role definitions (`user`, `admin`), and FastAPI
   `scope_guard` enforcement dependency (`require_scope`).

---

## Architectural Principles

### Zero Ambient Authority

Service-to-service calls MUST NOT forward raw user access tokens across security domain boundaries without exchanging
them for target-bounded tokens.

### Stateless Resource Validation

Resource Servers (FastMCP, EMS, Chat) validate JWTs locally using signature verification (`HS256`, `JWT_SECRET`) and
audience validation without making remote HTTP calls to `auth-service` during request processing.

### Strict PKCE Enforcement

Authorization code flows mandate SHA-256 code challenge method (`code_challenge_method=S256`).
