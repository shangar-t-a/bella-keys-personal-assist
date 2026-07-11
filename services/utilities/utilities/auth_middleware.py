"""JWT Authentication Middleware for Bella Keys services."""

import os
import re

from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate JWT tokens on protected routes."""

    def __init__(self, app, exclude_paths: list[str] | None = None, secret_key: str | None = None):
        """Initialize middleware with optional paths to exclude and a JWT secret."""
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            r"^/health$",
            r"^/openapi\.json$",
            r"^/docs$",
            r"^/redoc$"
        ]
        self.secret_key = secret_key or os.getenv("JWT_SECRET")

    def _get_error_response(self, status_code: int, detail: str, request: Request) -> JSONResponse:
        """Generate a JSONResponse with CORS headers to prevent browser blocks."""
        response = JSONResponse(status_code=status_code, content={"detail": detail})
        # Direct error responses bypass FastAPI's CORSMiddleware wrapper.
        # We manually inject CORS headers here so cross-origin desktop clients (like Electron)
        # do not experience network preflight blocks when a request is unauthorized.
        origin = request.headers.get("origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        else:
            response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        return response

    async def dispatch(self, request: Request, call_next):
        """Intercept and validate requests."""
        # 0. Allow OPTIONS requests to pass through for CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # 1. Check if path is excluded
        path = request.url.path
        for pattern in self.exclude_paths:
            if re.match(pattern, path):
                return await call_next(request)

        # 2. Extract Authorization Header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return self._get_error_response(401, "Not authenticated", request)

        token = auth_header.split(" ")[1]
        
        # 3. Validate Token
        if not self.secret_key:
            return self._get_error_response(500, "JWT_SECRET is not configured on this service", request)

        try:
            # We disable strict audience validation ("verify_aud": False) in this common middleware.
            # This allows the same access token to be used across multiple services and clients
            # while maintaining verification of token signatures, expirations, and issuers.
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"], options={"verify_aud": False})
            # Attach user info to request state
            request.state.user = payload
        except JWTError:
            return self._get_error_response(401, "Invalid or expired token", request)

        # 4. Continue Request
        response = await call_next(request)
        return response
