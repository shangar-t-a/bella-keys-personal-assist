"""Pagination models for use cases.

Pagination is a low level concern that is used across multiple use cases. Other high level use case models can import
and use these pagination models to include pagination parameters and metadata in their requests and responses. But these
models should not import any high level use case models to avoid circular dependencies.
"""

from pydantic import Field

from app.use_cases.models.base import BaseEntity


class Page(BaseEntity):
    """Model for paginated results."""

    number: int = Field(..., description="Page number returned in the current page", examples=[0])
    size: int = Field(..., description="Number of items returned in the current page", examples=[12])
    total_elements: int = Field(..., description="Total number of elements available", examples=[100])
    total_pages: int = Field(..., description="Total number of pages available", examples=[9])
