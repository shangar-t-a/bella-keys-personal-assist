"""OAuth 2.1 Service layer for managing database-backed authorization codes."""

import base64
from datetime import UTC, datetime, timedelta
import hashlib
import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import get_settings
from app.core.constants import CODE_CHALLENGE_METHOD_S256
from app.db.models import OAuthAuthorizationCode

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
    """Generate and persist a new authorization code valid for 5 minutes."""
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
    """Validate the auth code, consume (delete) it from the DB to prevent replay, and return its details."""
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

    await db.delete(db_code)
    await db.commit()

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

    if db_code.code_challenge_method != CODE_CHALLENGE_METHOD_S256:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_grant",
                "error_description": "Unsupported code challenge method",
            },
        )

    verifier_bytes = code_verifier.encode(ASCII_ENCODING)
    challenge_bytes = hashlib.sha256(verifier_bytes).digest()

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
    await db.execute(delete(OAuthAuthorizationCode).where(OAuthAuthorizationCode.expires_at < now.replace(tzinfo=None)))
    await db.commit()
