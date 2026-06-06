"""Price resolver service for live tracking mock feeds."""


class PriceResolverService:
    """Mock live price resolver service.

    Provides current market prices in INR for assets (metals, tickers).
    """

    @staticmethod
    def resolve_price(symbol: str) -> float | None:
        """Resolve current unit price for a given ticker symbol or key."""
        clean_symbol = symbol.upper().strip()

        # Hardcoded realistic gold/silver prices from PRD snapshots
        pricing_database = {
            "GOLD_24K": 15863.18,  # Gold 24K price per gram
            "GOLD_22K": 14541.25,  # Gold 22K price per gram
            "SILVER": 95.50,  # Silver price per gram
            "RELIANCE": 2450.0,  # Mock Stock
            "TCS": 3850.0,  # Mock Stock
            "NIFTY50": 22500.0,  # Mock Index
        }

        return pricing_database.get(clean_symbol)
