"""Schemas for accounts endpoints."""

from pydantic import Field

from app.routers.v1.schemas.base import BaseSchema


class AccountNameRequest(BaseSchema):
    """Schema for account name creation/update requests."""

    account_name: str = Field(..., description="Name of the account", examples=["ICICI", "SBI"])


class AccountNameResponse(BaseSchema):
    """Schema for account name responses."""

    id: str = Field(..., description="Unique identifier for the account")
    account_name: str = Field(..., description="Name of the account")


class AccountUpdateRequest(BaseSchema):
    """Schema for account update requests."""

    account_name: str = Field(..., description="New name for the account", examples=["ICICI"])
