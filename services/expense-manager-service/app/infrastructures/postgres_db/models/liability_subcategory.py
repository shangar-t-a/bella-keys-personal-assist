"""Postgres model for liability subcategory."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructures.postgres_db.database import Base


class LiabilitySubcategoryModel(Base):
    """Postgres model for liability subcategories."""

    __tablename__ = "liability_subcategory"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    category_id: Mapped[str] = mapped_column(
        String, ForeignKey("liability_category.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    valuation_type: Mapped[str] = mapped_column(String, nullable=False)  # VALUE_BASED, UNIT_BASED
    has_interest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_maturity: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )
