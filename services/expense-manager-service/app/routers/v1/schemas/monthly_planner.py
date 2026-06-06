"""Schemas for the monthly planner."""

from pydantic import BaseModel, Field

from app.entities.models.monthly_planner import CategoryL1, ExpenseStatus


class MonthlyCategoryBase(BaseModel):
    """Base schema for a monthly category."""

    name: str
    category_l1: CategoryL1


class MonthlyCategoryResponse(MonthlyCategoryBase):
    """Response schema for a monthly category."""

    id: str


class MonthlySummaryResponse(BaseModel):
    """Response schema for a monthly summary."""

    salary: float
    month: int
    year: int


class MonthlyExpenseItemBase(BaseModel):
    """Base schema for a monthly expense item."""

    name: str
    amount: float
    category_l1: CategoryL1
    category_l2: str
    is_recurring: bool


class MonthlyExpenseItemRequest(MonthlyExpenseItemBase):
    """Request schema for creating/updating a monthly expense item."""

    status: ExpenseStatus = Field(default=ExpenseStatus.PENDING)


class MonthlyExpenseItemResponse(MonthlyExpenseItemBase):
    """Response schema for a monthly expense item."""

    id: str
    status: ExpenseStatus
    month: int
    year: int


class UpdateSalaryRequest(BaseModel):
    """Request schema for updating monthly salary."""

    salary: float
