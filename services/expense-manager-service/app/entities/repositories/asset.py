"""Repository interface for assets."""

from abc import ABC, abstractmethod

from app.entities.models.asset import (
    Asset,
    AssetCategory,
    AssetFilter,
    AssetSort,
    AssetTransaction,
)


class AssetRepositoryInterface(ABC):
    """Interface for asset repository."""

    @abstractmethod
    async def get_all_categories(self) -> list[AssetCategory]:
        """Retrieve all asset categories."""
        pass

    @abstractmethod
    async def get_category_by_id(self, category_id: str) -> AssetCategory | None:
        """Retrieve an asset category by its ID."""
        pass

    @abstractmethod
    async def get_category_by_code(self, category_code: str) -> AssetCategory | None:
        """Retrieve an asset category by its code."""
        pass

    @abstractmethod
    async def add_asset(self, asset: Asset) -> Asset:
        """Add a new asset."""
        pass

    @abstractmethod
    async def get_asset_by_id(self, asset_id: str) -> Asset | None:
        """Retrieve an asset by its ID."""
        pass

    @abstractmethod
    async def edit_asset(self, asset_id: str, asset: Asset) -> Asset:
        """Edit an existing asset details."""
        pass

    @abstractmethod
    async def delete_asset(self, asset_id: str) -> None:
        """Delete an asset by its ID."""
        pass

    @abstractmethod
    async def get_all_assets(self, filters: AssetFilter | None = None, sort: AssetSort | None = None) -> list[Asset]:
        """Retrieve all assets matching the query parameters."""
        pass

    @abstractmethod
    async def add_transaction(self, transaction: AssetTransaction) -> AssetTransaction:
        """Add a transaction to an asset."""
        pass

    @abstractmethod
    async def get_transactions_for_asset(self, asset_id: str) -> list[AssetTransaction]:
        """Retrieve all transactions logged for an asset, ordered by transaction date descending."""
        pass

    @abstractmethod
    async def get_transaction_by_id(self, transaction_id: str) -> AssetTransaction | None:
        """Retrieve a transaction by its ID."""
        pass

    @abstractmethod
    async def delete_transaction(self, transaction_id: str) -> None:
        """Delete a transaction by its ID."""
        pass
