"""Schemas for pagination parameters."""

from pydantic import Field

from app.routers.v1.schemas.base import BaseSchema


class PaginationParams(BaseSchema):
    """Schema for pagination parameters."""

    limit: int = Field(12, ge=1, le=100, description="Number of items to return", examples=[12])
    offset: int = Field(
        0, ge=0, description="Number of items to skip before starting to collect the result set", examples=[0]
    )
