"""Reusable test object factory functions for all domain models."""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Any

from options_analyzer.domain.enums import ExerciseStyle, OptionType, PositionSide
from options_analyzer.domain.greeks import (
    FirstOrderGreeks,
    FullGreeks,
    SecondOrderGreeks,
)
from options_analyzer.domain.models import Leg, OptionContract, Position


def make_contract(**overrides: Any) -> OptionContract:
    """Create an OptionContract with sensible defaults."""
    defaults: dict[str, Any] = {
        "symbol": "AAPL  240119C00150000",
        "underlying": "AAPL",
        "option_type": OptionType.CALL,
        "strike": Decimal("150"),
        "expiration": date.today() + timedelta(days=30),
        "exercise_style": ExerciseStyle.AMERICAN,
        "multiplier": 100,
    }
    defaults.update(overrides)
    return OptionContract(**defaults)


def make_leg(**overrides: Any) -> Leg:
    """Create a Leg with sensible defaults."""
    defaults: dict[str, Any] = {
        "contract": make_contract(),
        "side": PositionSide.LONG,
        "quantity": 1,
        "open_price": Decimal("5.00"),
    }
    defaults.update(overrides)
    return Leg(**defaults)


def make_position(**overrides: Any) -> Position:
    """Create a Position with sensible defaults (single-leg)."""
    defaults: dict[str, Any] = {
        "id": "test-pos-1",
        "name": "Test Position",
        "underlying": "AAPL",
        "legs": [make_leg()],
        "opened_at": datetime(2024, 1, 1, tzinfo=UTC),
    }
    defaults.update(overrides)
    return Position(**defaults)


def make_first_order_greeks(**overrides: Any) -> FirstOrderGreeks:
    """Create FirstOrderGreeks with typical ATM call values."""
    defaults: dict[str, Any] = {
        "delta": 0.5,
        "gamma": 0.05,
        "theta": -0.05,
        "vega": 0.2,
        "rho": 0.01,
        "iv": 0.25,
    }
    defaults.update(overrides)
    return FirstOrderGreeks(**defaults)


def make_second_order_greeks(**overrides: Any) -> SecondOrderGreeks:
    """Create SecondOrderGreeks with reasonable near-zero values."""
    defaults: dict[str, Any] = {
        "vanna": 0.01,
        "volga": 0.02,
        "charm": -0.001,
        "veta": -0.005,
        "speed": 0.0001,
        "color": -0.0001,
    }
    defaults.update(overrides)
    return SecondOrderGreeks(**defaults)


def make_full_greeks(**overrides: Any) -> FullGreeks:
    """Create FullGreeks combining first + second order defaults."""
    defaults: dict[str, Any] = {
        "first_order": make_first_order_greeks(),
        "second_order": make_second_order_greeks(),
    }
    defaults.update(overrides)
    return FullGreeks(**defaults)


def make_vertical_spread(
    underlying: str,
    strikes: list[Decimal],
    option_type: OptionType = OptionType.CALL,
) -> Position:
    """Create a vertical spread (bull call or bear put)."""
    expiration = date.today() + timedelta(days=30)
    legs = [
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  C{strikes[0]}",
                underlying=underlying,
                option_type=option_type,
                strike=strikes[0],
                expiration=expiration,
            ),
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5.00"),
        ),
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  C{strikes[1]}",
                underlying=underlying,
                option_type=option_type,
                strike=strikes[1],
                expiration=expiration,
            ),
            side=PositionSide.SHORT,
            quantity=1,
            open_price=Decimal("3.00"),
        ),
    ]
    return Position(
        id="vertical-1",
        name=f"{underlying} {strikes[0]}/{strikes[1]} Vertical",
        underlying=underlying,
        legs=legs,
        opened_at=datetime.now(tz=UTC),
    )


def make_butterfly(
    underlying: str,
    strikes: list[Decimal],
    option_type: OptionType = OptionType.CALL,
) -> Position:
    """Create a butterfly spread (long wing/short body/long wing)."""
    expiration = date.today() + timedelta(days=30)
    legs = [
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  C{strikes[0]}",
                underlying=underlying,
                option_type=option_type,
                strike=strikes[0],
                expiration=expiration,
            ),
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("12.00"),
        ),
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  C{strikes[1]}",
                underlying=underlying,
                option_type=option_type,
                strike=strikes[1],
                expiration=expiration,
            ),
            side=PositionSide.SHORT,
            quantity=2,
            open_price=Decimal("7.00"),
        ),
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  C{strikes[2]}",
                underlying=underlying,
                option_type=option_type,
                strike=strikes[2],
                expiration=expiration,
            ),
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("3.50"),
        ),
    ]
    return Position(
        id="butterfly-1",
        name=f"{underlying} {strikes[0]}/{strikes[1]}/{strikes[2]} Butterfly",
        underlying=underlying,
        legs=legs,
        opened_at=datetime.now(tz=UTC),
    )


def make_iron_condor(
    underlying: str,
    strikes: list[Decimal],
) -> Position:
    """Create an iron condor (long put spread + short call spread).

    strikes: [put_long, put_short, call_short, call_long]
    """
    expiration = date.today() + timedelta(days=30)
    legs = [
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  P{strikes[0]}",
                underlying=underlying,
                option_type=OptionType.PUT,
                strike=strikes[0],
                expiration=expiration,
            ),
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("1.00"),
        ),
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  P{strikes[1]}",
                underlying=underlying,
                option_type=OptionType.PUT,
                strike=strikes[1],
                expiration=expiration,
            ),
            side=PositionSide.SHORT,
            quantity=1,
            open_price=Decimal("2.00"),
        ),
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  C{strikes[2]}",
                underlying=underlying,
                option_type=OptionType.CALL,
                strike=strikes[2],
                expiration=expiration,
            ),
            side=PositionSide.SHORT,
            quantity=1,
            open_price=Decimal("2.00"),
        ),
        Leg(
            contract=OptionContract(
                symbol=f"{underlying}  C{strikes[3]}",
                underlying=underlying,
                option_type=OptionType.CALL,
                strike=strikes[3],
                expiration=expiration,
            ),
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("1.00"),
        ),
    ]
    return Position(
        id="iron-condor-1",
        name=f"{underlying} {strikes[0]}/{strikes[1]}/{strikes[2]}/{strikes[3]} IC",
        underlying=underlying,
        legs=legs,
        opened_at=datetime.now(tz=UTC),
    )
