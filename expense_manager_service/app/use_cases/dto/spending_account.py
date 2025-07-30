"""DTO (Data Transfer Object) classes for spending account-related use cases."""

from pydantic import Field, model_validator

from app.use_cases.dto.base import BaseUseCaseDTO


class SpendingAccountEntryDTO(BaseUseCaseDTO):
    """DTO for spending account entry."""

    account_name: str = Field(..., description="Name of the spending account", examples=["ICICI", "SBI"])
    month: str = Field(..., description="Month of the entry", examples=["January", "February"])
    year: int = Field(..., ge=2000, le=2100, description="Year between 2000 and 2100", examples=[2024, 2025])
    starting_balance: float = Field(..., description="Starting balance of the account", examples=[10000.0])
    current_balance: float = Field(..., description="Current balance of the account", examples=[8000.0])
    current_credit: float = Field(..., description="Current credit of the account", examples=[2000.0])


class SpendingAccountEntryWithCalculatedFieldsDTO(SpendingAccountEntryDTO):
    """DTO for spending account entry with calculated fields for API responses."""

    balance_after_credit: float = Field(default=0, description="Balance after deducting credit")
    total_spent: float = Field(default=0, description="Total amount spent from the account")

    @model_validator(mode="before")
    @classmethod
    def calculate_fields(cls, values) -> "SpendingAccountEntryWithCalculatedFieldsDTO":
        """Calculate balance after credit and total spent."""
        values["balance_after_credit"] = values["current_balance"] - values["current_credit"]
        values["total_spent"] = (values["starting_balance"] - values["current_balance"]) + values["current_credit"]
        return values
