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
            if existing_entry["date_detail_id"] == entry.date_detail_id:
                raise ValueError(f"Entry for date {entry.date_detail_id} already exists.")
        new_entry = SpendingAccountEntryWithCalculatedFields(
            account_id=entry.account_id,
            date_detail_id=entry.date_detail_id,
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

    async def get_entry_by_account_and_month_year_or_none(
        self, account_id: str, month_year_id: str
    ) -> SpendingAccountEntryWithCalculatedFields | None:
        """Retrieve a specific entry for a given account and month-year."""
        for entry in self.entries:
            if entry["account_id"] == account_id and entry["date_detail_id"] == month_year_id:
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
