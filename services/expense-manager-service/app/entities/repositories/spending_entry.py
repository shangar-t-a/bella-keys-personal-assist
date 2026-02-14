"""Repository interface for spending accounts."""

from abc import ABC, abstractmethod

from app.entities.models.spending_entry import (
    SpendingEntry,
    SpendingEntryDetailWithCalc,
    SpendingEntryDetailWithCalcPage,
    SpendingEntryWithCalc,
    SpendingEntryWithCalcPage,
)


class SpendingEntryRepositoryInterface(ABC):
    """Interface for spending account repository."""

    @abstractmethod
    async def add_entry(self, entry: SpendingEntry) -> SpendingEntryWithCalc:
        """Add a new entry to the spending account."""
        pass

    @abstractmethod
    async def get_entry_by_id(self, entry_id: str) -> SpendingEntryWithCalc:
        """Retrieve a spending account entry by its ID."""
        pass

    @abstractmethod
    async def get_all_entries(self, limit: int = 12, offset: int = 0) -> SpendingEntryWithCalcPage:
        """Retrieve all entries for all spending accounts."""
        pass

    @abstractmethod
    async def get_all_entries_for_account(
        self, account_id: str, limit: int = 12, offset: int = 0
    ) -> SpendingEntryWithCalcPage:
        """Retrieve all entries for a given spending account."""
        pass

    @abstractmethod
    async def get_entry_by_account_and_period_or_none(
        self,
        account_id: str,
        period_id: str,
    ) -> SpendingEntryWithCalc | None:
        """Retrieve a specific entry for a given account and month-year."""
        pass

    @abstractmethod
    async def edit_entry(self, entry_id: str, entry: SpendingEntry) -> SpendingEntryWithCalc:
        """Edit an existing spending account entry."""
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: str) -> None:
        """Delete a spending account entry by its ID."""
        pass

    # Optimized methods with JOINs (N+1 query optimization)

    @abstractmethod
    async def add_entry_with_details(self, entry: SpendingEntry) -> SpendingEntryDetailWithCalc:
        """Add a new entry and return it with joined account and date details."""
        pass

    @abstractmethod
    async def get_entry_by_id_with_details(self, entry_id: str) -> SpendingEntryDetailWithCalc:
        """Retrieve a spending account entry by its ID with joined account and date details."""
        pass

    @abstractmethod
    async def get_all_entries_with_details(self, limit: int = 12, offset: int = 0) -> SpendingEntryDetailWithCalcPage:
        """Retrieve all entries with joined account and date details (optimized with JOIN)."""
        pass

    @abstractmethod
    async def get_all_entries_for_account_with_details(
        self, account_id: str, limit: int = 12, offset: int = 0
    ) -> SpendingEntryDetailWithCalcPage:
        """Retrieve all entries for an account with joined details (optimized with JOIN)."""
        pass

    @abstractmethod
    async def edit_entry_with_details(self, entry_id: str, entry: SpendingEntry) -> SpendingEntryDetailWithCalc:
        """Edit an existing entry and return it with joined account and date details."""
        pass
