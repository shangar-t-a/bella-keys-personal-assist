"""Postgres models for savings buckets and transactions."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructures.postgres_db.database import Base


class SavingsBucketModel(Base):
    """Postgres model for savings buckets."""

    __tablename__ = "savings_bucket"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    account_id: Mapped[str] = mapped_column(
        String, ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    allocated_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    target_amount: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(UTC), onupdate=datetime.now(UTC)
    )

    __table_args__ = (UniqueConstraint("account_id", "name", name="uq_account_bucket_name"),)


class SavingsBucketTransactionModel(Base):
    """Postgres model for savings bucket transactions."""

    __tablename__ = "savings_bucket_transaction"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    account_id: Mapped[str] = mapped_column(
        String, ForeignKey("account.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_bucket_id: Mapped[str] = mapped_column(
        String, ForeignKey("savings_bucket.id", ondelete="SET NULL"), nullable=True, index=True
    )
    destination_bucket_id: Mapped[str] = mapped_column(
        String, ForeignKey("savings_bucket.id", ondelete="SET NULL"), nullable=True, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    # 'deposit', 'withdraw', 'allocate', 'release', 'transfer'
    transaction_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    is_cancelled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cancellation_reason: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
