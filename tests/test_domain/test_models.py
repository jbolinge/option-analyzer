"""Tests for domain models — OptionContract, Leg, Position."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from options_analyzer.domain.enums import ExerciseStyle, OptionType, PositionSide
from options_analyzer.domain.models import Leg, OptionContract, Position


class TestOptionContract:
    def test_creation_with_required_fields(self) -> None:
        contract = OptionContract(
            symbol="AAPL  240119C00150000",
            underlying="AAPL",
            option_type=OptionType.CALL,
            strike=Decimal("150"),
            expiration=date(2024, 1, 19),
        )
        assert contract.symbol == "AAPL  240119C00150000"
        assert contract.underlying == "AAPL"
        assert contract.option_type == OptionType.CALL
        assert contract.strike == Decimal("150")
        assert contract.expiration == date(2024, 1, 19)

    def test_defaults(self) -> None:
        contract = OptionContract(
            symbol="AAPL  240119C00150000",
            underlying="AAPL",
            option_type=OptionType.CALL,
            strike=Decimal("150"),
            expiration=date(2024, 1, 19),
        )
        assert contract.exercise_style == ExerciseStyle.AMERICAN
        assert contract.multiplier == 100

    def test_frozen(self) -> None:
        contract = OptionContract(
            symbol="AAPL  240119C00150000",
            underlying="AAPL",
            option_type=OptionType.CALL,
            strike=Decimal("150"),
            expiration=date(2024, 1, 19),
        )
        with pytest.raises(ValidationError):
            contract.symbol = "NEW"  # type: ignore[misc]

    def test_invalid_option_type_raises(self) -> None:
        with pytest.raises(ValidationError):
            OptionContract(
                symbol="AAPL  240119C00150000",
                underlying="AAPL",
                option_type="invalid",  # type: ignore[arg-type]
                strike=Decimal("150"),
                expiration=date(2024, 1, 19),
            )

    def test_serialization_roundtrip(self) -> None:
        contract = OptionContract(
            symbol="AAPL  240119C00150000",
            underlying="AAPL",
            option_type=OptionType.CALL,
            strike=Decimal("150"),
            expiration=date(2024, 1, 19),
        )
        data = contract.model_dump()
        restored = OptionContract.model_validate(data)
        assert restored == contract


class TestLeg:
    @pytest.fixture()
    def call_contract(self) -> OptionContract:
        return OptionContract(
            symbol="AAPL  240119C00150000",
            underlying="AAPL",
            option_type=OptionType.CALL,
            strike=Decimal("150"),
            expiration=date(2024, 1, 19),
        )

    def test_creation(self, call_contract: OptionContract) -> None:
        leg = Leg(
            contract=call_contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5.00"),
        )
        assert leg.contract == call_contract
        assert leg.side == PositionSide.LONG
        assert leg.quantity == 1
        assert leg.open_price == Decimal("5.00")

    def test_signed_quantity_long(self, call_contract: OptionContract) -> None:
        leg = Leg(
            contract=call_contract,
            side=PositionSide.LONG,
            quantity=3,
            open_price=Decimal("5.00"),
        )
        assert leg.signed_quantity == 3

    def test_signed_quantity_short(self, call_contract: OptionContract) -> None:
        leg = Leg(
            contract=call_contract,
            side=PositionSide.SHORT,
            quantity=2,
            open_price=Decimal("5.00"),
        )
        assert leg.signed_quantity == -2

    def test_frozen(self, call_contract: OptionContract) -> None:
        leg = Leg(
            contract=call_contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5.00"),
        )
        with pytest.raises(ValidationError):
            leg.quantity = 10  # type: ignore[misc]

    def test_serialization_roundtrip(self, call_contract: OptionContract) -> None:
        leg = Leg(
            contract=call_contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5.00"),
        )
        data = leg.model_dump()
        restored = Leg.model_validate(data)
        assert restored == leg
        assert restored.signed_quantity == leg.signed_quantity


class TestPosition:
    @pytest.fixture()
    def butterfly_position(self) -> Position:
        contracts = [
            OptionContract(
                symbol=f"AAPL  240119C00{strike}000",
                underlying="AAPL",
                option_type=OptionType.CALL,
                strike=Decimal(str(strike)),
                expiration=date(2024, 1, 19),
            )
            for strike in [150, 160, 170]
        ]
        legs = [
            Leg(
                contract=contracts[0],
                side=PositionSide.LONG,
                quantity=1,
                open_price=Decimal("12.00"),
            ),
            Leg(
                contract=contracts[1],
                side=PositionSide.SHORT,
                quantity=2,
                open_price=Decimal("7.00"),
            ),
            Leg(
                contract=contracts[2],
                side=PositionSide.LONG,
                quantity=1,
                open_price=Decimal("3.50"),
            ),
        ]
        return Position(
            id="pos-1",
            name="AAPL Jan 150/160/170 BWB",
            underlying="AAPL",
            legs=legs,
            opened_at=datetime(2024, 1, 1, tzinfo=UTC),
        )

    def test_creation(self, butterfly_position: Position) -> None:
        assert butterfly_position.id == "pos-1"
        assert butterfly_position.name == "AAPL Jan 150/160/170 BWB"
        assert butterfly_position.underlying == "AAPL"
        assert len(butterfly_position.legs) == 3

    def test_net_debit_credit(self, butterfly_position: Position) -> None:
        # Long 1 @ 12.00 * 100 = +1200
        # Short 2 @ 7.00 * 100 = -1400
        # Long 1 @ 3.50 * 100 = +350
        # Net = 1200 - 1400 + 350 = 150 (debit)
        expected = Decimal("150.00")
        assert butterfly_position.net_debit_credit == expected

    def test_frozen(self, butterfly_position: Position) -> None:
        with pytest.raises(ValidationError):
            butterfly_position.name = "new"  # type: ignore[misc]

    def test_serialization_roundtrip(self, butterfly_position: Position) -> None:
        data = butterfly_position.model_dump()
        restored = Position.model_validate(data)
        assert restored == butterfly_position
        assert restored.net_debit_credit == butterfly_position.net_debit_credit
