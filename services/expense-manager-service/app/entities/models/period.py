"""Period (e.g., month-year) related entities for the Expense Manager Service."""

from pydantic import Field

from app.entities.models.base import BaseEntity


class Period(BaseEntity):
    """Entity representing date details with month and year."""

    month: int = Field(ge=1, le=12, description="Month of the year")
    year: int = Field(ge=2000, le=2100, description="Year of the entry")
