"""Streaming domain types — tagged update wrappers for real-time data."""

from dataclasses import dataclass
from decimal import Decimal

from options_analyzer.domain.greeks import FirstOrderGreeks


@dataclass(frozen=True)
class GreeksUpdate:
    """Tagged wrapper for a Greeks streaming event."""

    event_symbol: str
    greeks: FirstOrderGreeks


@dataclass(frozen=True)
class QuoteUpdate:
    """Tagged wrapper for a Quote streaming event."""

    event_symbol: str
    bid_price: Decimal
    ask_price: Decimal


StreamUpdate = GreeksUpdate | QuoteUpdate
