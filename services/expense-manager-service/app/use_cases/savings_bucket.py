"""Use case service for savings buckets and transactions."""

import uuid
from datetime import UTC, datetime

from app.entities.models.savings_bucket import SavingsBucket, SavingsBucketTransaction
from app.entities.repositories.savings_bucket import SavingsBucketRepositoryInterface
from app.use_cases.errors.savings_bucket import (
    SavingsBucketDuplicateNameError,
    SavingsBucketInsufficientFundsError,
    SavingsBucketNotFoundError,
    SavingsBucketProtectedError,
)


class SavingsBucketService:
    """Savings bucket service handling core allocation and ledger logic."""

    def __init__(self, savings_bucket_repository: SavingsBucketRepositoryInterface):
        """Initialize the service with the repository."""
        self.savings_bucket_repository = savings_bucket_repository

    async def get_buckets_for_account(self, account_id: str) -> list[SavingsBucket]:
        """Retrieve all buckets for a given account. Auto-seeds default buckets if empty."""
        buckets = await self.savings_bucket_repository.get_buckets_for_account(account_id=account_id)

        # If no buckets exist, auto-seed default ones
        if not buckets:
            default_names = ["Savings", "Minimum Balance", "Medical Insurance", "LIC"]
            seeded_buckets = []
            for name in default_names:
                new_bucket = SavingsBucket(
                    id=uuid.uuid4().hex,
                    account_id=account_id,
                    name=name,
                    allocated_amount=0.0,
                    target_amount=None,
                )
                seeded = await self.savings_bucket_repository.create_bucket(bucket=new_bucket)
                seeded_buckets.append(seeded)
            return seeded_buckets

        return buckets

    async def create_bucket(self, account_id: str, name: str, target_amount: float | None = None) -> SavingsBucket:
        """Create a new savings bucket directly."""
        cleaned_name = name.strip()
        existing = await self.savings_bucket_repository.get_bucket_by_name_and_account(
            account_id=account_id, name=cleaned_name
        )
        if existing is not None:
            raise SavingsBucketDuplicateNameError(name=cleaned_name)

        new_bucket = SavingsBucket(
            id=uuid.uuid4().hex,
            account_id=account_id,
            name=cleaned_name,
            allocated_amount=0.0,
            target_amount=target_amount,
        )
        return await self.savings_bucket_repository.create_bucket(bucket=new_bucket)

    async def edit_bucket(self, bucket_id: str, name: str, target_amount: float | None = None) -> SavingsBucket:
        """Edit a savings bucket's name or target. Renaming root Savings is blocked."""
        bucket = await self.savings_bucket_repository.get_bucket_by_id(bucket_id=bucket_id)
        if bucket is None:
            raise SavingsBucketNotFoundError(bucket_id=bucket_id)

        cleaned_name = name.strip()
        if bucket.name == "Savings" and cleaned_name != "Savings":
            raise SavingsBucketProtectedError(name="Savings")

        if cleaned_name != bucket.name:
            existing = await self.savings_bucket_repository.get_bucket_by_name_and_account(
                account_id=bucket.account_id, name=cleaned_name
            )
            if existing is not None:
                raise SavingsBucketDuplicateNameError(name=cleaned_name)

        return await self.savings_bucket_repository.update_bucket(
            bucket_id=bucket_id, name=cleaned_name, target_amount=target_amount
        )

    async def delete_bucket(self, bucket_id: str) -> None:
        """Delete a bucket. Remaining funds are automatically refunded to 'Savings' bucket."""
        bucket = await self.savings_bucket_repository.get_bucket_by_id(bucket_id=bucket_id)
        if bucket is None:
            raise SavingsBucketNotFoundError(bucket_id=bucket_id)

        if bucket.name == "Savings":
            raise SavingsBucketProtectedError(name="Savings")

        # Safe Deletion: Transfer remaining balance back to Savings
        if bucket.allocated_amount > 0.0:
            savings_bucket = await self.savings_bucket_repository.get_bucket_by_name_and_account(
                account_id=bucket.account_id, name="Savings"
            )
            if savings_bucket is None:
                # Should not happen under normal usage, but raise error just in case
                raise SavingsBucketNotFoundError(bucket_id="Root 'Savings' bucket")

            # Update Savings bucket balance
            new_savings_balance = savings_bucket.allocated_amount + bucket.allocated_amount
            await self.savings_bucket_repository.update_bucket_balance(
                bucket_id=savings_bucket.id, allocated_amount=new_savings_balance
            )

            # Log refund transaction
            refund_tx = SavingsBucketTransaction(
                id=uuid.uuid4().hex,
                account_id=bucket.account_id,
                source_bucket_id=bucket.id,
                destination_bucket_id=savings_bucket.id,
                amount=bucket.allocated_amount,
                transaction_type="release",
                description=f"Refunded remaining balance upon deletion of bucket '{bucket.name}'",
                transaction_date=datetime.now(UTC),
            )
            await self.savings_bucket_repository.add_transaction(transaction=refund_tx)

        # Delete bucket
        await self.savings_bucket_repository.delete_bucket(bucket_id=bucket_id)

    async def add_transaction(  # noqa: PLR0913
        self,
        account_id: str,
        source_bucket_id: str | None,
        destination_bucket_id: str | None,
        amount: float,
        transaction_type: str,
        description: str,
        transaction_date: datetime | None = None,
    ) -> SavingsBucketTransaction:
        """Execute a fund transaction, adjusting bucket balances atomically in the database."""
        if amount <= 0.0:
            raise ValueError("Transaction amount must be greater than zero.")

        tx_date = transaction_date if transaction_date else datetime.now(UTC)

        # 1. Update source bucket if applicable
        if source_bucket_id:
            src_bucket = await self.savings_bucket_repository.get_bucket_by_id(bucket_id=source_bucket_id)
            if src_bucket is None:
                raise SavingsBucketNotFoundError(bucket_id=source_bucket_id)
            if src_bucket.account_id != account_id:
                raise ValueError("Source bucket does not belong to the selected account.")
            if src_bucket.allocated_amount < amount:
                raise SavingsBucketInsufficientFundsError(
                    name=src_bucket.name,
                    current_balance=src_bucket.allocated_amount,
                    requested_amount=amount,
                )

            # Deduct balance
            new_src_balance = src_bucket.allocated_amount - amount
            await self.savings_bucket_repository.update_bucket_balance(
                bucket_id=source_bucket_id, allocated_amount=new_src_balance
            )

        # 2. Update destination bucket if applicable
        if destination_bucket_id:
            dest_bucket = await self.savings_bucket_repository.get_bucket_by_id(bucket_id=destination_bucket_id)
            if dest_bucket is None:
                raise SavingsBucketNotFoundError(bucket_id=destination_bucket_id)
            if dest_bucket.account_id != account_id:
                raise ValueError("Destination bucket does not belong to the selected account.")

            # Add balance
            new_dest_balance = dest_bucket.allocated_amount + amount
            await self.savings_bucket_repository.update_bucket_balance(
                bucket_id=destination_bucket_id, allocated_amount=new_dest_balance
            )

        # 3. Create transaction log
        new_tx = SavingsBucketTransaction(
            id=uuid.uuid4().hex,
            account_id=account_id,
            source_bucket_id=source_bucket_id,
            destination_bucket_id=destination_bucket_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description.strip(),
            transaction_date=tx_date,
        )
        return await self.savings_bucket_repository.add_transaction(transaction=new_tx)

    async def get_transactions_for_account(
        self, account_id: str, limit: int = 50, offset: int = 0
    ) -> list[SavingsBucketTransaction]:
        """Retrieve paginated transaction history logs."""
        return await self.savings_bucket_repository.get_transactions_for_account(
            account_id=account_id, limit=limit, offset=offset
        )

    async def get_transactions_count_for_account(self, account_id: str) -> int:
        """Get total transaction count."""
        return await self.savings_bucket_repository.get_transactions_count_for_account(account_id=account_id)
