"""DTO (Data Transfer Object) classes for account-related use cases."""

from typing import Literal

from pydantic import Field

from app.use_cases.dto.base import BaseUseCaseDTO

MonthLiteral = Literal[
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


class AccountNameDTO(BaseUseCaseDTO):
    """DTO for account name entity."""

    account_name: str


class MonthYearDTO(BaseUseCaseDTO):
    """DTO for month year entity."""

    month: MonthLiteral
    year: int = Field(ge=2000, le=2100)
