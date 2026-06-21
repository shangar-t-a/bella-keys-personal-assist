"""Repository interface for liabilities."""

from abc import ABC, abstractmethod

from app.entities.models.liability import (
    Liability,
    LiabilityCategory,
    LiabilityFilter,
    LiabilitySort,
    LiabilitySubcategory,
    LiabilityTransaction,
)


class LiabilityRepositoryInterface(ABC):
    """Interface for liability repository."""

    @abstractmethod
    async def get_all_categories(self) -> list[LiabilityCategory]:
        """Retrieve all liability categories."""
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: str) -> LiabilityCategory | None:
        """Retrieve a liability category by its ID."""
        pass

    @abstractmethod
    async def get_category_by_code(self, category_code: str) -> LiabilityCategory | None:
        """Retrieve a liability category by its code."""
        pass

    @abstractmethod
    async def get_subcategory_by_id(self, subcategory_id: str) -> LiabilitySubcategory | None:
        """Retrieve a liability subcategory by its ID."""
        pass

    @abstractmethod
    async def add_liability(self, liability: Liability) -> Liability:
        """Add a new liability."""
        pass

    @abstractmethod
    async def get_liability_by_id(self, liability_id: str) -> Liability | None:
        """Retrieve a liability by its ID."""
        pass

    @abstractmethod
    async def edit_liability(self, liability_id: str, liability: Liability) -> Liability:
        """Edit an existing liability details."""
        pass

    @abstractmethod
    async def delete_liability(self, liability_id: str) -> None:
        """Delete a liability by its ID."""
        pass

    @abstractmethod
    async def get_all_liabilities(
        self, filters: LiabilityFilter | None = None, sort: LiabilitySort | None = None
    ) -> list[Liability]:
        """Retrieve all liabilities matching the query parameters."""
        pass

    @abstractmethod
    async def add_transaction(self, transaction: LiabilityTransaction) -> LiabilityTransaction:
        """Add a transaction to a liability."""
        pass

    @abstractmethod
    async def get_transactions_for_liability(self, liability_id: str) -> list[LiabilityTransaction]:
        """Retrieve all transactions logged for a liability, ordered by transaction date descending."""
        pass

    @abstractmethod
    async def get_transaction_by_id(self, transaction_id: str) -> LiabilityTransaction | None:
        """Retrieve a transaction by its ID."""
        pass

    @abstractmethod
    async def delete_transaction(self, transaction_id: str) -> None:
        """Delete a transaction by its ID."""
        pass
