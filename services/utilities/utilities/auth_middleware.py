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
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        token = auth_header.split(" ")[1]
        
        # 3. Validate Token
        if not self.secret_key:
            return JSONResponse(status_code=500, content={"detail": "JWT_SECRET is not configured on this service"})

        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            # Attach user info to request state
            request.state.user = payload
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        # 4. Continue Request
        response = await call_next(request)
        return response
