"""DXLink streaming wrapper for real-time Greeks and quote data."""

from __future__ import annotations

from collections.abc import AsyncIterator
from decimal import Decimal
from typing import TYPE_CHECKING

from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import Greeks, Quote

from options_analyzer.adapters.tastytrade.mapping import map_greeks_to_first_order
from options_analyzer.domain.greeks import FirstOrderGreeks

if TYPE_CHECKING:
    from options_analyzer.adapters.tastytrade.session import TastyTradeSession


class DXLinkStreamerWrapper:
    """Wraps the tastytrade DXLinkStreamer for streaming Greeks and quotes."""

    def __init__(self, session: TastyTradeSession) -> None:
        self._session = session

    async def subscribe_greeks(
        self, streamer_symbols: list[str]
    ) -> AsyncIterator[tuple[str, FirstOrderGreeks]]:
        """Subscribe to Greeks stream for given option streamer symbols."""
        if not streamer_symbols:
            return
        async with DXLinkStreamer(self._session.session) as streamer:
            await streamer.subscribe(Greeks, streamer_symbols)
            async for greeks_event in streamer.listen(Greeks):
                yield (
                    greeks_event.event_symbol,
                    map_greeks_to_first_order(greeks_event),
                )

    async def subscribe_quotes(
        self, symbols: list[str]
    ) -> AsyncIterator[tuple[str, Decimal, Decimal]]:
        """Subscribe to bid/ask quote stream for given symbols."""
        if not symbols:
            return
        async with DXLinkStreamer(self._session.session) as streamer:
            await streamer.subscribe(Quote, symbols)
            async for quote in streamer.listen(Quote):
                yield (quote.event_symbol, quote.bid_price, quote.ask_price)
