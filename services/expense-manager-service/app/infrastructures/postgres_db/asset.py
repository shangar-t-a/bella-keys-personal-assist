"""Postgres repository implementation for assets."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.models.asset import (
    Asset,
    AssetCategory,
    AssetFilter,
    AssetSort,
    AssetSortField,
    AssetSubcategory,
    AssetTransaction,
)
from app.entities.models.sort import SortOrder
from app.entities.repositories.asset import AssetRepositoryInterface
from app.infrastructures.postgres_db.database import get_async_session
from app.infrastructures.postgres_db.models.asset import AssetModel
from app.infrastructures.postgres_db.models.asset_category import AssetCategoryModel
from app.infrastructures.postgres_db.models.asset_subcategory import AssetSubcategoryModel
from app.infrastructures.postgres_db.models.asset_transaction import AssetTransactionModel


class PostgresAssetRepository(AssetRepositoryInterface):
    """Postgres implementation of the AssetRepositoryInterface."""

    def __init__(self):
        """Initialize the Postgres asset repository."""
        self.session_factory = get_async_session()

    async def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    def _to_subcategory_entity(self, model: AssetSubcategoryModel) -> AssetSubcategory:
        """Map DB model to Domain entity."""
        return AssetSubcategory(
            id=model.id,
            category_id=model.category_id,
            name=model.name,
            code=model.code,
            description=model.description,
            valuation_type=model.valuation_type,
            has_interest=model.has_interest,
            has_maturity=model.has_maturity,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_category_entity(self, model: AssetCategoryModel, subcategories: list[AssetSubcategory] | None = None) -> AssetCategory:
        """Map DB model to Domain entity."""
        return AssetCategory(
            id=model.id,
            name=model.name,
            code=model.code,
            description=model.description,
            subcategories=subcategories or [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_asset_entity(self, model: AssetModel) -> Asset:
        """Map DB model to Domain entity."""
        return Asset(
            id=model.id,
            category_id=model.category_id,
            name=model.name,
            sub_category=model.sub_category,
            subcategory_id=model.subcategory_id,
            invested_value=model.invested_value,
            current_value=model.current_value,
            interest_rate=model.interest_rate,
            interest_compounding=model.interest_compounding,
            maturity_date=model.maturity_date,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_transaction_entity(self, model: AssetTransactionModel) -> AssetTransaction:
        """Map DB model to Domain entity."""
        return AssetTransaction(
            id=model.id,
            asset_id=model.asset_id,
            transaction_type=model.transaction_type,
            amount=model.amount,
            units=model.units,
            price_per_unit=model.price_per_unit,
            transaction_date=model.transaction_date,
            description=model.description,
            created_at=model.created_at,
        )

    async def get_all_categories(self) -> list[AssetCategory]:
        """Retrieve all asset categories."""
        async with await self._get_session() as session:
            cat_stmt = select(AssetCategoryModel).order_by(AssetCategoryModel.name.asc())
            cat_result = await session.execute(cat_stmt)
            cat_models = cat_result.scalars().all()

            sub_stmt = select(AssetSubcategoryModel).order_by(AssetSubcategoryModel.name.asc())
            sub_result = await session.execute(sub_stmt)
            sub_models = sub_result.scalars().all()

            sub_map = {}
            for s in sub_models:
                entity = self._to_subcategory_entity(s)
                sub_map.setdefault(s.category_id, []).append(entity)

            return [self._to_category_entity(m, sub_map.get(m.id, [])) for m in cat_models]

    async def get_category_by_id(self, category_id: str) -> AssetCategory | None:
        """Retrieve an asset category by its ID."""
        async with await self._get_session() as session:
            stmt = select(AssetCategoryModel).where(AssetCategoryModel.id == category_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return None

            sub_stmt = select(AssetSubcategoryModel).where(AssetSubcategoryModel.category_id == category_id).order_by(AssetSubcategoryModel.name.asc())
            sub_result = await session.execute(sub_stmt)
            sub_models = sub_result.scalars().all()
            subcategories = [self._to_subcategory_entity(s) for s in sub_models]

            return self._to_category_entity(model, subcategories)

    async def get_category_by_code(self, category_code: str) -> AssetCategory | None:
        """Retrieve an asset category by its code."""
        async with await self._get_session() as session:
            stmt = select(AssetCategoryModel).where(AssetCategoryModel.code == category_code.upper())
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return None

            sub_stmt = select(AssetSubcategoryModel).where(AssetSubcategoryModel.category_id == model.id).order_by(AssetSubcategoryModel.name.asc())
            sub_result = await session.execute(sub_stmt)
            sub_models = sub_result.scalars().all()
            subcategories = [self._to_subcategory_entity(s) for s in sub_models]

            return self._to_category_entity(model, subcategories)

    async def add_asset(self, asset: Asset) -> Asset:
        """Add a new asset."""
        async with await self._get_session() as session:
            model = AssetModel(
                id=asset.id,
                category_id=asset.category_id,
                name=asset.name,
                sub_category=asset.sub_category,
                subcategory_id=asset.subcategory_id,
                invested_value=asset.invested_value,
                current_value=asset.current_value,
                interest_rate=asset.interest_rate,
                interest_compounding=asset.interest_compounding,
                maturity_date=asset.maturity_date,
                notes=asset.notes,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_asset_entity(model)

    async def get_asset_by_id(self, asset_id: str) -> Asset | None:
        """Retrieve an asset by its ID."""
        async with await self._get_session() as session:
            stmt = select(AssetModel).where(AssetModel.id == asset_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_asset_entity(model) if model else None

    async def get_asset_by_name(self, name: str) -> Asset | None:
        """Retrieve an asset by its name."""
        async with await self._get_session() as session:
            stmt = select(AssetModel).where(AssetModel.name == name)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_asset_entity(model) if model else None

    async def edit_asset(self, asset_id: str, asset: Asset) -> Asset:
        """Edit an existing asset details."""
        async with await self._get_session() as session:
            stmt = select(AssetModel).where(AssetModel.id == asset_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Asset with ID {asset_id} not found.")

            model.name = asset.name
            model.category_id = asset.category_id
            model.sub_category = asset.sub_category
            model.subcategory_id = asset.subcategory_id
            model.invested_value = asset.invested_value
            model.current_value = asset.current_value
            model.interest_rate = asset.interest_rate
            model.interest_compounding = asset.interest_compounding
            model.maturity_date = asset.maturity_date
            model.notes = asset.notes

            await session.commit()
            await session.refresh(model)
            return self._to_asset_entity(model)

    async def delete_asset(self, asset_id: str) -> None:
        """Delete an asset by its ID."""
        async with await self._get_session() as session:
            stmt = select(AssetModel).where(AssetModel.id == asset_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Asset with ID {asset_id} not found.")

            await session.delete(model)
            await session.commit()

    async def get_all_assets(self, filters: AssetFilter | None = None, sort: AssetSort | None = None) -> list[Asset]:
        """Retrieve all assets matching the query parameters."""
        async with await self._get_session() as session:
            stmt = select(AssetModel)

            # Apply filters
            if filters:
                if filters.category_id:
                    stmt = stmt.where(AssetModel.category_id == filters.category_id)
                if filters.search:
                    stmt = stmt.where(AssetModel.name.ilike(f"%{filters.search}%"))

            # Apply sorting
            if sort:
                column_map = {
                    AssetSortField.NAME: AssetModel.name,
                    AssetSortField.INVESTED_VALUE: AssetModel.invested_value,
                    AssetSortField.CURRENT_VALUE: AssetModel.current_value,
                    AssetSortField.CREATED_AT: AssetModel.created_at,
                }
                sort_col = column_map.get(sort.sort_by, AssetModel.name)
                if sort.sort_order == SortOrder.DESC:
                    stmt = stmt.order_by(sort_col.desc(), AssetModel.id.desc())
                else:
                    stmt = stmt.order_by(sort_col.asc(), AssetModel.id.asc())
            else:
                stmt = stmt.order_by(AssetModel.name.asc())

            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._to_asset_entity(m) for m in models]

    async def add_transaction(self, transaction: AssetTransaction) -> AssetTransaction:
        """Add a transaction to an asset."""
        async with await self._get_session() as session:
            model = AssetTransactionModel(
                id=transaction.id,
                asset_id=transaction.asset_id,
                transaction_type=transaction.transaction_type,
                amount=transaction.amount,
                units=transaction.units,
                price_per_unit=transaction.price_per_unit,
                transaction_date=transaction.transaction_date,
                description=transaction.description,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_transaction_entity(model)

    async def get_transactions_for_asset(self, asset_id: str) -> list[AssetTransaction]:
        """Retrieve all transactions logged for an asset, ordered by transaction date descending."""
        async with await self._get_session() as session:
            stmt = (
                select(AssetTransactionModel)
                .where(AssetTransactionModel.asset_id == asset_id)
                .order_by(AssetTransactionModel.transaction_date.desc(), AssetTransactionModel.created_at.desc())
            )
            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._to_transaction_entity(m) for m in models]

    async def get_transaction_by_id(self, transaction_id: str) -> AssetTransaction | None:
        """Retrieve a transaction by its ID."""
        async with await self._get_session() as session:
            stmt = select(AssetTransactionModel).where(AssetTransactionModel.id == transaction_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_transaction_entity(model) if model else None

    async def delete_transaction(self, transaction_id: str) -> None:
        """Delete a transaction by its ID."""
        async with await self._get_session() as session:
            stmt = select(AssetTransactionModel).where(AssetTransactionModel.id == transaction_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Transaction with ID {transaction_id} not found.")

            await session.delete(model)
            await session.commit()
