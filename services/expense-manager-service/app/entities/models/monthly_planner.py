"""Monthly Planner related entities for the Expense Manager Service."""

from enum import StrEnum

from pydantic import Field

from app.entities.models.base import BaseEntity


class CategoryL1(StrEnum):
    """Level 1 categories for expenses."""

    SPENDING = "spending"
    SAVING = "saving"


class ExpenseStatus(StrEnum):
    """Status of an expense item."""

    PENDING = "pending"
    SETTLED = "settled"


class MonthlyCategory(BaseEntity):
    """Entity representing a custom level 2 category."""

    name: str = Field(description="Name of the category")
    category_l1: CategoryL1 = Field(description="Level 1 category it belongs to")


class MonthlySummary(BaseEntity):
    """Entity representing the monthly summary (salary, etc.)."""

    period_id: str = Field(description="Internal FK to the period record")
    salary: float = Field(default=0.0, description="Monthly salary/income")


class MonthlyExpenseItem(BaseEntity):
    """Entity representing an individual expense item for a month."""

    period_id: str = Field(description="Internal FK to the period record")
    name: str = Field(description="Name of the expense")
    amount: float = Field(description="Amount of the expense")
    status: ExpenseStatus = Field(default=ExpenseStatus.PENDING, description="Current status")
    category_l1: CategoryL1 = Field(description="Level 1 category")
    category_l2: str = Field(description="Level 2 category name")
    is_recurring: bool = Field(default=True, description="Whether this expense repeats monthly")


class MonthlySummaryDetail(BaseEntity):
    """Monthly summary with human-readable period details, for use at the API boundary."""

    salary: float = Field(default=0.0, description="Monthly salary/income")
    month: int = Field(description="Calendar month (1-12)")
    year: int = Field(description="Calendar year")


class MonthlyExpenseItemDetail(BaseEntity):
    """Monthly expense item with human-readable period details, for use at the API boundary."""

    name: str = Field(description="Name of the expense")
    amount: float = Field(description="Amount of the expense")
    status: ExpenseStatus = Field(default=ExpenseStatus.PENDING, description="Current status")
    category_l1: CategoryL1 = Field(description="Level 1 category")
    category_l2: str = Field(description="Level 2 category name")
    is_recurring: bool = Field(default=True, description="Whether this expense repeats monthly")
    month: int = Field(description="Calendar month (1-12)")
    year: int = Field(description="Calendar year")
