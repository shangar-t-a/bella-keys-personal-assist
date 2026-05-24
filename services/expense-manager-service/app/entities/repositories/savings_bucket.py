"""Repository interface for savings buckets and transactions."""

from abc import ABC, abstractmethod

from app.entities.models.savings_bucket import SavingsBucket, SavingsBucketTransaction


class SavingsBucketRepositoryInterface(ABC):
    """Interface for savings bucket repository."""

    @abstractmethod
    async def get_buckets_for_account(self, account_id: str) -> list[SavingsBucket]:
        """Retrieve all buckets for a given account."""
        pass

    @abstractmethod
    async def create_bucket(self, bucket: SavingsBucket) -> SavingsBucket:
        """Create a new savings bucket."""
        pass

    @abstractmethod
    async def get_bucket_by_id(self, bucket_id: str) -> SavingsBucket | None:
        """Retrieve a savings bucket by its ID."""
        pass

    @abstractmethod
    async def get_bucket_by_name_and_account(self, account_id: str, name: str) -> SavingsBucket | None:
        """Retrieve a savings bucket by its name and parent account ID."""
        pass

    @abstractmethod
    async def update_bucket(self, bucket_id: str, name: str, target_amount: float | None) -> SavingsBucket:
        """Update a savings bucket's details (name and target amount)."""
        pass

    @abstractmethod
    async def update_bucket_balance(self, bucket_id: str, allocated_amount: float) -> SavingsBucket:
        """Update a savings bucket's allocated balance."""
        pass

    @abstractmethod
    async def delete_bucket(self, bucket_id: str) -> None:
        """Delete a savings bucket by its ID."""
        pass

    @abstractmethod
    async def add_transaction(self, transaction: SavingsBucketTransaction) -> SavingsBucketTransaction:
        """Add a new transaction log for a bucket."""
        pass

    @abstractmethod
    async def get_transactions_for_account(
        self, account_id: str, limit: int = 50, offset: int = 0
    ) -> list[SavingsBucketTransaction]:
        """Retrieve all transactions associated with a given account with pagination."""
        pass

    @abstractmethod
    async def get_transactions_count_for_account(self, account_id: str) -> int:
        """Get the total count of transactions for an account."""
        pass

    @abstractmethod
    async def get_transaction_by_id(self, transaction_id: str) -> SavingsBucketTransaction | None:
        """Retrieve a specific transaction by its ID."""
        pass

    @abstractmethod
    async def cancel_transaction(self, transaction_id: str, reason: str) -> SavingsBucketTransaction:
        """Mark a transaction as cancelled in the database."""
        pass
