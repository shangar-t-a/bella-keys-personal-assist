"""Postgres model for liability."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructures.postgres_db.database import Base


class LiabilityModel(Base):
    """Postgres model for liabilities."""

    __tablename__ = "liability"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    category_id: Mapped[str] = mapped_column(
        String, ForeignKey("liability_category.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    subcategory_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("liability_subcategory.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    original_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    current_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    interest_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    interest_compounding: Mapped[str | None] = mapped_column(String, nullable=True)
    emi_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    maturity_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
