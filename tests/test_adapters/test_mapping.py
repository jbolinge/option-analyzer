"""Tests for TastyTrade mapping layer — SDK types to domain models."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from options_analyzer.adapters.tastytrade.mapping import (
    map_greeks_to_first_order,
    map_option_to_contract,
    map_position_to_leg,
)
from options_analyzer.domain.enums import ExerciseStyle, OptionType, PositionSide


def _make_sdk_option(**overrides: object) -> MagicMock:
    """Create a mock tastytrade Option with realistic defaults."""
    defaults = {
        "symbol": "AAPL  260220C00150000",
        "underlying_symbol": "AAPL",
        "option_type": MagicMock(value="C"),
        "strike_price": Decimal("150.00"),
        "expiration_date": date(2026, 2, 20),
        "exercise_style": "American",
        "shares_per_contract": 100,
        "streamer_symbol": ".AAPL260220C150",
    }
    defaults.update(overrides)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


def _make_sdk_position(**overrides: object) -> MagicMock:
    """Create a mock tastytrade CurrentPosition with realistic defaults."""
    defaults = {
        "symbol": "AAPL  260220C00150000",
        "underlying_symbol": "AAPL",
        "quantity": Decimal("2"),
        "quantity_direction": "Long",
        "average_open_price": Decimal("5.25"),
        "multiplier": 100,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


def _make_sdk_greeks(**overrides: object) -> MagicMock:
    """Create a mock tastytrade Greeks event with realistic defaults."""
    defaults = {
        "event_symbol": ".AAPL260220C150",
        "delta": Decimal("0.5123"),
        "gamma": Decimal("0.0456"),
        "theta": Decimal("-0.0512"),
        "vega": Decimal("0.2345"),
        "rho": Decimal("0.0123"),
        "volatility": Decimal("0.2500"),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


class TestMapOptionToContract:
    def test_maps_call_option(self) -> None:
        sdk_option = _make_sdk_option()
        contract = map_option_to_contract(sdk_option)
        assert contract.symbol == "AAPL  260220C00150000"
        assert contract.underlying == "AAPL"
        assert contract.option_type == OptionType.CALL
        assert contract.strike == Decimal("150.00")
        assert contract.expiration == date(2026, 2, 20)
        assert contract.exercise_style == ExerciseStyle.AMERICAN
        assert contract.multiplier == 100

    def test_maps_put_option(self) -> None:
        sdk_option = _make_sdk_option(
            symbol="AAPL  260220P00150000",
            option_type=MagicMock(value="P"),
            streamer_symbol=".AAPL260220P150",
        )
        contract = map_option_to_contract(sdk_option)
        assert contract.option_type == OptionType.PUT

    def test_maps_european_exercise_style(self) -> None:
        sdk_option = _make_sdk_option(exercise_style="European")
        contract = map_option_to_contract(sdk_option)
        assert contract.exercise_style == ExerciseStyle.EUROPEAN

    def test_maps_different_multiplier(self) -> None:
        sdk_option = _make_sdk_option(shares_per_contract=10)
        contract = map_option_to_contract(sdk_option)
        assert contract.multiplier == 10


class TestMapPositionToLeg:
    def test_maps_long_position(self) -> None:
        sdk_option = _make_sdk_option()
        sdk_position = _make_sdk_position(quantity_direction="Long")
        leg = map_position_to_leg(sdk_position, sdk_option)
        assert leg.side == PositionSide.LONG
        assert leg.quantity == 2
        assert leg.open_price == Decimal("5.25")
        assert leg.contract.symbol == "AAPL  260220C00150000"

    def test_maps_short_position(self) -> None:
        sdk_option = _make_sdk_option()
        sdk_position = _make_sdk_position(
            quantity_direction="Short", quantity=Decimal("3")
        )
        leg = map_position_to_leg(sdk_position, sdk_option)
        assert leg.side == PositionSide.SHORT
        assert leg.quantity == 3

    def test_quantity_is_always_positive(self) -> None:
        sdk_option = _make_sdk_option()
        sdk_position = _make_sdk_position(quantity=Decimal("-5"))
        leg = map_position_to_leg(sdk_position, sdk_option)
        assert leg.quantity == 5


class TestMapGreeksToFirstOrder:
    def test_maps_all_fields(self) -> None:
        sdk_greeks = _make_sdk_greeks()
        greeks = map_greeks_to_first_order(sdk_greeks)
        assert greeks.delta == pytest.approx(0.5123)
        assert greeks.gamma == pytest.approx(0.0456)
        assert greeks.theta == pytest.approx(-0.0512)
        assert greeks.vega == pytest.approx(0.2345)
        assert greeks.rho == pytest.approx(0.0123)
        assert greeks.iv == pytest.approx(0.2500)

    def test_converts_decimal_to_float(self) -> None:
        sdk_greeks = _make_sdk_greeks()
        greeks = map_greeks_to_first_order(sdk_greeks)
        assert isinstance(greeks.delta, float)
        assert isinstance(greeks.iv, float)

    def test_handles_zero_values(self) -> None:
        sdk_greeks = _make_sdk_greeks(
            delta=Decimal("0"),
            gamma=Decimal("0"),
            theta=Decimal("0"),
            vega=Decimal("0"),
            rho=Decimal("0"),
            volatility=Decimal("0"),
        )
        greeks = map_greeks_to_first_order(sdk_greeks)
        assert greeks.delta == 0.0
        assert greeks.iv == 0.0
