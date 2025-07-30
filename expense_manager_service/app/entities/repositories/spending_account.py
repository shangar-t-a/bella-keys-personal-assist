"""Repository interface for spending accounts."""

from abc import ABC, abstractmethod

from app.entities.models.spending_account import SpendingAccountEntry, SpendingAccountEntryWithCalculatedFields


class SpendingAccountRepositoryInterface(ABC):
    """Interface for spending account repository."""

    @abstractmethod
    async def add_entry(self, entry: SpendingAccountEntry) -> SpendingAccountEntryWithCalculatedFields:
        """Add a new entry to the spending account."""
        pass

    @abstractmethod
    async def get_entry_by_id(self, entry_id: str) -> SpendingAccountEntryWithCalculatedFields:
        """Retrieve a spending account entry by its ID."""
        pass

    @abstractmethod
    async def get_all_entries(self) -> list[SpendingAccountEntryWithCalculatedFields]:
        """Retrieve all entries for all spending accounts."""
        pass

    @abstractmethod
    async def get_all_entries_for_account(self, account_id: str) -> list[SpendingAccountEntryWithCalculatedFields]:
        """Retrieve all entries for a given spending account."""
        pass

    @abstractmethod
    async def get_entry_by_account_and_month_year_or_none(
        self,
        account_id: str,
        month_year_id: str,
    ) -> SpendingAccountEntryWithCalculatedFields | None:
        """Retrieve a specific entry for a given account and month-year."""
        pass

    @abstractmethod
    async def edit_entry(self, entry_id: str, entry: SpendingAccountEntry) -> SpendingAccountEntryWithCalculatedFields:
        """Edit an existing spending account entry."""
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: str) -> None:
        """Delete a spending account entry by its ID."""
        pass
