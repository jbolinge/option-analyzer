"""MarketDataProvider port — abstract interface for market data access."""

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal

from options_analyzer.domain.candles import CandleSeries, align_series
from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import OptionContract
from options_analyzer.domain.streaming import StreamUpdate

logger = logging.getLogger(__name__)


class MarketDataProvider(ABC):
    """Abstract interface for fetching option chains, prices, and streaming data."""

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def get_option_chain(
        self, underlying: str
    ) -> dict[date, list[OptionContract]]: ...

    @abstractmethod
    async def get_underlying_price(self, symbol: str) -> Decimal: ...

    @abstractmethod
    def stream_greeks(
        self, contracts: list[OptionContract]
    ) -> AsyncIterator[tuple[str, FirstOrderGreeks]]: ...

    @abstractmethod
    def stream_quotes(
        self, symbols: list[str]
    ) -> AsyncIterator[tuple[str, Decimal, Decimal]]: ...

    @abstractmethod
    def stream_greeks_and_quotes(
        self,
        contracts: list[OptionContract],
        quote_symbols: list[str],
    ) -> AsyncIterator[StreamUpdate]: ...

    @abstractmethod
    async def get_candles(
        self,
        symbol: str,
        interval: str = "1d",
        days_back: int = 365,
    ) -> CandleSeries: ...

    async def get_candles_batch(
        self,
        symbols: list[str],
        interval: str = "1d",
        days_back: int = 365,
    ) -> dict[str, CandleSeries]:
        """Fetch candles for multiple symbols and align to common timestamps.

        Default implementation calls get_candles() for each symbol concurrently,
        then aligns all series via timestamp intersection. Adapters may override
        for optimization.
        """
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

        if len(results) >= 2:
            ordered_symbols = [s for s in symbols if s in results]
            aligned = align_series(*(results[s] for s in ordered_symbols))
            results = dict(zip(ordered_symbols, aligned))

        return results
