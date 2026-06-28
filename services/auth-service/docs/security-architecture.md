# Auth Service Security Architecture

This document outlines the security architecture and design choices implemented for authentication and session management in Bella Keys. These patterns are directly informed by modern web security standards, including IETF RFCs and Best Current Practices (BCPs).

---

## 1. OAuth 2.0 & Token Authorization Strategy

### RFC 9700 (OAuth 2.0 Security Best Current Practice) Compliance
Bella Keys implements the **Authorization Code Flow with Proof Key for Code Exchange (PKCE - RFC 7636)** for user authentication.
* **Implicit Flow Deprecation**: Older client-side implicit flows return tokens directly in the browser's redirect URL, exposing them to history leaks and interception. Following **RFC 9700**, we deprecate implicit response types entirely.
* **Client Type**: Single-Page Applications (SPAs) and Desktop wrappers (Electron) are categorized as **Public Clients** because they cannot securely hold client secrets. All token-exchanges are verified dynamically using runtime code challenges.

---

## 2. Token Storage and Threat Mitigation

The choice of storage for OAuth tokens determines vulnerability to Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF).

### Access Token (Short-Lived: 60 Minutes)
* **Storage Location**: Client-Side Application Memory (In-Memory).
* **Implementation**: Managed inside `tokenStore.ts` and set dynamically upon successful login or silent refresh.
* **Security Rationale**: Since the token lives strictly in the active JavaScript runtime memory, it is never written to disk or browser storage APIs (like `localStorage` or `sessionStorage`). This mitigates the risk of an attacker extracting a persistent Bearer token in the event of an XSS vulnerability.
* **UX Trade-off**: Refreshing the browser tab or closing the app clears this token, triggering a silent refresh.

### Refresh Token (Long-Lived: 7 Days)
* **Storage Location**: `HttpOnly`, `Secure` (when HTTPS), and `SameSite=Lax` Cookie.
* **Security Rationale**: Storing refresh tokens in `localStorage` is an anti-pattern. If an XSS vulnerability exists, a malicious script can read `localStorage` and steal the token, gaining permanent account access. By marking the cookie as `HttpOnly`, browser engines prevent client-side scripts from reading or modifying the cookie, neutralizing XSS theft.
* **CSRF Mitigation**: SameSite cookies restrict automatic transmission of the cookie in cross-site requests. Furthermore, because `/refresh` only outputs the access token in the response body (which standard browser CSRF requests cannot read due to the Same-Origin Policy), the endpoint is safe from CSRF session hijackings.

---

## 3. Refresh Token Rotation (RTR)

Following the security guidelines in **RFC 9700**, we implement Refresh Token Rotation to detect and prevent unauthorized token replay:

1. **Rotation**: When a client presents a valid refresh token at the `/refresh` endpoint, the server issues a **new** access token AND a **new** refresh token, while invalidating the old refresh token in the database.
2. **Replay Detection**: If the backend receives a refresh request containing a refresh token that has already been rotated (invalidated), this indicates that either a malicious actor intercepted the token and replayed it, or a sync issue occurred. 
3. **Session Revocation**: Upon detecting token reuse, the authorization server automatically invalidates **all** active refresh tokens linked to that user, immediately forcing a full lock-out and requiring password re-authentication.

---

## 4. Failure Design Logic

Our silent refresh failure handling distinguishes between two distinct scenarios:

* **Authentication Failures (400 / 401 / 403)**:
  If the `/refresh` endpoint explicitly rejects the request (e.g. cookie expired, token revoked, database entry deleted), the client application assumes the session is fully invalid. The client immediately wipes all local session memory and redirects the user to the Lock Screen.
* **Connectivity Failures (Network Disconnect)**:
  If the silent refresh request fails because the network is offline or the server is temporarily unreachable (causing a fetch rejection), the UI **does not** log the user out. Wiping the session on simple internet drops creates a poor user experience. Instead, the UI logs the warning and retains current session states, allowing request retries once connectivity is restored.

---

## 5. Hashing & Transit Security

### Native Bcrypt Hashing (Python 3.13 Compatibility)
* **Design Choice**: Instead of using the legacy and unmaintained `passlib` wrapper library, we call the native Python `bcrypt` library directly inside `app/core/security.py`. This ensures full native support for Python 3.13, removes the dependency on `passlib` entirely, and avoids the runtime version traceback issues introduced by `passlib`'s legacy version metadata checks.
* **Algorithm**: Plain-text master passwords are hashed using `bcrypt`'s native cryptographic function with a secure, random salt (`bcrypt.gensalt()`, default work factor 12) before database insertion.

### Password Transmission (POST Request Body Security)
* **Transit Encryption**: The password is sent in the HTTP `POST` request body during login. Since all production traffic is protected under SSL/TLS (HTTPS), the entire HTTP request payload (including headers, parameters, and the body) is encrypted in transit. This prevents eavesdropping or interception by intermediaries.
* **Why POST is Used Over GET**: GET requests pass parameters in the URL query string (e.g. `?password=...`). Browser history, server access logs (like Nginx), and reverse proxy logs record query strings in plain text on disk, which is a major security vulnerability. POST bodies are excluded from standard logging systems, keeping credentials secure on the host.
