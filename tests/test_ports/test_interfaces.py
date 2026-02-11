"""Tests for port ABC interfaces — MarketDataProvider and AccountProvider."""

from abc import ABC
from collections.abc import AsyncIterator
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import Leg, OptionContract
from options_analyzer.domain.streaming import GreeksUpdate, StreamUpdate
from options_analyzer.ports.account import AccountProvider
from options_analyzer.ports.market_data import MarketDataProvider


class TestMarketDataProviderABC:
    """Verify MarketDataProvider is a proper ABC."""

    def test_is_abstract_base_class(self) -> None:
        assert issubclass(MarketDataProvider, ABC)

    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError, match="abstract method"):
            MarketDataProvider()  # type: ignore[abstract]

    def test_subclass_must_implement_all_methods(self) -> None:
        class IncompleteProvider(MarketDataProvider):
            pass

        with pytest.raises(TypeError, match="abstract method"):
            IncompleteProvider()  # type: ignore[abstract]

    def test_concrete_subclass_instantiates(self) -> None:
        class ConcreteProvider(MarketDataProvider):
            async def connect(self) -> None:
                pass

            async def disconnect(self) -> None:
                pass

            async def get_option_chain(
                self, underlying: str
            ) -> dict[date, list[OptionContract]]:
                return {}

            async def get_underlying_price(self, symbol: str) -> Decimal:
                return Decimal("100")

            async def stream_greeks(
                self, contracts: list[OptionContract]
            ) -> AsyncIterator[tuple[str, FirstOrderGreeks]]:
                greeks = FirstOrderGreeks(
                    delta=0, gamma=0, theta=0, vega=0, rho=0, iv=0
                )
                yield ("", greeks)  # type: ignore[misc]

            async def stream_quotes(
                self, symbols: list[str]
            ) -> AsyncIterator[tuple[str, Decimal, Decimal]]:
                yield ("", Decimal("0"), Decimal("0"))  # type: ignore[misc]

            async def stream_greeks_and_quotes(
                self,
                contracts: list[OptionContract],
                quote_symbols: list[str],
            ) -> AsyncIterator[StreamUpdate]:
                greeks = FirstOrderGreeks(
                    delta=0, gamma=0, theta=0, vega=0, rho=0, iv=0
                )
                yield GreeksUpdate(event_symbol="", greeks=greeks)  # type: ignore[misc]

        provider = ConcreteProvider()
        assert isinstance(provider, MarketDataProvider)

    def test_has_required_abstract_methods(self) -> None:
        expected = {
            "connect",
            "disconnect",
            "get_option_chain",
            "get_underlying_price",
            "stream_greeks",
            "stream_quotes",
            "stream_greeks_and_quotes",
        }
        assert expected == set(MarketDataProvider.__abstractmethods__)


class TestAccountProviderABC:
    """Verify AccountProvider is a proper ABC."""

    def test_is_abstract_base_class(self) -> None:
        assert issubclass(AccountProvider, ABC)

    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError, match="abstract method"):
            AccountProvider()  # type: ignore[abstract]

    def test_subclass_must_implement_all_methods(self) -> None:
        class IncompleteProvider(AccountProvider):
            pass

        with pytest.raises(TypeError, match="abstract method"):
            IncompleteProvider()  # type: ignore[abstract]

    def test_concrete_subclass_instantiates(self) -> None:
        class ConcreteProvider(AccountProvider):
            async def get_accounts(self) -> list[str]:
                return []

            async def get_positions(
                self, account_id: str, underlying: str | None = None
            ) -> list[Leg]:
                return []

        provider = ConcreteProvider()
        assert isinstance(provider, AccountProvider)

    def test_has_required_abstract_methods(self) -> None:
        expected = {"get_accounts", "get_positions"}
        assert expected == set(AccountProvider.__abstractmethods__)


class TestMockImplementation:
    """Verify mock implementations work with port interfaces."""

    @pytest.mark.asyncio
    async def test_mock_market_data_get_option_chain(self) -> None:
        mock = AsyncMock(spec=MarketDataProvider)
        mock.get_option_chain.return_value = {}
        result = await mock.get_option_chain("SPY")
        assert result == {}
        mock.get_option_chain.assert_called_once_with("SPY")

    @pytest.mark.asyncio
    async def test_mock_market_data_get_underlying_price(self) -> None:
        mock = AsyncMock(spec=MarketDataProvider)
        mock.get_underlying_price.return_value = Decimal("450.50")
        result = await mock.get_underlying_price("SPY")
        assert result == Decimal("450.50")

    @pytest.mark.asyncio
    async def test_mock_account_get_accounts(self) -> None:
        mock = AsyncMock(spec=AccountProvider)
        mock.get_accounts.return_value = ["5WX01234", "5WX05678"]
        result = await mock.get_accounts()
        assert result == ["5WX01234", "5WX05678"]

    @pytest.mark.asyncio
    async def test_mock_account_get_positions(self) -> None:
        mock = AsyncMock(spec=AccountProvider)
        mock.get_positions.return_value = []
        result = await mock.get_positions("5WX01234", underlying="SPY")
        assert result == []
        mock.get_positions.assert_called_once_with("5WX01234", underlying="SPY")
