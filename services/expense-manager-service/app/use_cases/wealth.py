"""Use cases for portfolio, net worth, and allocation analytics."""

import calendar
from datetime import UTC, datetime

from app.entities.repositories.asset import AssetRepositoryInterface
from app.entities.repositories.liability import LiabilityRepositoryInterface
from app.use_cases.liability import _simulate_amortization, add_months, calculate_current_outstanding
from app.use_cases.models.wealth import (
    HistoricalNetWorthPoint,
    WealthAllocation,
    WealthCategoryAllocation,
    WealthSummary,
)
from app.use_cases.price_resolver import PriceResolverService

# Threshold Constants for Leverage and Liquidity Ratios
DEBT_TO_ASSET_HEALTHY_THRESHOLD = 30.0
DEBT_TO_ASSET_WATCH_THRESHOLD = 50.0
LIQUIDITY_RATIO_HEALTHY_THRESHOLD = 15.0


class WealthService:
    """Service handling portfolio aggregation, net worth tracking, and allocation calculations."""

    def __init__(
        self,
        asset_repository: AssetRepositoryInterface,
        liability_repository: LiabilityRepositoryInterface,
    ):
        """Initialize the WealthService with repositories."""
        self.asset_repository = asset_repository
        self.liability_repository = liability_repository

    async def get_wealth_summary(self) -> WealthSummary:
        """Calculate high-level current wealth aggregation (assets, liabilities, and net worth)."""
        assets = await self.asset_repository.get_all_assets()
        liabilities = await self.liability_repository.get_all_liabilities()

        total_assets = sum(a.current_value for a in assets)
        total_invested_assets = sum(a.invested_value for a in assets)
        total_returns_assets = total_assets - total_invested_assets
        percentage_returns_assets = (
            (total_returns_assets / total_invested_assets) * 100 if total_invested_assets > 0 else 0.0
        )

        total_liabilities = 0.0
        total_original_liabilities = sum(liab.original_value for liab in liabilities)
        total_repaid_liabilities = 0.0
        accumulated_interest_liabilities = 0.0

        for liab in liabilities:
            txs = await self.liability_repository.get_transactions_for_liability(liab.id)
            calcs = calculate_current_outstanding(
                original_value=liab.original_value,
                interest_rate=liab.interest_rate,
                emi_amount=liab.emi_amount,
                transactions=txs,
                today=datetime.now(UTC),
                emi_start_date=liab.emi_start_date,
                interest_compounding=liab.interest_compounding,
            )
            total_liabilities += calcs["current_value"]
            total_repaid_liabilities += calcs["total_repaid"]
            accumulated_interest_liabilities += calcs["accumulated_interest"]

        net_worth = total_assets - total_liabilities

        return WealthSummary(
            total_assets=round(total_assets, 2),
            total_invested_assets=round(total_invested_assets, 2),
            total_returns_assets=round(total_returns_assets, 2),
            percentage_returns_assets=round(percentage_returns_assets, 2),
            total_liabilities=round(total_liabilities, 2),
            total_original_liabilities=round(total_original_liabilities, 2),
            total_repaid_liabilities=round(total_repaid_liabilities, 2),
            accumulated_interest_liabilities=round(accumulated_interest_liabilities, 2),
            net_worth=round(net_worth, 2),
        )

    async def get_historical_net_worth(self, months: int = 12) -> list[HistoricalNetWorthPoint]:
        """Calculate historical net worth over the last N months."""
        today = datetime.now(UTC)
        months_list = []
        for i in range(months - 1, -1, -1):
            date_m = add_months(today, -i)
            months_list.append(date_m.strftime("%Y-%m"))

        # Pre-fetch assets and liabilities with their respective transactions
        assets = await self.asset_repository.get_all_assets()
        asset_txs = {}
        for a in assets:
            asset_txs[a.id] = await self.asset_repository.get_transactions_for_asset(a.id)

        liabilities = await self.liability_repository.get_all_liabilities()
        liability_txs = {}
        for liab in liabilities:
            liability_txs[liab.id] = await self.liability_repository.get_transactions_for_liability(liab.id)

        points = []
        for m_str in months_list:
            year, month = map(int, m_str.split("-"))
            last_day = calendar.monthrange(year, month)[1]
            end_of_month = datetime(year, month, last_day, 23, 59, 59, 999999, tzinfo=UTC)

            # Accumulate historical asset values
            total_assets = 0.0
            for a in assets:
                val = await self._calculate_asset_value_at(a, asset_txs[a.id], end_of_month)
                total_assets += val

            # Accumulate historical liability values
            total_liabilities = 0.0
            for liab in liabilities:
                val = await self._calculate_liability_value_at(liab, liability_txs[liab.id], end_of_month)
                total_liabilities += val

            points.append(
                HistoricalNetWorthPoint(
                    date=m_str,
                    total_assets=round(total_assets, 2),
                    total_liabilities=round(total_liabilities, 2),
                    net_worth=round(total_assets - total_liabilities, 2),
                )
            )

        return points

    async def get_portfolio_allocation(self) -> WealthAllocation:
        """Calculate the asset and liability category allocation breakdowns."""
        # 1. Assets allocation
        assets = await self.asset_repository.get_all_assets()
        asset_categories = await self.asset_repository.get_all_categories()
        total_assets = sum(a.current_value for a in assets)

        asset_allocations = []
        for cat in asset_categories:
            cat_assets = [a for a in assets if a.category_id == cat.id]
            cat_value = sum(a.current_value for a in cat_assets)
            pct = (cat_value / total_assets) * 100 if total_assets > 0 else 0.0
            asset_allocations.append(
                WealthCategoryAllocation(
                    category_name=cat.name,
                    category_code=cat.code,
                    total_value=round(cat_value, 2),
                    percentage=round(pct, 2),
                )
            )

        # 2. Liabilities allocation
        liabilities = await self.liability_repository.get_all_liabilities()
        liability_categories = await self.liability_repository.get_all_categories()

        # Compute dynamic current values for all liabilities
        liab_current_values = {}
        total_liabilities = 0.0
        for liab in liabilities:
            txs = await self.liability_repository.get_transactions_for_liability(liab.id)
            calcs = calculate_current_outstanding(
                original_value=liab.original_value,
                interest_rate=liab.interest_rate,
                emi_amount=liab.emi_amount,
                transactions=txs,
                today=datetime.now(UTC),
                emi_start_date=liab.emi_start_date,
                interest_compounding=liab.interest_compounding,
            )
            val = calcs["current_value"]
            liab_current_values[liab.id] = val
            total_liabilities += val

        liability_allocations = []
        for cat in liability_categories:
            cat_liabs = [liab for liab in liabilities if liab.category_id == cat.id]
            cat_value = sum(liab_current_values[liab.id] for liab in cat_liabs)
            pct = (cat_value / total_liabilities) * 100 if total_liabilities > 0 else 0.0
            liability_allocations.append(
                WealthCategoryAllocation(
                    category_name=cat.name,
                    category_code=cat.code,
                    total_value=round(cat_value, 2),
                    percentage=round(pct, 2),
                )
            )

        total_assets_value = round(total_assets, 2)
        total_liabilities_value = round(total_liabilities, 2)

        # 3. Debt-to-Asset Ratio
        debt_to_asset_ratio = (total_liabilities / total_assets * 100) if total_assets > 0 else 0.0
        debt_to_asset_ratio = round(debt_to_asset_ratio, 2)

        # 4. Liquidity Ratio (Cash & Bank + Equity categories)
        liquid_categories = {"EQUITY", "CASH_BANK"}
        liquid_assets = sum(a.total_value for a in asset_allocations if a.category_code in liquid_categories)
        liquidity_ratio = (liquid_assets / total_assets * 100) if total_assets > 0 else 0.0
        liquidity_ratio = round(liquidity_ratio, 2)

        # 5. Financing Leverage percentages
        liabilities_financed_pct = min(100.0, debt_to_asset_ratio)
        equity_financed_pct = round(100.0 - liabilities_financed_pct, 2)
        liabilities_financed_pct = round(liabilities_financed_pct, 2)

        # 6. Status Labels and Types
        if debt_to_asset_ratio < DEBT_TO_ASSET_HEALTHY_THRESHOLD:
            leverage_status_label = "Low Risk (Healthy)"
            leverage_status_type = "SUCCESS"
        elif debt_to_asset_ratio <= DEBT_TO_ASSET_WATCH_THRESHOLD:
            leverage_status_label = "Moderate Risk (Watch)"
            leverage_status_type = "WARNING"
        else:
            leverage_status_label = "High Risk (Leveraged)"
            leverage_status_type = "ERROR"

        if liquidity_ratio >= LIQUIDITY_RATIO_HEALTHY_THRESHOLD:
            liquidity_status_label = "Healthy Liquidity"
            liquidity_status_type = "SUCCESS"
        else:
            liquidity_status_label = "Low Liquidity"
            liquidity_status_type = "WARNING"

        return WealthAllocation(
            assets=asset_allocations,
            liabilities=liability_allocations,
            total_assets_value=total_assets_value,
            total_liabilities_value=total_liabilities_value,
            debt_to_asset_ratio=debt_to_asset_ratio,
            liquidity_ratio=liquidity_ratio,
            equity_financed_pct=equity_financed_pct,
            liabilities_financed_pct=liabilities_financed_pct,
            leverage_status_label=leverage_status_label,
            leverage_status_type=leverage_status_type,
            liquidity_status_label=liquidity_status_label,
            liquidity_status_type=liquidity_status_type,
        )

    def _calculate_value_based_asset_value(self, txs_chrono: list) -> float:
        """Calculate the value of a value-based asset chronologically."""
        buys = sum(t.amount for t in txs_chrono if t.transaction_type == "BUY")
        sells = sum(t.amount for t in txs_chrono if t.transaction_type == "SELL")
        invested_value = max(0.0, buys - sells)

        revalues = [t for t in txs_chrono if t.transaction_type == "REVALUE"]
        if revalues:
            latest_revalue = revalues[-1]
            reval_index = txs_chrono.index(latest_revalue)
            current_val = latest_revalue.amount
            for t in txs_chrono[reval_index + 1 :]:
                if t.transaction_type == "BUY":
                    current_val += t.amount
                elif t.transaction_type == "SELL":
                    current_val = max(0.0, current_val - t.amount)
            return round(current_val, 2)
        return round(invested_value, 2)

    async def _calculate_unit_based_asset_value(self, asset, txs_chrono: list, as_of: datetime) -> float:
        """Calculate the value of a unit-based asset chronologically."""
        total_units = 0.0
        for t in txs_chrono:
            t_units = t.units or 0.0
            if t.transaction_type == "BUY":
                total_units += t_units
            elif t.transaction_type == "SELL":
                total_units = max(0.0, total_units - t_units)

        today_str = datetime.now(UTC).strftime("%Y-%m")
        as_of_str = as_of.strftime("%Y-%m")
        ppu = None

        if as_of_str == today_str:
            ticker_symbol = asset.name
            if asset.subcategory_id:
                sub = await self.asset_repository.get_subcategory_by_id(asset.subcategory_id)
                if sub:
                    ticker_symbol = sub.code
            ppu = PriceResolverService.resolve_price(ticker_symbol)

        if ppu is None:
            latest_ppu_txs = [
                t
                for t in txs_chrono
                if t.price_per_unit is not None and t.transaction_type in ("BUY", "REVALUE")
            ]
            ppu = latest_ppu_txs[-1].price_per_unit if latest_ppu_txs else 0.0

        return round(total_units * ppu, 2)

    async def _calculate_asset_value_at(self, asset, transactions: list, as_of: datetime) -> float:
        """Calculate the value of an asset as of a specific date."""
        txs = [t for t in transactions if t.transaction_date <= as_of]
        if not txs:
            return 0.0

        txs_chrono = sorted(txs, key=lambda t: (t.transaction_date, t.id))
        is_unit_based = any(t.units is not None for t in txs if t.transaction_type in ("BUY", "SELL"))

        if not is_unit_based:
            return self._calculate_value_based_asset_value(txs_chrono)
        else:
            return await self._calculate_unit_based_asset_value(asset, txs_chrono, as_of)

    def _calculate_interest_bearing_liability_value(self, liability, txs: list, as_of: datetime) -> float:
        """Calculate outstanding balance of an interest-bearing liability."""
        sorted_txs = sorted(txs, key=lambda t: (t.transaction_date, t.created_at or datetime.min))
        borrow_txs = [t for t in sorted_txs if t.transaction_type == "BORROW"]
        if not borrow_txs:
            return 0.0

        total_borrowed = sum(t.amount for t in borrow_txs)
        snapshots = _simulate_amortization(
            original_value=total_borrowed,
            interest_rate=liability.interest_rate,
            emi_amount=liability.emi_amount,
            transactions=txs,
            up_to_date=as_of,
            emi_start_date=liability.emi_start_date,
            compounding=liability.interest_compounding,
        )
        if not snapshots:
            return 0.0
        last_key = sorted(snapshots.keys())[-1]
        balance, _, _ = snapshots[last_key]
        return round(balance, 2)

    def _calculate_interest_free_liability_value(self, txs: list) -> float:
        """Calculate outstanding balance of an interest-free liability."""
        sorted_txs = sorted(txs, key=lambda t: (t.transaction_date, t.id))
        borrow_txs = [t for t in sorted_txs if t.transaction_type == "BORROW"]
        if not borrow_txs:
            return 0.0

        total_borrowed = sum(t.amount for t in borrow_txs)
        repayments = sum(t.amount for t in sorted_txs if t.transaction_type == "REPAY")
        revalue_txs = [t for t in sorted_txs if t.transaction_type == "REVALUE"]
        if revalue_txs:
            latest_revalue = revalue_txs[-1]
            revalue_index = sorted_txs.index(latest_revalue)
            current_val = latest_revalue.amount
            for t in sorted_txs[revalue_index + 1 :]:
                if t.transaction_type == "BORROW":
                    current_val += t.amount
                elif t.transaction_type == "REPAY":
                    current_val -= t.amount
            return round(max(0.0, current_val), 2)
        return round(max(0.0, total_borrowed - repayments), 2)

    async def _calculate_liability_value_at(self, liability, transactions: list, as_of: datetime) -> float:
        """Calculate the outstanding balance of a liability as of a specific date."""
        if not transactions:
            return 0.0

        txs = [t for t in transactions if t.transaction_date <= as_of]
        if not txs:
            return 0.0

        if liability.interest_rate and liability.interest_rate > 0:
            return self._calculate_interest_bearing_liability_value(liability, txs, as_of)
        else:
            return self._calculate_interest_free_liability_value(txs)
