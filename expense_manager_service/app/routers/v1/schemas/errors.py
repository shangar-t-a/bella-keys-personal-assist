"""Schemas for error responses."""

from pydantic import BaseModel


class HTTPErrorResponse(BaseModel):
    """Base schema for HTTP error responses."""

    detail: str
