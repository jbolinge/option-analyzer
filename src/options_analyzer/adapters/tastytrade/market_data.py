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
from tastytrade.market_data import get_market_data, get_market_data_by_type
from tastytrade.order import InstrumentType

from options_analyzer.adapters.tastytrade.mapping import (
    instrument_type_for_symbol,
    map_candle_to_bar,
    map_greeks_to_first_order,
    map_market_data_to_bar,
    map_option_to_contract,
)
from options_analyzer.domain.candles import CandleBar, CandleSeries, align_series
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
        If include_latest_candle is enabled, appends today's OHLCV from the
        TastyTrade REST API.
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

            series = await fetch_candles_yfinance(symbol, interval, days_back)
        else:
            # Sort by timestamp, deduplicate
            seen_times: set[object] = set()
            unique_bars = []
            for event in sorted(candle_events, key=lambda c: c.time):
                if event.time in seen_times:
                    continue
                seen_times.add(event.time)
                bar = map_candle_to_bar(event, symbol)
                unique_bars.append(bar)

            series = CandleSeries(bars=unique_bars)

        # Append latest candle from REST API if enabled
        include_latest = getattr(self._session, "include_latest_candle", False)
        if include_latest and interval == "1d":
            series = await self._append_latest_bar(series, symbol)

        return series

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

    async def _fetch_latest_bar(self, symbol: str) -> CandleBar | None:
        """Fetch today's OHLCV from TastyTrade REST API.

        Returns None on any failure — caller falls back to historical only.
        """
        try:
            clean_symbol = symbol.lstrip("$")
            if instrument_type_for_symbol(clean_symbol) == "INDEX":
                data_list = await get_market_data_by_type(
                    self._session.session, indices=[clean_symbol],
                )
                if not data_list:
                    return None
                data = data_list[0]
            else:
                data = await get_market_data(
                    self._session.session,
                    clean_symbol,
                    InstrumentType.EQUITY,
                )
            return map_market_data_to_bar(data, clean_symbol)
        except Exception as exc:
            logger.debug(
                "Latest candle fetch failed for %s: %s", symbol, exc,
            )
            return None

    async def _append_latest_bar(
        self, series: CandleSeries, symbol: str,
    ) -> CandleSeries:
        """Append or replace today's bar from the REST API.

        If the last historical bar has the same date as the latest bar,
        replace it (REST data is more current). Otherwise, append.
        """
        latest = await self._fetch_latest_bar(symbol)
        if latest is None:
            return series

        bars = list(series.bars)
        if bars and bars[-1].timestamp.date() == latest.timestamp.date():
            bars[-1] = latest
        else:
            bars.append(latest)

        return CandleSeries(bars=bars)

    async def get_candles_batch(
        self,
        symbols: list[str],
        interval: str = "1d",
        days_back: int = 365,
    ) -> dict[str, CandleSeries]:
        """Fetch candles for multiple symbols concurrently, aligned to common timestamps."""
        tasks = {
            sym: asyncio.create_task(self.get_candles(sym, interval, days_back))
            for sym in symbols
        }
        results: dict[str, CandleSeries] = {}
        for sym, task in tasks.items():
            try:
                results[sym] = await task
            except Exception as exc:
                logger.warning("Failed to fetch %s: %s", sym, exc)

        # Print per-symbol bar counts
        for sym, series in results.items():
            print(f"  {sym}: {len(series)} bars")

        # Align to common timestamps
        if len(results) >= 2:
            ordered_symbols = [s for s in symbols if s in results]
            pre_align_counts = {s: len(results[s]) for s in ordered_symbols}
            aligned = align_series(*(results[s] for s in ordered_symbols))
            results = dict(zip(ordered_symbols, aligned))

            # Log alignment summary if any trimming occurred
            aligned_len = len(next(iter(results.values())))
            trimmed = {
                s: pre_align_counts[s] - aligned_len
                for s in ordered_symbols
                if pre_align_counts[s] != aligned_len
            }
            if trimmed:
                logger.info(
                    "Aligned %d symbols to %d common bars (trimmed: %s)",
                    len(results), aligned_len,
                    ", ".join(f"{s}:-{n}" for s, n in trimmed.items()),
                )

        if results:
            any_series = next(iter(results.values()))
            if any_series.bars:
                ts = any_series.timestamps
                print(
                    f"\nFetched {len(results)}/{len(symbols)} symbols successfully "
                    f"({len(any_series)} bars, "
                    f"{ts[0]:%Y-%m-%d} to {ts[-1]:%Y-%m-%d})"
                )
            else:
                print(f"\nFetched {len(results)}/{len(symbols)} symbols (0 bars)")
        else:
            print(f"\nFetched 0/{len(symbols)} symbols")

        return results

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
