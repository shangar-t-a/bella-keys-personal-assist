# Authentication Guide

Bella Keys uses a centralized Single Sign-On (SSO) authentication system designed to keep your data secure on your own device. When you step away, your personal assistant remains locked and protected.

## Logging In

1. Open Bella Keys.
2. At the **Lock Screen**, click **Sign In with SSO**.
3. You will be redirected to the central **Bella Keys login & authorization page**.
4. Enter your Master Username and Password, and click **Authorize**.
5. Once authorized, you will be securely redirected back to the application dashboard.

*Note: Your credentials are only stored locally on your machine. They are never sent to a cloud server.*

## Session Security & Timeouts

To ensure your data remains secure:

- **Automatic Lock:** Your active session securely expires after **1 hour** of inactivity.
- **Silent Refresh:** If you are actively using the application, Bella Keys will silently refresh your session in the background using HttpOnly cookies so you are not repeatedly asked for your password.
- **Full Expiration:** If the app is closed or inactive for **7 days**, your background session token fully expires. On your next visit, you will need to log in again.

## Locking the App Manually

If you need to leave your computer and want to secure Bella Keys immediately:

1. Locate the sidebar menu.
2. Click **Lock App**.
3. You will immediately be returned to the Lock Screen, requiring a password for the next access.

## Authentication Flow Diagram

The sequence diagram below illustrates the authentication lifecycle, including central SSO redirection, PKCE code-to-token exchange, and silent refresh:

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Browser)
    participant UI as React UI (Nginx)
    participant Auth as Auth Service (IdP)
    participant DB as PostgreSQL DB
    participant API as Protected Services (EMS/Bella)

    Note over User, DB: 1. SSO Login Flow (OAuth 2.1 + PKCE)
    User->>UI: Click "Sign In with SSO"
    UI->>UI: Generate PKCE code_verifier & challenge
    UI->>User: Redirect browser to Auth Service /oauth/authorize
    User->>Auth: Enter Username & Password, click "Authorize"
    Auth->>DB: Query User & verify password hash
    DB-->>Auth: User verified
    Auth->>DB: Store temporary auth code & PKCE challenge
    Auth->>DB: Store initial Refresh Token
    Auth-->>User: 303 Redirect to UI /callback?code=xxx
    User->>UI: Load /callback?code=xxx
    UI->>Auth: POST /oauth/token (with code & code_verifier)
    Auth->>Auth: Verify PKCE verifier against code_challenge
    Auth->>DB: Consume & delete temporary code
    Auth-->>UI: Return Access Token & set HttpOnly Refresh Cookie
    UI-->>User: Unlock App & show Dashboard

    Note over User, DB: 2. Accessing Protected Resources
    UI->>API: API Request (Authorization: Bearer <access_token>)
    API->>API: Decode and verify JWT signature locally (HS256)
    API-->>UI: Protected Data Response
    UI-->>User: Update Dashboard UI

    Note over User, DB: 3. Token Rotation (Silent Refresh)
    UI->>API: API Request (Expired Access Token)
    API-->>UI: 401 Unauthorized Response
    UI->>Auth: POST /refresh (Cookie: refresh_token)
    Auth->>DB: Lookup refresh token & verify expiration
    DB-->>Auth: Token valid, return record
    Auth->>Auth: Generate new Access & Refresh Tokens
    Auth->>DB: Rotate token (update record)
    Auth-->>UI: Return new Access Token & update HttpOnly Refresh Cookie
    UI->>API: Retry original API Request (Authorization: Bearer <new_access_token>)
    API-->>UI: Protected Data Response
    UI-->>User: Update UI
```

