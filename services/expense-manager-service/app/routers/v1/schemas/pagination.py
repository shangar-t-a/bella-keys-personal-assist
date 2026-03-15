"""Schemas for pagination parameters.

Pagination is a low level concern that is used across multiple schemas. Other high level schemas can import and use
these pagination schemas to include pagination parameters and metadata in their requests and responses. But these
schemas should not import any high level schemas to avoid circular dependencies.
"""

from pydantic import Field

from app.routers.v1.schemas.base import BaseSchema


class PaginationParams(BaseSchema):
    """Schema for pagination parameters."""

    size: int = Field(12, ge=1, le=100, description="Number of items per page", examples=[12])
    page: int = Field(0, ge=0, description="Page number to retrieve. Page numbering starts from 0", examples=[0])


class PaginationResponse(BaseSchema):
    """Schema for pagination response metadata."""

    number: int = Field(..., description="Page number returned in the current page", examples=[0])
    size: int = Field(..., description="Number of items returned in the current page", examples=[12])
    total_elements: int = Field(..., description="Total number of elements available", examples=[100])
    total_pages: int = Field(..., description="Total number of pages available", examples=[9])
