"""Tests for test object factories."""

from decimal import Decimal

from options_analyzer.domain.enums import OptionType, PositionSide
from options_analyzer.domain.greeks import (
    FirstOrderGreeks,
    FullGreeks,
    SecondOrderGreeks,
)
from options_analyzer.domain.models import Leg, OptionContract, Position

from .factories import (
    make_butterfly,
    make_contract,
    make_first_order_greeks,
    make_full_greeks,
    make_iron_condor,
    make_leg,
    make_position,
    make_second_order_greeks,
    make_vertical_spread,
)


class TestMakeContract:
    def test_defaults_produce_valid_contract(self) -> None:
        contract = make_contract()
        assert isinstance(contract, OptionContract)
        assert contract.underlying == "AAPL"
        assert contract.option_type == OptionType.CALL
        assert contract.strike == Decimal("150")

    def test_overrides(self) -> None:
        contract = make_contract(underlying="TSLA", strike=Decimal("200"))
        assert contract.underlying == "TSLA"
        assert contract.strike == Decimal("200")


class TestMakeLeg:
    def test_defaults_produce_valid_leg(self) -> None:
        leg = make_leg()
        assert isinstance(leg, Leg)
        assert leg.side == PositionSide.LONG
        assert leg.quantity == 1

    def test_overrides(self) -> None:
        leg = make_leg(side=PositionSide.SHORT, quantity=5)
        assert leg.side == PositionSide.SHORT
        assert leg.quantity == 5


class TestMakePosition:
    def test_defaults_produce_valid_position(self) -> None:
        pos = make_position()
        assert isinstance(pos, Position)
        assert len(pos.legs) == 1

    def test_overrides(self) -> None:
        legs = [make_leg(), make_leg(side=PositionSide.SHORT)]
        pos = make_position(name="Custom", legs=legs)
        assert pos.name == "Custom"
        assert len(pos.legs) == 2


class TestMakeGreeks:
    def test_first_order_defaults(self) -> None:
        greeks = make_first_order_greeks()
        assert isinstance(greeks, FirstOrderGreeks)
        assert greeks.delta == 0.5

    def test_second_order_defaults(self) -> None:
        greeks = make_second_order_greeks()
        assert isinstance(greeks, SecondOrderGreeks)

    def test_full_greeks_defaults(self) -> None:
        greeks = make_full_greeks()
        assert isinstance(greeks, FullGreeks)
        assert isinstance(greeks.first_order, FirstOrderGreeks)
        assert isinstance(greeks.second_order, SecondOrderGreeks)


class TestStrategyHelpers:
    def test_vertical_spread(self) -> None:
        pos = make_vertical_spread("AAPL", [Decimal("150"), Decimal("160")])
        assert len(pos.legs) == 2
        assert pos.legs[0].side == PositionSide.LONG
        assert pos.legs[1].side == PositionSide.SHORT
        assert pos.legs[0].contract.strike == Decimal("150")
        assert pos.legs[1].contract.strike == Decimal("160")

    def test_butterfly(self) -> None:
        pos = make_butterfly("AAPL", [Decimal("150"), Decimal("160"), Decimal("170")])
        assert len(pos.legs) == 3
        assert pos.legs[0].side == PositionSide.LONG
        assert pos.legs[0].quantity == 1
        assert pos.legs[1].side == PositionSide.SHORT
        assert pos.legs[1].quantity == 2
        assert pos.legs[2].side == PositionSide.LONG
        assert pos.legs[2].quantity == 1

    def test_iron_condor(self) -> None:
        pos = make_iron_condor(
            "SPY", [Decimal("400"), Decimal("410"), Decimal("430"), Decimal("440")]
        )
        assert len(pos.legs) == 4
        # Put spread: long lower put, short higher put
        assert pos.legs[0].contract.option_type == OptionType.PUT
        assert pos.legs[0].side == PositionSide.LONG
        assert pos.legs[1].contract.option_type == OptionType.PUT
        assert pos.legs[1].side == PositionSide.SHORT
        # Call spread: short lower call, long higher call
        assert pos.legs[2].contract.option_type == OptionType.CALL
        assert pos.legs[2].side == PositionSide.SHORT
        assert pos.legs[3].contract.option_type == OptionType.CALL
        assert pos.legs[3].side == PositionSide.LONG
