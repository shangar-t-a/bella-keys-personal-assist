"""Postgres repository implementation for liabilities."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.models.liability import (
    Liability,
    LiabilityCategory,
    LiabilityFilter,
    LiabilitySort,
    LiabilitySortField,
    LiabilitySubcategory,
    LiabilityTransaction,
)
from app.entities.models.sort import SortOrder
from app.entities.repositories.liability import LiabilityRepositoryInterface
from app.infrastructures.postgres_db.database import get_async_session
from app.infrastructures.postgres_db.models.liability import LiabilityModel
from app.infrastructures.postgres_db.models.liability_category import LiabilityCategoryModel
from app.infrastructures.postgres_db.models.liability_subcategory import LiabilitySubcategoryModel
from app.infrastructures.postgres_db.models.liability_transaction import LiabilityTransactionModel


class PostgresLiabilityRepository(LiabilityRepositoryInterface):
    """Postgres implementation of the LiabilityRepositoryInterface."""

    def __init__(self):
        """Initialize the Postgres liability repository."""
        self.session_factory = get_async_session()

    async def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    def _to_subcategory_entity(self, model: LiabilitySubcategoryModel) -> LiabilitySubcategory:
        """Map DB model to Domain entity."""
        return LiabilitySubcategory(
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

    def _to_category_entity(
        self, model: LiabilityCategoryModel, subcategories: list[LiabilitySubcategory] | None = None
    ) -> LiabilityCategory:
        """Map DB model to Domain entity."""
        return LiabilityCategory(
            id=model.id,
            name=model.name,
            code=model.code,
            description=model.description,
            subcategories=subcategories or [],
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_liability_entity(self, model: LiabilityModel) -> Liability:
        """Map DB model to Domain entity."""
        return Liability(
            id=model.id,
            category_id=model.category_id,
            name=model.name,
            subcategory_id=model.subcategory_id,
            original_value=model.original_value,
            current_value=model.current_value,
            interest_rate=model.interest_rate,
            interest_compounding=model.interest_compounding,
            emi_amount=model.emi_amount,
            emi_start_date=model.emi_start_date,
            maturity_date=model.maturity_date,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_transaction_entity(self, model: LiabilityTransactionModel) -> LiabilityTransaction:
        """Map DB model to Domain entity."""
        return LiabilityTransaction(
            id=model.id,
            liability_id=model.liability_id,
            transaction_type=model.transaction_type,
            amount=model.amount,
            transaction_date=model.transaction_date,
            description=model.description,
            created_at=model.created_at,
        )

    async def get_all_categories(self) -> list[LiabilityCategory]:
        """Retrieve all liability categories."""
        async with await self._get_session() as session:
            cat_stmt = select(LiabilityCategoryModel).order_by(LiabilityCategoryModel.name.asc())
            cat_result = await session.execute(cat_stmt)
            cat_models = cat_result.scalars().all()

            sub_stmt = select(LiabilitySubcategoryModel).order_by(LiabilitySubcategoryModel.name.asc())
            sub_result = await session.execute(sub_stmt)
            sub_models = sub_result.scalars().all()

            sub_map = {}
            for s in sub_models:
                entity = self._to_subcategory_entity(s)
                sub_map.setdefault(s.category_id, []).append(entity)

            return [self._to_category_entity(m, sub_map.get(m.id, [])) for m in cat_models]

    async def get_category_by_id(self, category_id: str) -> LiabilityCategory | None:
        """Retrieve a liability category by its ID."""
        async with await self._get_session() as session:
            stmt = select(LiabilityCategoryModel).where(LiabilityCategoryModel.id == category_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return None

            sub_stmt = (
                select(LiabilitySubcategoryModel)
                .where(LiabilitySubcategoryModel.category_id == category_id)
                .order_by(LiabilitySubcategoryModel.name.asc())
            )
            sub_result = await session.execute(sub_stmt)
            sub_models = sub_result.scalars().all()
            subcategories = [self._to_subcategory_entity(s) for s in sub_models]

            return self._to_category_entity(model, subcategories)

    async def get_category_by_code(self, category_code: str) -> LiabilityCategory | None:
        """Retrieve a liability category by its code."""
        async with await self._get_session() as session:
            stmt = select(LiabilityCategoryModel).where(LiabilityCategoryModel.code == category_code.upper())
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if not model:
                return None

            sub_stmt = (
                select(LiabilitySubcategoryModel)
                .where(LiabilitySubcategoryModel.category_id == model.id)
                .order_by(LiabilitySubcategoryModel.name.asc())
            )
            sub_result = await session.execute(sub_stmt)
            sub_models = sub_result.scalars().all()
            subcategories = [self._to_subcategory_entity(s) for s in sub_models]

            return self._to_category_entity(model, subcategories)

    async def get_subcategory_by_id(self, subcategory_id: str) -> LiabilitySubcategory | None:
        """Retrieve a liability subcategory by its ID."""
        async with await self._get_session() as session:
            stmt = select(LiabilitySubcategoryModel).where(LiabilitySubcategoryModel.id == subcategory_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_subcategory_entity(model) if model else None

    async def add_liability(self, liability: Liability) -> Liability:
        """Add a new liability."""
        async with await self._get_session() as session:
            model = LiabilityModel(
                id=liability.id,
                category_id=liability.category_id,
                name=liability.name,
                subcategory_id=liability.subcategory_id,
                original_value=liability.original_value,
                current_value=liability.current_value,
                interest_rate=liability.interest_rate,
                interest_compounding=liability.interest_compounding,
                emi_amount=liability.emi_amount,
                emi_start_date=liability.emi_start_date,
                maturity_date=liability.maturity_date,
                notes=liability.notes,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_liability_entity(model)

    async def get_liability_by_id(self, liability_id: str) -> Liability | None:
        """Retrieve a liability by its ID."""
        async with await self._get_session() as session:
            stmt = select(LiabilityModel).where(LiabilityModel.id == liability_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_liability_entity(model) if model else None

    async def edit_liability(self, liability_id: str, liability: Liability) -> Liability:
        """Edit an existing liability details."""
        async with await self._get_session() as session:
            stmt = select(LiabilityModel).where(LiabilityModel.id == liability_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Liability with ID {liability_id} not found.")

            model.name = liability.name
            model.category_id = liability.category_id
            model.subcategory_id = liability.subcategory_id
            model.original_value = liability.original_value
            model.current_value = liability.current_value
            model.interest_rate = liability.interest_rate
            model.interest_compounding = liability.interest_compounding
            model.emi_amount = liability.emi_amount
            model.emi_start_date = liability.emi_start_date
            model.maturity_date = liability.maturity_date
            model.notes = liability.notes

            await session.commit()
            await session.refresh(model)
            return self._to_liability_entity(model)

    async def delete_liability(self, liability_id: str) -> None:
        """Delete a liability by its ID."""
        async with await self._get_session() as session:
            stmt = select(LiabilityModel).where(LiabilityModel.id == liability_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Liability with ID {liability_id} not found.")

            await session.delete(model)
            await session.commit()

    async def get_all_liabilities(
        self, filters: LiabilityFilter | None = None, sort: LiabilitySort | None = None
    ) -> list[Liability]:
        """Retrieve all liabilities matching the query parameters."""
        async with await self._get_session() as session:
            stmt = select(LiabilityModel)

            # Apply filters
            if filters:
                if filters.category_id:
                    stmt = stmt.where(LiabilityModel.category_id == filters.category_id)
                if filters.search:
                    stmt = stmt.where(LiabilityModel.name.ilike(f"%{filters.search}%"))

            # Apply sorting
            if sort:
                column_map = {
                    LiabilitySortField.NAME: LiabilityModel.name,
                    LiabilitySortField.ORIGINAL_VALUE: LiabilityModel.original_value,
                    LiabilitySortField.CURRENT_VALUE: LiabilityModel.current_value,
                    LiabilitySortField.CREATED_AT: LiabilityModel.created_at,
                }
                sort_col = column_map.get(sort.sort_by, LiabilityModel.name)
                if sort.sort_order == SortOrder.DESC:
                    stmt = stmt.order_by(sort_col.desc(), LiabilityModel.id.desc())
                else:
                    stmt = stmt.order_by(sort_col.asc(), LiabilityModel.id.asc())
            else:
                stmt = stmt.order_by(LiabilityModel.name.asc())

            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._to_liability_entity(m) for m in models]

    async def add_transaction(self, transaction: LiabilityTransaction) -> LiabilityTransaction:
        """Add a transaction to a liability."""
        async with await self._get_session() as session:
            model = LiabilityTransactionModel(
                id=transaction.id,
                liability_id=transaction.liability_id,
                transaction_type=transaction.transaction_type,
                amount=transaction.amount,
                transaction_date=transaction.transaction_date,
                description=transaction.description,
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_transaction_entity(model)

    async def get_transactions_for_liability(self, liability_id: str) -> list[LiabilityTransaction]:
        """Retrieve all transactions logged for a liability, ordered by transaction date descending."""
        async with await self._get_session() as session:
            stmt = (
                select(LiabilityTransactionModel)
                .where(LiabilityTransactionModel.liability_id == liability_id)
                .order_by(
                    LiabilityTransactionModel.transaction_date.desc(), LiabilityTransactionModel.created_at.desc()
                )
            )
            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._to_transaction_entity(m) for m in models]

    async def get_transaction_by_id(self, transaction_id: str) -> LiabilityTransaction | None:
        """Retrieve a transaction by its ID."""
        async with await self._get_session() as session:
            stmt = select(LiabilityTransactionModel).where(LiabilityTransactionModel.id == transaction_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._to_transaction_entity(model) if model else None

    async def delete_transaction(self, transaction_id: str) -> None:
        """Delete a transaction by its ID."""
        async with await self._get_session() as session:
            stmt = select(LiabilityTransactionModel).where(LiabilityTransactionModel.id == transaction_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                raise ValueError(f"Transaction with ID {transaction_id} not found.")

            await session.delete(model)
            await session.commit()
