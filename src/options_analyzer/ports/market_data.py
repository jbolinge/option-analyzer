"""MarketDataProvider port — abstract interface for market data access."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal

from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import OptionContract


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
