"""TastyTrade market data provider — implements MarketDataProvider port."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import Greeks, Quote
from tastytrade.instruments import get_option_chain

from options_analyzer.adapters.tastytrade.mapping import (
    map_greeks_to_first_order,
    map_option_to_contract,
)
from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import OptionContract
from options_analyzer.ports.market_data import MarketDataProvider

if TYPE_CHECKING:
    from options_analyzer.adapters.tastytrade.session import TastyTradeSession


class TastyTradeMarketDataProvider(MarketDataProvider):
    """Fetches option chains, prices, and streams data via TastyTrade."""

    def __init__(self, session: TastyTradeSession) -> None:
        self._session = session

    async def connect(self) -> None:
        await self._session.connect()

    async def disconnect(self) -> None:
        await self._session.disconnect()

    async def get_option_chain(
        self, underlying: str
    ) -> dict[date, list[OptionContract]]:
        sdk_chain = await get_option_chain(self._session.session, underlying)
        result: dict[date, list[OptionContract]] = {}
        for exp_date, options in sdk_chain.items():
            result[exp_date] = [map_option_to_contract(opt) for opt in options]
        return result

    async def get_underlying_price(self, symbol: str) -> Decimal:
        async with DXLinkStreamer(self._session.session) as streamer:
            await streamer.subscribe(Quote, [symbol])
            quote = await streamer.get_event(Quote)
            return (quote.bid_price + quote.ask_price) / 2

    async def stream_greeks(
        self, contracts: list[OptionContract]
    ) -> AsyncIterator[tuple[str, FirstOrderGreeks]]:
        symbols = [c.streamer_symbol for c in contracts if c.streamer_symbol]
        async with DXLinkStreamer(self._session.session) as streamer:
            await streamer.subscribe(Greeks, symbols)
            async for greeks_event in streamer.listen(Greeks):
                yield (
                    greeks_event.event_symbol,
                    map_greeks_to_first_order(greeks_event),
                )

    async def stream_quotes(
        self, symbols: list[str]
    ) -> AsyncIterator[tuple[str, Decimal, Decimal]]:
        async with DXLinkStreamer(self._session.session) as streamer:
            await streamer.subscribe(Quote, symbols)
            async for quote in streamer.listen(Quote):
                yield (quote.event_symbol, quote.bid_price, quote.ask_price)
