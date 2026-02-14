"""Data access layer for spending account."""

from typing import ClassVar

from app.entities.errors.spending_account import SpendingAccountEntryNotFoundError
from app.entities.models.spending_account import SpendingAccountEntry, SpendingAccountEntryWithCalculatedFields
from app.entities.repositories.spending_account import SpendingAccountRepositoryInterface


class SpendingAccountRepository(SpendingAccountRepositoryInterface):
    """Implementation of the SpendingAccountRepositoryInterface."""

    entries: ClassVar = []

    def __init__(self):
        """Initialize the in-memory spending account repository."""
        pass

    async def add_entry(self, entry: SpendingAccountEntry) -> SpendingAccountEntryWithCalculatedFields:
        """Add a new entry to the spending account."""
        for existing_entry in self.entries:
            if existing_entry["period_id"] == entry.period_id:
                raise ValueError(f"Entry for date {entry.period_id} already exists.")
        new_entry = SpendingAccountEntryWithCalculatedFields(
            account_id=entry.account_id,
            period_id=entry.period_id,
            starting_balance=entry.starting_balance,
            current_balance=entry.current_balance,
            current_credit=entry.current_credit,
        )
        self.entries.append(new_entry.model_dump())
        return new_entry

    async def get_entry_by_id(self, entry_id: str) -> SpendingAccountEntryWithCalculatedFields:
        """Retrieve a spending account entry by its ID."""
        for entry in self.entries:
            if entry["id"] == entry_id:
                return SpendingAccountEntryWithCalculatedFields(**entry)
        raise SpendingAccountEntryNotFoundError(entry_id=entry_id)

    async def get_all_entries(self) -> list[SpendingAccountEntryWithCalculatedFields]:
        """Retrieve all entries for all spending accounts."""
        return [SpendingAccountEntryWithCalculatedFields(**entry) for entry in self.entries]

    async def get_all_entries_for_account(self, account_id: str) -> list[SpendingAccountEntryWithCalculatedFields]:
        """Retrieve all entries for a given spending account."""
        return [
            SpendingAccountEntryWithCalculatedFields(**entry)
            for entry in self.entries
            if entry["account_id"] == account_id
        ]

    async def get_entry_by_account_and_period_or_none(
        self, account_id: str, period_id: str
    ) -> SpendingAccountEntryWithCalculatedFields | None:
        """Retrieve a specific entry for a given account and month-year."""
        for entry in self.entries:
            if entry["account_id"] == account_id and entry["period_id"] == period_id:
                return SpendingAccountEntryWithCalculatedFields(**entry)
        return None

    async def edit_entry(self, entry_id: str, entry: SpendingAccountEntry) -> SpendingAccountEntryWithCalculatedFields:
        """Edit an existing spending account entry."""
        for idx, existing_entry in enumerate(self.entries):
            if existing_entry["id"] == entry_id:
                update_entry = entry.model_dump()
                update_entry["id"] = entry_id
                self.entries[idx] = update_entry
                return SpendingAccountEntryWithCalculatedFields(**self.entries[idx])
        raise SpendingAccountEntryNotFoundError(entry_id=entry_id)

    async def delete_entry(self, entry_id: str) -> None:
        """Delete a spending account entry by its ID."""
        for idx, entry in enumerate(self.entries):
            if entry["id"] == entry_id:
                del self.entries[idx]
                return
        raise SpendingAccountEntryNotFoundError(entry_id=entry_id)

    # Optimized methods with JOINs - not implemented for InMemory
    async def add_entry_with_details(self, entry):
        raise NotImplementedError("InMemory repository does not support optimized JOIN methods")

    async def get_entry_by_id_with_details(self, entry_id: str):
        raise NotImplementedError("InMemory repository does not support optimized JOIN methods")

    async def get_all_entries_with_details(self, limit: int = 12, offset: int = 0):
        raise NotImplementedError("InMemory repository does not support optimized JOIN methods")

    async def get_all_entries_for_account_with_details(self, account_id: str, limit: int = 12, offset: int = 0):
        raise NotImplementedError("InMemory repository does not support optimized JOIN methods")

    async def edit_entry_with_details(self, entry_id: str, entry):
        raise NotImplementedError("InMemory repository does not support optimized JOIN methods")
