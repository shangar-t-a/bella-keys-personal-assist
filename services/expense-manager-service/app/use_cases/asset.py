"""Use cases for Assets."""

import uuid

from app.entities.models.asset import (
    Asset,
    AssetCategory,
    AssetFilter,
    AssetSort,
    AssetTransaction,
    AssetTransactionType,
)
from app.entities.repositories.asset import AssetRepositoryInterface
from app.use_cases.models.asset import (
    AssetCategorySummary,
    AssetCreate,
    AssetSummary,
    AssetTransactionCreate,
    AssetUpdate,
    AssetWithCalc,
)
from app.use_cases.price_resolver import PriceResolverService


class AssetService:
    """Service handling asset orchestration and financial calculations."""

    def __init__(self, asset_repository: AssetRepositoryInterface):
        """Initialize the AssetService with repository."""
        self.asset_repository = asset_repository

    async def get_all_categories(self) -> list[AssetCategory]:
        """Retrieve all asset categories."""
        return await self.asset_repository.get_all_categories()

    async def _to_calc_model(self, asset: Asset) -> AssetWithCalc:
        """Add calculated fields and category name to asset model."""
        category = await self.asset_repository.get_category_by_id(asset.category_id)
        category_name = category.name if category else "Unknown"
        category_code = category.code if category else "UNKNOWN"

        absolute_returns = asset.current_value - asset.invested_value
        percentage_returns = 0.0
        if asset.invested_value > 0:
            percentage_returns = (absolute_returns / asset.invested_value) * 100

        return AssetWithCalc(
            id=asset.id,
            category_id=asset.category_id,
            category_name=category_name,
            category_code=category_code,
            name=asset.name,
            sub_category=asset.sub_category,
            subcategory_id=asset.subcategory_id,
            invested_value=asset.invested_value,
            current_value=asset.current_value,
            interest_rate=asset.interest_rate,
            interest_compounding=asset.interest_compounding,
            maturity_date=asset.maturity_date,
            notes=asset.notes,
            absolute_returns=round(absolute_returns, 2),
            percentage_returns=round(percentage_returns, 2),
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )

    async def create_asset(self, asset_create: AssetCreate) -> AssetWithCalc:
        """Create a new asset and log its initial transaction."""
        asset_id = uuid.uuid4().hex

        # Create the asset model
        asset = Asset(
            id=asset_id,
            category_id=asset_create.category_id,
            name=asset_create.name,
            sub_category=asset_create.sub_category,
            subcategory_id=asset_create.subcategory_id,
            invested_value=0.0,
            current_value=0.0,
            interest_rate=asset_create.interest_rate,
            interest_compounding=asset_create.interest_compounding,
            maturity_date=asset_create.maturity_date,
            notes=asset_create.notes,
        )
        created_asset = await self.asset_repository.add_asset(asset)

        # Log the initial transaction
        tx = AssetTransaction(
            id=uuid.uuid4().hex,
            asset_id=asset_id,
            transaction_type=AssetTransactionType.BUY,
            amount=asset_create.initial_amount,
            units=asset_create.units,
            price_per_unit=asset_create.price_per_unit,
            description="Initial deposit/purchase",
        )
        await self.asset_repository.add_transaction(tx)

        # Recalculate cached values
        await self._recalculate_asset_values(asset_id)

        # Retrieve recalculated asset
        updated_asset = await self.asset_repository.get_asset_by_id(asset_id)
        if not updated_asset:
            return await self._to_calc_model(created_asset)
        return await self._to_calc_model(updated_asset)

    async def update_asset(self, asset_id: str, asset_update: AssetUpdate) -> AssetWithCalc:
        """Update asset details."""
        existing_asset = await self.asset_repository.get_asset_by_id(asset_id)
        if not existing_asset:
            raise ValueError(f"Asset with ID {asset_id} not found.")

        updated_asset = Asset(
            id=existing_asset.id,
            category_id=asset_update.category_id,
            name=asset_update.name,
            sub_category=asset_update.sub_category,
            subcategory_id=asset_update.subcategory_id,
            invested_value=existing_asset.invested_value,
            current_value=existing_asset.current_value,
            interest_rate=asset_update.interest_rate,
            interest_compounding=asset_update.interest_compounding,
            maturity_date=asset_update.maturity_date,
            notes=asset_update.notes,
            created_at=existing_asset.created_at,
        )
        saved_asset = await self.asset_repository.edit_asset(asset_id, updated_asset)
        await self._recalculate_asset_values(asset_id)
        final_asset = await self.asset_repository.get_asset_by_id(asset_id)
        return await self._to_calc_model(final_asset or saved_asset)

    async def delete_asset(self, asset_id: str) -> None:
        """Delete an asset."""
        await self.asset_repository.delete_asset(asset_id)

    async def get_asset_by_id(self, asset_id: str) -> AssetWithCalc:
        """Retrieve an asset by ID with returns mapping."""
        asset = await self.asset_repository.get_asset_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found.")
        return await self._to_calc_model(asset)

    async def list_assets(
        self, category_id: str | None = None, search: str | None = None
    ) -> list[AssetWithCalc]:
        """List assets matching criteria with return parameters."""
        filters = AssetFilter(category_id=category_id, search=search)
        sort = AssetSort(sort_by="name", sort_order="asc")
        assets = await self.asset_repository.get_all_assets(filters=filters, sort=sort)
        return [await self._to_calc_model(a) for a in assets]

    async def get_asset_summary(self) -> AssetSummary:
        """Calculate total summary and category breakdowns for all assets."""
        assets = await self.asset_repository.get_all_assets()
        categories = await self.asset_repository.get_all_categories()

        total_invested = sum(a.invested_value for a in assets)
        total_current = sum(a.current_value for a in assets)
        total_returns = total_current - total_invested
        total_pct = 0.0
        if total_invested > 0:
            total_pct = (total_returns / total_invested) * 100

        category_breakdowns = []
        for cat in categories:
            cat_assets = [a for a in assets if a.category_id == cat.id]
            cat_invested = sum(a.invested_value for a in cat_assets)
            cat_current = sum(a.current_value for a in cat_assets)
            cat_returns = cat_current - cat_invested
            cat_pct = 0.0
            if cat_invested > 0:
                cat_pct = (cat_returns / cat_invested) * 100

            category_breakdowns.append(
                AssetCategorySummary(
                    category_id=cat.id,
                    category_name=cat.name,
                    category_code=cat.code,
                    total_invested=round(cat_invested, 2),
                    total_current=round(cat_current, 2),
                    total_returns=round(cat_returns, 2),
                    percentage_returns=round(cat_pct, 2),
                )
            )

        return AssetSummary(
            total_invested=round(total_invested, 2),
            total_current=round(total_current, 2),
            total_returns=round(total_returns, 2),
            percentage_returns=round(total_pct, 2),
            category_breakdowns=category_breakdowns,
        )

    async def add_transaction(self, asset_id: str, tx_create: AssetTransactionCreate) -> AssetTransaction:
        """Log a new transaction and update the cached valuations on the asset."""
        asset = await self.asset_repository.get_asset_by_id(asset_id)
        if not asset:
            raise ValueError(f"Asset with ID {asset_id} not found.")

        tx = AssetTransaction(
            id=uuid.uuid4().hex,
            asset_id=asset_id,
            transaction_type=tx_create.transaction_type,
            amount=tx_create.amount,
            units=tx_create.units,
            price_per_unit=tx_create.price_per_unit,
            transaction_date=tx_create.transaction_date,
            description=tx_create.description,
        )
        created_tx = await self.asset_repository.add_transaction(tx)
        await self._recalculate_asset_values(asset_id)
        return created_tx

    async def get_transactions_for_asset(self, asset_id: str) -> list[AssetTransaction]:
        """Fetch transactions list for a single asset."""
        return await self.asset_repository.get_transactions_for_asset(asset_id)

    async def delete_transaction(self, transaction_id: str) -> None:
        """Remove a transaction and recalculate valuations on the parent asset."""
        tx = await self.asset_repository.get_transaction_by_id(transaction_id)
        if not tx:
            raise ValueError(f"Transaction with ID {transaction_id} not found.")

        await self.asset_repository.delete_transaction(transaction_id)
        await self._recalculate_asset_values(tx.asset_id)

    async def _recalculate_asset_values(self, asset_id: str) -> None:
        """Run calculations across all transactions to refresh invested and current values."""
        asset = await self.asset_repository.get_asset_by_id(asset_id)
        if not asset:
            return

        transactions = await self.asset_repository.get_transactions_for_asset(asset_id)
        if not transactions:
            # Reset
            updated = Asset(
                id=asset.id,
                category_id=asset.category_id,
                name=asset.name,
                sub_category=asset.sub_category,
                invested_value=0.0,
                current_value=0.0,
                notes=asset.notes,
                created_at=asset.created_at,
            )
            await self.asset_repository.edit_asset(asset_id, updated)
            return

        # Determine if asset is unit-based (if any transaction contains unit values)
        is_unit_based = any(
            t.units is not None
            for t in transactions
            if t.transaction_type in (AssetTransactionType.BUY, AssetTransactionType.SELL)
        )

        invested_value = 0.0
        current_value = 0.0

        if not is_unit_based:
            # Flat balance tracking
            buys = sum(t.amount for t in transactions if t.transaction_type == AssetTransactionType.BUY)
            sells = sum(t.amount for t in transactions if t.transaction_type == AssetTransactionType.SELL)
            invested_value = max(0.0, buys - sells)

            # Look for the latest REVALUE transaction
            revalues = [t for t in transactions if t.transaction_type == AssetTransactionType.REVALUE]
            current_value = revalues[0].amount if revalues else invested_value
        else:
            # Unit-based tracking
            total_units = 0.0
            invested_cash = 0.0

            for t in transactions[::-1]:  # Iterate chronological (oldest first)
                t_units = t.units or 0.0
                t_ppu = t.price_per_unit or 0.0

                if t.transaction_type == AssetTransactionType.BUY:
                    total_units += t_units
                    invested_cash += t_units * t_ppu
                elif t.transaction_type == AssetTransactionType.SELL:
                    total_units = max(0.0, total_units - t_units)
                    invested_cash = max(0.0, invested_cash - t_units * t_ppu)

            invested_value = max(0.0, invested_cash)

            # Resolve price per unit (latest mock live price or latest transaction price)
            ticker_symbol = asset.sub_category or asset.name
            live_price = PriceResolverService.resolve_price(ticker_symbol)

            if live_price is not None:
                ppu = live_price
            else:
                # Find most recent price_per_unit in transactions (REVALUE or BUY)
                latest_ppu_txs = [
                    t
                    for t in transactions
                    if t.price_per_unit is not None
                    and t.transaction_type in (AssetTransactionType.BUY, AssetTransactionType.REVALUE)
                ]
                ppu = latest_ppu_txs[0].price_per_unit if latest_ppu_txs else 0.0

            current_value = total_units * ppu

        # Save recalculations
        updated = Asset(
            id=asset.id,
            category_id=asset.category_id,
            name=asset.name,
            sub_category=asset.sub_category,
            invested_value=round(invested_value, 2),
            current_value=round(current_value, 2),
            notes=asset.notes,
            created_at=asset.created_at,
        )
        await self.asset_repository.edit_asset(asset_id, updated)
