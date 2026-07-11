"""Reusable FastAPI scope enforcement dependency for resource services.

Resource services (EMS, Chat) import `require_scope` and apply it as a FastAPI
dependency to enforce that the JWT access token carries the required scopes
before granting access to an endpoint.

Scope enforcement works in two layers:
  1. JWTAuthMiddleware validates the token signature and expiry (transport layer).
  2. require_scope checks that the granted scope set includes the required scopes (permission layer).

Both layers must pass for a request to reach the route handler.
"""

from fastapi import Depends, HTTPException, Request, status


def require_scope(*required_scopes: str):
    """Return a FastAPI dependency that enforces the presence of all required scopes.

    Usage:
        @router.get("/resource", dependencies=[require_scope("bella-ems:read")])
        async def list_resources():
            ...

    Args:
        *required_scopes: One or more scope strings that the token must contain.

    Returns:
        A FastAPI Depends() object that raises HTTP 403 if any required scope is absent.
    """
    def _check(request: Request) -> None:
        user = getattr(request.state, "user", {})
        # The scope claim is a space-separated string stored in the JWT payload.
        token_scopes = set((user.get("scope") or "").split())
        missing = set(required_scopes) - token_scopes
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "insufficient_scope",
                    "error_description": (
                        f"Token is missing required scopes: {', '.join(sorted(missing))}"
                    ),
                },
            )
    return Depends(_check)
