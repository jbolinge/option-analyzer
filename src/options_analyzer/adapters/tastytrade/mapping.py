"""Mapping layer — converts TastyTrade SDK objects to/from domain models.

This is the ONLY file (besides session.py) that imports tastytrade SDK types.
All other code depends on domain models exclusively.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from options_analyzer.domain.enums import ExerciseStyle, OptionType, PositionSide
from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import Leg, OptionContract

if TYPE_CHECKING:
    from tastytrade.account import CurrentPosition
    from tastytrade.dxfeed import Greeks
    from tastytrade.instruments import Option


def map_option_to_contract(option: Option | Any) -> OptionContract:
    """Map a tastytrade Option instrument to a domain OptionContract."""
    option_type = (
        OptionType.CALL if option.option_type.value == "C" else OptionType.PUT
    )
    exercise_raw = option.exercise_style.lower()
    exercise_style = (
        ExerciseStyle.EUROPEAN if exercise_raw == "european" else ExerciseStyle.AMERICAN
    )
    return OptionContract(
        symbol=option.symbol,
        underlying=option.underlying_symbol,
        option_type=option_type,
        strike=option.strike_price,
        expiration=option.expiration_date,
        exercise_style=exercise_style,
        multiplier=option.shares_per_contract,
        streamer_symbol=option.streamer_symbol,
    )


def map_position_to_leg(
    position: CurrentPosition | Any, option: Option | Any
) -> Leg:
    """Map a tastytrade CurrentPosition + Option to a domain Leg."""
    contract = map_option_to_contract(option)
    side = (
        PositionSide.LONG
        if position.quantity_direction == "Long"
        else PositionSide.SHORT
    )
    return Leg(
        contract=contract,
        side=side,
        quantity=abs(int(position.quantity)),
        open_price=position.average_open_price,
    )


def map_greeks_to_first_order(greeks: Greeks | Any) -> FirstOrderGreeks:
    """Map a tastytrade dxfeed Greeks event to a domain FirstOrderGreeks."""
    return FirstOrderGreeks(
        delta=float(greeks.delta),
        gamma=float(greeks.gamma),
        theta=float(greeks.theta),
        vega=float(greeks.vega),
        rho=float(greeks.rho),
        iv=float(greeks.volatility),
    )
