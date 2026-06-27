"""Unit tests for asset schema validation."""

import pytest
from pydantic import ValidationError

from app.entities.models.asset import AssetTransactionType
from app.routers.v1.schemas.asset import AssetTransactionRequest


def test_asset_transaction_request_revalue_units_optional():
    """Verify that AssetTransactionRequest allows REVALUE with price_per_unit and no units."""
    data = {
        "transaction_type": "REVALUE",
        "amount": 110000.0,
        "unit_details": {
            "price_per_unit": 1100.0
        }
    }
    req = AssetTransactionRequest.model_validate(data)
    assert req.transaction_type == AssetTransactionType.REVALUE
    assert req.unit_details.price_per_unit == 1100.0
    assert req.unit_details.units is None


def test_asset_transaction_request_buy_units_required():
    """Verify that AssetTransactionRequest rejects BUY with unit_details missing units."""
    data = {
        "transaction_type": "BUY",
        "amount": 110000.0,
        "unit_details": {
            "price_per_unit": 1100.0
        }
    }
    with pytest.raises(ValidationError) as exc_info:
        AssetTransactionRequest.model_validate(data)
    assert "units must be specified for BUY or SELL transactions" in str(exc_info.value)


def test_asset_transaction_request_sell_units_required():
    """Verify that AssetTransactionRequest rejects SELL with unit_details missing units."""
    data = {
        "transaction_type": "SELL",
        "amount": 110000.0,
        "unit_details": {
            "price_per_unit": 1100.0
        }
    }
    with pytest.raises(ValidationError) as exc_info:
        AssetTransactionRequest.model_validate(data)
    assert "units must be specified for BUY or SELL transactions" in str(exc_info.value)


def test_asset_transaction_request_valid_value_based():
    """Verify that AssetTransactionRequest accepts flat balance transactions without unit details."""
    data = {
        "transaction_type": "REVALUE",
        "amount": 55000.0
    }
    req = AssetTransactionRequest.model_validate(data)
    assert req.transaction_type == AssetTransactionType.REVALUE
    assert req.unit_details is None
