"""Core domain models — OptionContract, Leg, Position."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, computed_field

from options_analyzer.domain.enums import ExerciseStyle, OptionType, PositionSide


class OptionContract(BaseModel):
    """Immutable model for a single option contract."""

    model_config = ConfigDict(frozen=True)

    symbol: str
    underlying: str
    option_type: OptionType
    strike: Decimal
    expiration: date
    exercise_style: ExerciseStyle = ExerciseStyle.AMERICAN
    multiplier: int = 100


class Leg(BaseModel):
    """A contract combined with a side, quantity, and open price."""

    model_config = ConfigDict(frozen=True)

    contract: OptionContract
    side: PositionSide
    quantity: int
    open_price: Decimal

    @computed_field  # type: ignore[prop-decorator]
    @property
    def signed_quantity(self) -> int:
        """Positive for LONG, negative for SHORT."""
        return self.quantity if self.side == PositionSide.LONG else -self.quantity


class Position(BaseModel):
    """Named collection of legs representing a multi-leg options strategy."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    underlying: str
    legs: list[Leg]
    opened_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def net_debit_credit(self) -> Decimal:
        """Sum of signed_quantity * open_price * multiplier across all legs."""
        total = Decimal(0)
        for leg in self.legs:
            total += leg.signed_quantity * leg.open_price * leg.contract.multiplier
        return total
