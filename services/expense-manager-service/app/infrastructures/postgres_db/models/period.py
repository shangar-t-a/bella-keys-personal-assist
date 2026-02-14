"""Postgres models for period."""

import uuid
from datetime import (
    UTC,
    datetime,
)

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructures.postgres_db.database import Base


class PeriodModel(Base):
    """Postgres model for month-year records."""

    __tablename__ = "period"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    month: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    __table_args__ = (
        UniqueConstraint("month", "year", name="uq_period"),
        CheckConstraint("month >= 1 AND month <= 12", name="chk_month_range"),
    )
