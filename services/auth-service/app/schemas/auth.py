"""Pydantic schemas for authentication and identity."""

from pydantic import BaseModel


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    username: str
    password: str


class Token(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str
    expires_in: int


class UserResponse(BaseModel):
    """Schema for returning user data."""

    id: str
    username: str
    role: str
