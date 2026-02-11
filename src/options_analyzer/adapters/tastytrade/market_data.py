"""TastyTrade market data provider — implements MarketDataProvider port."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import Greeks, Quote
from tastytrade.instruments import get_option_chain
from tastytrade.market_data import get_market_data
from tastytrade.order import InstrumentType

from options_analyzer.adapters.tastytrade.mapping import (
    map_greeks_to_first_order,
    map_option_to_contract,
)
from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import OptionContract
from options_analyzer.domain.streaming import GreeksUpdate, StreamUpdate
from options_analyzer.ports.market_data import MarketDataProvider

if TYPE_CHECKING:
    from options_analyzer.adapters.tastytrade.session import TastyTradeSession


class TastyTradeMarketDataProvider(MarketDataProvider):
    """Fetches option chains, prices, and streams data via TastyTrade."""

    def __init__(self, session: TastyTradeSession) -> None:
        self._session = session
        self._streamer_symbols: dict[str, str] = {}

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
            mapped = []
            for opt in options:
                contract = map_option_to_contract(opt)
                if opt.streamer_symbol:
                    self._streamer_symbols[contract.symbol] = opt.streamer_symbol
                mapped.append(contract)
            result[exp_date] = mapped
        return result

    def get_streamer_symbols(
        self, contracts: list[OptionContract]
    ) -> list[str]:
        """Resolve contracts to their provider-specific streaming identifiers."""
        return [
            self._streamer_symbols[c.symbol]
            for c in contracts
            if c.symbol in self._streamer_symbols
        ]

    async def get_underlying_price(self, symbol: str) -> Decimal:
        data = await get_market_data(
            self._session.session, symbol, InstrumentType.EQUITY
        )
        if data.mid is not None:
            return data.mid
        if data.bid is not None and data.ask is not None:
            return (data.bid + data.ask) / 2
        return data.mark

    async def stream_greeks(
        self, contracts: list[OptionContract]
    ) -> AsyncIterator[tuple[str, FirstOrderGreeks]]:
        symbols = self.get_streamer_symbols(contracts)
        # Reverse map: streamer_symbol -> canonical contract.symbol
        reverse_map = {
            self._streamer_symbols[c.symbol]: c.symbol
            for c in contracts
            if c.symbol in self._streamer_symbols
        }
        async with DXLinkStreamer(self._session.session) as streamer:
            await streamer.subscribe(Greeks, symbols)
            async for greeks_event in streamer.listen(Greeks):
                canonical = reverse_map.get(
                    greeks_event.event_symbol, greeks_event.event_symbol
                )
                yield (canonical, map_greeks_to_first_order(greeks_event))

    async def stream_quotes(
        self, symbols: list[str]
    ) -> AsyncIterator[tuple[str, Decimal, Decimal]]:
        async with DXLinkStreamer(self._session.session) as streamer:
            await streamer.subscribe(Quote, symbols)
            async for quote in streamer.listen(Quote):
                yield (quote.event_symbol, quote.bid_price, quote.ask_price)

    async def stream_greeks_and_quotes(
        self,
        contracts: list[OptionContract],
        quote_symbols: list[str],
    ) -> AsyncIterator[StreamUpdate]:
        """Stream combined Greeks + Quotes, translating to canonical symbols."""
        from options_analyzer.adapters.tastytrade.streaming import (
            DXLinkStreamerWrapper,
        )

        greeks_symbols = self.get_streamer_symbols(contracts)
        # Reverse map: streamer_symbol -> canonical contract.symbol
        reverse_map = {
            self._streamer_symbols[c.symbol]: c.symbol
            for c in contracts
            if c.symbol in self._streamer_symbols
        }
        wrapper = DXLinkStreamerWrapper(self._session)
        all_quote_symbols = quote_symbols + greeks_symbols
        async for update in wrapper.subscribe_greeks_and_quotes(
            greeks_symbols, all_quote_symbols
        ):
            if isinstance(update, GreeksUpdate):
                canonical = reverse_map.get(
                    update.event_symbol, update.event_symbol
                )
                yield GreeksUpdate(
                    event_symbol=canonical, greeks=update.greeks
                )
            else:
                yield update
