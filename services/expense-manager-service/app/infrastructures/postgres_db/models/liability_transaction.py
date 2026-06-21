"""Postgres model for liability transactions."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructures.postgres_db.database import Base


class LiabilityTransactionModel(Base):
    """Postgres model for liability transactions."""

    __tablename__ = "liability_transaction"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    liability_id: Mapped[str] = mapped_column(
        String, ForeignKey("liability.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # BORROW, REPAY, REVALUE
    transaction_type: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
