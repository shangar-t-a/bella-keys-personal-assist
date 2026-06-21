"""Core request context variables for the Bella Chat Service."""

from contextvars import ContextVar

# ContextVar to hold user authorization token during request execution
current_auth_header: ContextVar[str | None] = ContextVar("current_auth_header", default=None)
