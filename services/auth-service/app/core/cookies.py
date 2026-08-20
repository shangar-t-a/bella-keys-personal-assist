"""Cookie management utilities for Auth Service."""

from fastapi import Response

from app.core.constants import (
    COOKIE_PATH_ROOT,
    COOKIE_REFRESH_TOKEN,
    COOKIE_SAMESITE_LAX,
)


def set_refresh_token_cookie(response: Response, refresh_token: str, is_secure: bool) -> None:
    """Set HttpOnly refresh token cookie on HTTP response."""
    response.set_cookie(
        key=COOKIE_REFRESH_TOKEN,
        value=refresh_token,
        httponly=True,
        secure=is_secure,
        samesite=COOKIE_SAMESITE_LAX,
        path=COOKIE_PATH_ROOT,
    )


def delete_refresh_token_cookie(response: Response) -> None:
    """Delete refresh token cookie from client browser."""
    response.delete_cookie(
        key=COOKIE_REFRESH_TOKEN,
        path=COOKIE_PATH_ROOT,
    )
