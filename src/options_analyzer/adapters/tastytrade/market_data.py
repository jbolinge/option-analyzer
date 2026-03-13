"""TastyTrade market data provider — implements MarketDataProvider port."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING

from tastytrade import DXLinkStreamer
from tastytrade.dxfeed import Candle, Greeks, Quote
from tastytrade.instruments import get_option_chain
from tastytrade.market_data import get_market_data
from tastytrade.order import InstrumentType

from options_analyzer.adapters.tastytrade.mapping import (
    map_candle_to_bar,
    map_greeks_to_first_order,
    map_option_to_contract,
)
from options_analyzer.domain.candles import CandleSeries
from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import OptionContract
from options_analyzer.domain.streaming import GreeksUpdate, StreamUpdate
from options_analyzer.ports.market_data import MarketDataProvider

if TYPE_CHECKING:
    from options_analyzer.adapters.tastytrade.session import TastyTradeSession

logger = logging.getLogger(__name__)


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

    async def _ensure_streamer_symbols(
        self, contracts: list[OptionContract]
    ) -> None:
        """Populate streamer symbol cache for any contracts not yet resolved."""
        missing_underlyings = {
            c.underlying
            for c in contracts
            if c.symbol not in self._streamer_symbols
        }
        for underlying in missing_underlyings:
            await self.get_option_chain(underlying)

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
        await self._ensure_streamer_symbols(contracts)
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

    async def get_candles(
        self,
        symbol: str,
        interval: str = "1d",
        days_back: int = 365,
    ) -> CandleSeries:
        """Fetch historical candle data via DXLink streamer.

        Index symbols (e.g. SPX) are prefixed with '$' per dxfeed convention.
        Falls back to yfinance if DXLink returns no events or fails.
        """
        use_dxlink = getattr(self._session, "use_dxlink_candles", True)

        candle_events: list[Candle] = []
        if use_dxlink:
            # dxfeed convention: index symbols need '$' prefix
            streamer_symbol = f"${symbol}" if not symbol.startswith("$") else symbol
            start_time = datetime.now(tz=UTC) - timedelta(days=days_back)

            candle_events = await self._fetch_candle_events(
                streamer_symbol, interval, start_time, timeout_seconds=3,
            )

        if not candle_events:
            if use_dxlink:
                logger.warning(
                    "DXLink returned 0 candle events for %s, "
                    "falling back to yfinance",
                    symbol,
                )
            else:
                logger.info(
                    "DXLink candles disabled, using yfinance for %s", symbol,
                )
            from options_analyzer.adapters.yfinance_candles import (
                fetch_candles_yfinance,
            )

            return await fetch_candles_yfinance(symbol, interval, days_back)

        # Sort by timestamp, deduplicate
        seen_times: set[object] = set()
        unique_bars = []
        for event in sorted(candle_events, key=lambda c: c.time):
            if event.time in seen_times:
                continue
            seen_times.add(event.time)
            bar = map_candle_to_bar(event, symbol)
            unique_bars.append(bar)

        return CandleSeries(bars=unique_bars)

    async def _fetch_candle_events(
        self,
        streamer_symbol: str,
        interval: str,
        start_time: datetime,
        timeout_seconds: float = 30,
    ) -> list[Candle]:
        """Single attempt to fetch candle events via a fresh DXLink connection."""
        events: list[Candle] = []
        try:
            async with asyncio.timeout(timeout_seconds):
                async with DXLinkStreamer(self._session.session) as streamer:
                    await streamer.subscribe_candle(
                        [streamer_symbol],
                        interval=interval,
                        start_time=start_time,
                    )
                    async for candle in streamer.listen(Candle):
                        if not candle.remove:
                            events.append(candle)
                        if candle.snapshot_end or candle.snapshot_snip:
                            break
        except TimeoutError:
            logger.debug(
                "Candle fetch timed out after %.0fs with %d events for %s",
                timeout_seconds, len(events), streamer_symbol,
            )
        except Exception as exc:
            logger.debug(
                "Candle fetch failed for %s: %s", streamer_symbol, exc,
            )
        return events

    async def stream_greeks_and_quotes(
        self,
        contracts: list[OptionContract],
        quote_symbols: list[str],
    ) -> AsyncIterator[StreamUpdate]:
        """Stream combined Greeks + Quotes, translating to canonical symbols."""
        from options_analyzer.adapters.tastytrade.streaming import (
            DXLinkStreamerWrapper,
        )

        await self._ensure_streamer_symbols(contracts)
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
