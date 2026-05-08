"""SQLite models for the monthly planner."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Boolean, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.infrastructures.sqlite_db.database import Base


class MonthlyCategoryModel(Base):
    """SQLite model for custom level 2 categories."""
    __tablename__ = "monthly_categories"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category_l1: Mapped[str] = mapped_column(String, nullable=False)  # spending/saving
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))

    __table_args__ = (UniqueConstraint("name", "category_l1", name="uq_category_name_l1"),)


class MonthlySummaryModel(Base):
    """SQLite model for monthly summary (salary)."""
    __tablename__ = "monthly_summaries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    period_id: Mapped[str] = mapped_column(
        String, ForeignKey("period.id", ondelete="CASCADE"), nullable=False, index=True
    )
    salary: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC), onupdate=datetime.now(UTC))

    __table_args__ = (UniqueConstraint("period_id", name="uq_summary_period"),)


class MonthlyExpenseItemModel(Base):
    """SQLite model for individual expense items."""
    __tablename__ = "monthly_expense_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    period_id: Mapped[str] = mapped_column(
        String, ForeignKey("period.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")  # pending/settled
    category_l1: Mapped[str] = mapped_column(String, nullable=False)
    category_l2: Mapped[str] = mapped_column(String, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC), onupdate=datetime.now(UTC))
