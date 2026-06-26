# Authentication Guide

Bella Keys uses a local authentication system designed to keep your data secure on your own device. When you step away, your personal assistant remains locked and protected.

## Logging In

1. Open Bella Keys.
2. At the **Lock Screen**, enter your Master Username and Password.
3. Click **Unlock**.

*Note: Your credentials are only stored locally on your machine. They are never sent to a cloud server.*

## Session Security & Timeouts

To ensure your data remains secure:

- **Automatic Lock:** Your active session securely expires after **1 hour** of inactivity.
- **Silent Refresh:** If you are actively using the application, Bella Keys will silently refresh your session in the background so you are not repeatedly asked for your password.
- **Full Expiration:** If the app is closed or inactive for **7 days**, your background session token fully expires. On your next visit, you will need to log in again.

## Locking the App Manually

If you need to leave your computer and want to secure Bella Keys immediately:

1. Locate the sidebar menu.
2. Click **Lock App**.
3. You will immediately be returned to the Lock Screen, requiring a password for the next access.

## Authentication Flow Diagram

The sequence diagram below illustrates the authentication lifecycle, including initial login, accessing resources, and token rotation (silent refresh):

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Browser)
    participant UI as React UI (Nginx)
    participant Auth as Auth Service
    participant DB as PostgreSQL DB
    participant API as Protected Services (EMS/Bella)

    Note over User, DB: 1. User Login Flow
    User->>UI: Enter Username/Password
    UI->>Auth: POST /auth/login (form-data)
    Auth->>DB: Query User & verify password hash
    DB-->>Auth: User verified
    Auth->>Auth: Generate JWT Access & Refresh Tokens
    Auth->>DB: Store Refresh Token (user_id, token, expires_at)
    DB-->>Auth: Token stored
    Auth-->>UI: Return Access Token & Refresh Token (Bearer)
    UI-->>User: Unlock App & show Dashboard

    Note over User, DB: 2. Accessing Protected Resources
    UI->>API: API Request (Authorization: Bearer <access_token>)
    API->>API: Decode and verify JWT signature
    API-->>UI: Protected Data Response
    UI-->>User: Update Dashboard UI

    Note over User, DB: 3. Token Rotation (Silent Refresh)
    UI->>API: API Request (Expired Access Token)
    API-->>UI: 401 Unauthorized Response
    UI->>Auth: POST /auth/refresh { refresh_token }
    Auth->>DB: Lookup refresh token & verify expiration
    DB-->>Auth: Token valid, return record
    Auth->>Auth: Generate new Access & Refresh Tokens
    Auth->>DB: Rotate token (update old record with new token)
    DB-->>Auth: Record updated
    Auth-->>UI: Return new Access & Refresh Tokens
    UI->>API: Retry original API Request (Authorization: Bearer <new_access_token>)
    API-->>UI: Protected Data Response
    UI-->>User: Update UI
```
