"""Schemas for period endpoints."""

from pydantic import Field

from app.routers.v1.schemas.base import BaseSchema


class PeriodRequest(BaseSchema):
    """Schema for month-year creation requests."""

    month: int = Field(..., ge=1, le=12, description="Month as an integer between 1 and 12", examples=[1, 2, 3])
    year: int = Field(..., ge=2000, le=2100, description="Year between 2000 and 2100", examples=[2024, 2025])


class PeriodResponse(BaseSchema):
    """Schema for month-year responses."""

    id: str = Field(..., description="Unique identifier for the month-year combination")
    month: int = Field(..., ge=1, le=12, description="Month as an integer between 1 and 12", examples=[1, 2, 3])
    year: int = Field(..., description="Year value")
