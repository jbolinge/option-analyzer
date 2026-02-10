"""DXLink streaming wrapper for real-time Greeks and quote data."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import Greeks, Quote

from options_analyzer.adapters.tastytrade.mapping import map_greeks_to_first_order
from options_analyzer.domain.greeks import FirstOrderGreeks

if TYPE_CHECKING:
    from options_analyzer.adapters.tastytrade.session import TastyTradeSession


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

    async def subscribe_greeks_and_quotes(
        self,
        greeks_symbols: list[str],
        quote_symbols: list[str],
    ) -> AsyncIterator[StreamUpdate]:
        """Subscribe to both Greeks and Quote streams on a single connection.

        Greeks events are low-frequency (server-side IV recomputation).
        Quote events are high-frequency (every bid/ask change).
        Both are merged into a single async stream of tagged updates.
        """
        if not greeks_symbols and not quote_symbols:
            return

        queue: asyncio.Queue[StreamUpdate] = asyncio.Queue()

        async def _listen_greeks(streamer: DXLinkStreamer) -> None:
            async for event in streamer.listen(Greeks):
                await queue.put(
                    GreeksUpdate(
                        event_symbol=event.event_symbol,
                        greeks=map_greeks_to_first_order(event),
                    )
                )

        async def _listen_quotes(streamer: DXLinkStreamer) -> None:
            async for event in streamer.listen(Quote):
                await queue.put(
                    QuoteUpdate(
                        event_symbol=event.event_symbol,
                        bid_price=event.bid_price,
                        ask_price=event.ask_price,
                    )
                )

        async with DXLinkStreamer(self._session.session) as streamer:
            if greeks_symbols:
                await streamer.subscribe(Greeks, greeks_symbols)
            if quote_symbols:
                await streamer.subscribe(Quote, quote_symbols)

            tasks: list[asyncio.Task[None]] = []
            if greeks_symbols:
                tasks.append(asyncio.create_task(_listen_greeks(streamer)))
            if quote_symbols:
                tasks.append(asyncio.create_task(_listen_quotes(streamer)))

            try:
                while True:
                    update = await queue.get()
                    yield update
            except GeneratorExit:
                pass
            finally:
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
