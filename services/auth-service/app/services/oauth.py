"""OAuth 2.1 Service layer for managing database-backed authorization codes."""

import base64
from datetime import datetime, timedelta, UTC
import hashlib
import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import get_settings
from app.db.models import OAuthAuthorizationCode

PKCE_CHALLENGE_METHOD_S256 = "S256"
ASCII_ENCODING = "ascii"


async def create_authorization_code(  # noqa: PLR0913
    db: AsyncSession,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    code_challenge_method: str,
    username: str,
    role: str,
    resource: str | None = None,
    scope: str | None = None,
) -> str:
    """Generate and persist a new authorization code valid for 5 minutes.

    This function represents Step 1 of the PKCE (Proof Key for Code Exchange, RFC 7636) flow:
    1. The client (e.g., React SPA) generates a cryptographically random 'code_verifier'.
    2. The client hashes the verifier using SHA-256 and base64url-encodes it to produce a 'code_challenge'.
    3. The client initiates login by sending the 'code_challenge' and 'code_challenge_method' (S256)
       to this authorization service.
    4. Upon successful user authentication, we store this challenge in the database associated with the
       issued temporary authorization code.
    """
    code = f"auth_code_{uuid.uuid4().hex}"
    db_code = OAuthAuthorizationCode(
        code=code,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        username=username,
        role=role,
        resource=resource,
        scope=scope,
        expires_at=(datetime.now(UTC) + timedelta(minutes=get_settings().OAUTH_CODE_EXPIRE_MINUTES)).replace(
            tzinfo=None
        ),
    )
    db.add(db_code)
    await db.commit()
    return code


async def validate_and_consume_code(
    db: AsyncSession,
    code: str,
    client_id: str,
    redirect_uri: str,
    code_verifier: str,
) -> OAuthAuthorizationCode:
    """Validate the auth code, consume (delete) it from the DB to prevent replay, and return its details.

    This function implements Step 2 of the PKCE (Proof Key for Code Exchange, RFC 7636) flow:
    1. The client sends the authorization code along with the plaintext 'code_verifier' to /oauth/token.
    2. We retrieve the authorization record, immediately deleting it to prevent reuse (replay protection).
    3. We hash the client's plaintext 'code_verifier' using SHA-256, base64url-encode it, and compare it
       against the stored 'code_challenge'.
    4. If they match, it proves that the client requesting the token is the same client that initiated the
       authorization request, mitigating authorization code interception attacks.
    """
    result = await db.execute(select(OAuthAuthorizationCode).where(OAuthAuthorizationCode.code == code))
    db_code = result.scalars().first()

    if not db_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_grant",
                "error_description": "Invalid or expired authorization code",
            },
        )

    # Replay protection: immediately delete the code once read
    await db.delete(db_code)
    await db.commit()

    # Normalize timezone for comparison
    expires_at = db_code.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)

    if expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_grant",
                "error_description": "Authorization code expired",
            },
        )

    if db_code.client_id != client_id or db_code.redirect_uri != redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_grant",
                "error_description": "Client ID or Redirect URI mismatch",
            },
        )

    # Perform PKCE S256 validation
    if db_code.code_challenge_method != PKCE_CHALLENGE_METHOD_S256:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_grant",
                "error_description": "Unsupported code challenge method",
            },
        )

    # Convert code_verifier to bytes and hash using SHA-256
    verifier_bytes = code_verifier.encode(ASCII_ENCODING)
    challenge_bytes = hashlib.sha256(verifier_bytes).digest()

    # Base64url-encode the resulting hash and strip padding '=' characters
    computed_challenge = base64.urlsafe_b64encode(challenge_bytes).decode(ASCII_ENCODING).replace("=", "")
    expected_challenge = db_code.code_challenge.replace("=", "")

    if computed_challenge != expected_challenge:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_grant",
                "error_description": "PKCE S256 verification failed",
            },
        )

    return db_code


async def prune_expired_codes(db: AsyncSession) -> None:
    """Evict expired authorization codes to prevent database bloat."""
    now = datetime.now(UTC)
    # Remove tzinfo for database query comparison if stored naive
    await db.execute(delete(OAuthAuthorizationCode).where(OAuthAuthorizationCode.expires_at < now.replace(tzinfo=None)))
    await db.commit()
