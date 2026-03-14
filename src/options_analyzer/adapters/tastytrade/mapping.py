"""Mapping layer — converts TastyTrade SDK objects to/from domain models.

This is the ONLY file (besides session.py) that imports tastytrade SDK types.
All other code depends on domain models exclusively.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from options_analyzer.domain.candles import CandleBar
from options_analyzer.domain.enums import ExerciseStyle, OptionType, PositionSide
from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import Leg, OptionContract

if TYPE_CHECKING:
    from datetime import datetime

    from tastytrade.account import CurrentPosition
    from tastytrade.dxfeed import Candle, Greeks
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


def instrument_type_for_symbol(symbol: str) -> str:
    """Return 'INDEX' or 'EQUITY' for a given symbol.

    Index symbols (SPX, VIX, VIX3M, NDX, RUT, DJX) require a different
    TastyTrade REST API call than equities/ETFs.
    """
    raise NotImplementedError


def map_market_data_to_bar(data: Any, symbol: str) -> CandleBar | None:
    """Map a TastyTrade REST MarketData response to a domain CandleBar.

    Returns None if essential OHLC fields are missing (e.g. pre-market).
    """
    raise NotImplementedError


def map_candle_to_bar(
    candle: Candle | Any, symbol: str, timestamp: datetime | None = None
) -> CandleBar:
    """Map a tastytrade dxfeed Candle event to a domain CandleBar."""
    import datetime as dt_mod

    if timestamp is not None:
        ts = timestamp
    elif isinstance(candle.time, dt_mod.datetime):
        ts = candle.time
    else:
        # SDK may return epoch millis as int
        ts = dt_mod.datetime.fromtimestamp(
            candle.time / 1000, tz=dt_mod.UTC
        )
    return CandleBar(
        symbol=symbol,
        timestamp=ts,
        open=float(candle.open),
        high=float(candle.high),
        low=float(candle.low),
        close=float(candle.close),
        volume=int(candle.volume) if candle.volume else 0,
    )
