"""SQLite models for spending accounts."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructures.sqlite_db.database import Base


class SpendingAccountEntryModel(Base):
    """SQLite model for spending account entries."""

    __tablename__ = "spending_account_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    account_id: Mapped[str] = mapped_column(
        String, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date_detail_id: Mapped[str] = mapped_column(
        String, ForeignKey("month_years.id", ondelete="CASCADE"), nullable=False, index=True
    )
    starting_balance: Mapped[float] = mapped_column(Float, nullable=False)
    current_balance: Mapped[float] = mapped_column(Float, nullable=False)
    current_credit: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(UTC), onupdate=datetime.now(UTC))

    __table_args__ = (UniqueConstraint("account_id", "date_detail_id", name="uq_account_date_detail"),)
