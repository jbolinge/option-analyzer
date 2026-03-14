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


_INDEX_SYMBOLS: frozenset[str] = frozenset(
    {"SPX", "VIX", "VIX3M", "NDX", "RUT", "DJX"}
)


def instrument_type_for_symbol(symbol: str) -> str:
    """Return 'INDEX' or 'EQUITY' for a given symbol.

    Index symbols (SPX, VIX, VIX3M, NDX, RUT, DJX) require a different
    TastyTrade REST API call than equities/ETFs.
    """
    clean = symbol.lstrip("$")
    return "INDEX" if clean in _INDEX_SYMBOLS else "EQUITY"


def map_market_data_to_bar(data: Any, symbol: str) -> CandleBar | None:
    """Map a TastyTrade REST MarketData response to a domain CandleBar.

    Returns None if essential OHLC fields (open, last) are missing —
    e.g. pre-market before an open price exists.
    """
    import datetime as dt_mod

    open_price = getattr(data, "open", None)
    close_price = getattr(data, "last", None)

    if open_price is None or close_price is None:
        return None

    high_price = getattr(data, "day_high_price", None)
    if high_price is None:
        high_price = getattr(data, "day_high", None)
    if high_price is None:
        high_price = open_price

    low_price = getattr(data, "day_low_price", None)
    if low_price is None:
        low_price = getattr(data, "day_low", None)
    if low_price is None:
        low_price = open_price

    volume = getattr(data, "volume", None)

    ts = dt_mod.datetime.combine(
        data.summary_date,
        dt_mod.time(16, 0),
        tzinfo=dt_mod.UTC,
    )

    return CandleBar(
        symbol=symbol,
        timestamp=ts,
        open=float(open_price),
        high=float(high_price),
        low=float(low_price),
        close=float(close_price),
        volume=int(volume) if volume else 0,
    )


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
