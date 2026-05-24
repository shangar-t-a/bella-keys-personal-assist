"""Postgres repository implementation for savings buckets and transactions."""


from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.models.savings_bucket import SavingsBucket, SavingsBucketTransaction
from app.entities.repositories.savings_bucket import SavingsBucketRepositoryInterface
from app.infrastructures.postgres_db.database import get_async_session
from app.infrastructures.postgres_db.models.savings_bucket import (
    SavingsBucketModel,
    SavingsBucketTransactionModel,
)


class PostgresSavingsBucketRepository(SavingsBucketRepositoryInterface):
    """Postgres implementation of the SavingsBucketRepositoryInterface."""

    def __init__(self):
        """Initialize the Postgres savings bucket repository."""
        self.session_factory = get_async_session()

    async def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    async def get_buckets_for_account(self, account_id: str) -> list[SavingsBucket]:
        """Retrieve all buckets for a given account."""
        async with await self._get_session() as session:
            stmt = (
                select(SavingsBucketModel)
                .where(SavingsBucketModel.account_id == account_id)
                .order_by(SavingsBucketModel.name)
            )
            result = await session.execute(stmt)
            buckets = result.scalars().all()
            return [
                SavingsBucket(
                    id=b.id,
                    account_id=b.account_id,
                    name=b.name,
                    allocated_amount=b.allocated_amount,
                    target_amount=b.target_amount,
                )
                for b in buckets
            ]

    async def create_bucket(self, bucket: SavingsBucket) -> SavingsBucket:
        """Create a new savings bucket."""
        async with await self._get_session() as session:
            db_bucket = SavingsBucketModel(
                id=bucket.id,
                account_id=bucket.account_id,
                name=bucket.name,
                allocated_amount=bucket.allocated_amount,
                target_amount=bucket.target_amount,
            )
            session.add(db_bucket)
            await session.commit()
            await session.refresh(db_bucket)
            return SavingsBucket(
                id=db_bucket.id,
                account_id=db_bucket.account_id,
                name=db_bucket.name,
                allocated_amount=db_bucket.allocated_amount,
                target_amount=db_bucket.target_amount,
            )

    async def get_bucket_by_id(self, bucket_id: str) -> SavingsBucket | None:
        """Retrieve a savings bucket by its ID."""
        async with await self._get_session() as session:
            stmt = select(SavingsBucketModel).where(SavingsBucketModel.id == bucket_id)
            result = await session.execute(stmt)
            b = result.scalar_one_or_none()
            if b is None:
                return None
            return SavingsBucket(
                id=b.id,
                account_id=b.account_id,
                name=b.name,
                allocated_amount=b.allocated_amount,
                target_amount=b.target_amount,
            )

    async def get_bucket_by_name_and_account(self, account_id: str, name: str) -> SavingsBucket | None:
        """Retrieve a savings bucket by its name and parent account ID."""
        async with await self._get_session() as session:
            stmt = select(SavingsBucketModel).where(
                SavingsBucketModel.account_id == account_id,
                SavingsBucketModel.name == name,
            )
            result = await session.execute(stmt)
            b = result.scalar_one_or_none()
            if b is None:
                return None
            return SavingsBucket(
                id=b.id,
                account_id=b.account_id,
                name=b.name,
                allocated_amount=b.allocated_amount,
                target_amount=b.target_amount,
            )

    async def update_bucket(self, bucket_id: str, name: str, target_amount: float | None) -> SavingsBucket:
        """Update a savings bucket's details (name and target amount)."""
        async with await self._get_session() as session:
            stmt = select(SavingsBucketModel).where(SavingsBucketModel.id == bucket_id)
            result = await session.execute(stmt)
            db_bucket = result.scalar_one_or_none()
            if db_bucket is None:
                raise ValueError(f"Bucket with ID '{bucket_id}' not found.")
            db_bucket.name = name
            db_bucket.target_amount = target_amount
            await session.commit()
            await session.refresh(db_bucket)
            return SavingsBucket(
                id=db_bucket.id,
                account_id=db_bucket.account_id,
                name=db_bucket.name,
                allocated_amount=db_bucket.allocated_amount,
                target_amount=db_bucket.target_amount,
            )

    async def update_bucket_balance(self, bucket_id: str, allocated_amount: float) -> SavingsBucket:
        """Update a savings bucket's allocated balance."""
        async with await self._get_session() as session:
            stmt = select(SavingsBucketModel).where(SavingsBucketModel.id == bucket_id)
            result = await session.execute(stmt)
            db_bucket = result.scalar_one_or_none()
            if db_bucket is None:
                raise ValueError(f"Bucket with ID '{bucket_id}' not found.")
            db_bucket.allocated_amount = allocated_amount
            await session.commit()
            await session.refresh(db_bucket)
            return SavingsBucket(
                id=db_bucket.id,
                account_id=db_bucket.account_id,
                name=db_bucket.name,
                allocated_amount=db_bucket.allocated_amount,
                target_amount=db_bucket.target_amount,
            )

    async def delete_bucket(self, bucket_id: str) -> None:
        """Delete a savings bucket by its ID."""
        async with await self._get_session() as session:
            stmt = select(SavingsBucketModel).where(SavingsBucketModel.id == bucket_id)
            result = await session.execute(stmt)
            db_bucket = result.scalar_one_or_none()
            if db_bucket is not None:
                await session.delete(db_bucket)
                await session.commit()

    async def add_transaction(self, transaction: SavingsBucketTransaction) -> SavingsBucketTransaction:
        """Add a new transaction log for a bucket."""
        async with await self._get_session() as session:
            db_tx = SavingsBucketTransactionModel(
                id=transaction.id,
                account_id=transaction.account_id,
                source_bucket_id=transaction.source_bucket_id,
                destination_bucket_id=transaction.destination_bucket_id,
                amount=transaction.amount,
                transaction_type=transaction.transaction_type,
                description=transaction.description,
                transaction_date=transaction.transaction_date,
                is_cancelled=transaction.is_cancelled,
                cancellation_reason=transaction.cancellation_reason,
            )
            session.add(db_tx)
            await session.commit()
            await session.refresh(db_tx)
            return SavingsBucketTransaction(
                id=db_tx.id,
                account_id=db_tx.account_id,
                source_bucket_id=db_tx.source_bucket_id,
                destination_bucket_id=db_tx.destination_bucket_id,
                amount=db_tx.amount,
                transaction_type=db_tx.transaction_type,
                description=db_tx.description,
                transaction_date=db_tx.transaction_date,
                is_cancelled=db_tx.is_cancelled,
                cancellation_reason=db_tx.cancellation_reason,
            )

    async def get_transactions_for_account(
        self, account_id: str, limit: int = 50, offset: int = 0
    ) -> list[SavingsBucketTransaction]:
        """Retrieve all transactions associated with a given account with pagination."""
        async with await self._get_session() as session:
            stmt = (
                select(SavingsBucketTransactionModel)
                .where(SavingsBucketTransactionModel.account_id == account_id)
                .order_by(
                    SavingsBucketTransactionModel.transaction_date.desc(),
                    SavingsBucketTransactionModel.created_at.desc(),
                )
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            txs = result.scalars().all()
            return [
                SavingsBucketTransaction(
                    id=t.id,
                    account_id=t.account_id,
                    source_bucket_id=t.source_bucket_id,
                    destination_bucket_id=t.destination_bucket_id,
                    amount=t.amount,
                    transaction_type=t.transaction_type,
                    description=t.description,
                    transaction_date=t.transaction_date,
                    is_cancelled=t.is_cancelled,
                    cancellation_reason=t.cancellation_reason,
                )
                for t in txs
            ]

    async def get_transactions_count_for_account(self, account_id: str) -> int:
        """Get the total count of transactions for an account."""
        async with await self._get_session() as session:
            stmt = select(func.count(SavingsBucketTransactionModel.id)).where(
                SavingsBucketTransactionModel.account_id == account_id
            )
            result = await session.execute(stmt)
            return result.scalar_one()

    async def get_transaction_by_id(self, transaction_id: str) -> SavingsBucketTransaction | None:
        """Retrieve a specific transaction by its ID."""
        async with await self._get_session() as session:
            stmt = select(SavingsBucketTransactionModel).where(SavingsBucketTransactionModel.id == transaction_id)
            result = await session.execute(stmt)
            t = result.scalar_one_or_none()
            if t is None:
                return None
            return SavingsBucketTransaction(
                id=t.id,
                account_id=t.account_id,
                source_bucket_id=t.source_bucket_id,
                destination_bucket_id=t.destination_bucket_id,
                amount=t.amount,
                transaction_type=t.transaction_type,
                description=t.description,
                transaction_date=t.transaction_date,
                is_cancelled=t.is_cancelled,
                cancellation_reason=t.cancellation_reason,
            )

    async def cancel_transaction(self, transaction_id: str, reason: str) -> SavingsBucketTransaction:
        """Mark a transaction as cancelled in the database."""
        async with await self._get_session() as session:
            stmt = select(SavingsBucketTransactionModel).where(SavingsBucketTransactionModel.id == transaction_id)
            result = await session.execute(stmt)
            db_tx = result.scalar_one_or_none()
            if db_tx is None:
                raise ValueError(f"Transaction with ID '{transaction_id}' not found.")
            db_tx.is_cancelled = True
            db_tx.cancellation_reason = reason
            await session.commit()
            await session.refresh(db_tx)
            return SavingsBucketTransaction(
                id=db_tx.id,
                account_id=db_tx.account_id,
                source_bucket_id=db_tx.source_bucket_id,
                destination_bucket_id=db_tx.destination_bucket_id,
                amount=db_tx.amount,
                transaction_type=db_tx.transaction_type,
                description=db_tx.description,
                transaction_date=db_tx.transaction_date,
                is_cancelled=db_tx.is_cancelled,
                cancellation_reason=db_tx.cancellation_reason,
            )
