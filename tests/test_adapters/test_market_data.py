"""Tests for TastyTrade market data provider."""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from options_analyzer.adapters.tastytrade.market_data import (
    TastyTradeMarketDataProvider,
)
from options_analyzer.adapters.tastytrade.session import TastyTradeSession
from options_analyzer.domain.enums import OptionType
from options_analyzer.domain.models import OptionContract
from options_analyzer.ports.market_data import MarketDataProvider


def _make_sdk_option(
    symbol: str = "SPY  260220C00450000",
    underlying: str = "SPY",
    option_type_value: str = "C",
    strike: Decimal = Decimal("450"),
    expiration: date = date(2026, 2, 20),
    streamer_symbol: str = ".SPY260220C450",
) -> MagicMock:
    mock = MagicMock()
    mock.symbol = symbol
    mock.underlying_symbol = underlying
    mock.option_type.value = option_type_value
    mock.strike_price = strike
    mock.expiration_date = expiration
    mock.exercise_style = "American"
    mock.shares_per_contract = 100
    mock.streamer_symbol = streamer_symbol
    return mock


@pytest.fixture
def mock_session() -> MagicMock:
    mock = MagicMock(spec=TastyTradeSession)
    mock.session = MagicMock()
    return mock


class TestTastyTradeMarketDataProviderIsPort:
    def test_implements_market_data_provider(self) -> None:
        assert issubclass(TastyTradeMarketDataProvider, MarketDataProvider)


class TestGetOptionChain:
    @pytest.mark.asyncio
    async def test_returns_mapped_option_chain(self, mock_session: MagicMock) -> None:
        exp_date = date(2026, 2, 20)
        sdk_options = [
            _make_sdk_option(
                symbol="SPY  260220C00450000",
                strike=Decimal("450"),
                streamer_symbol=".SPY260220C450",
            ),
            _make_sdk_option(
                symbol="SPY  260220P00450000",
                option_type_value="P",
                strike=Decimal("450"),
                streamer_symbol=".SPY260220P450",
            ),
        ]
        sdk_chain = {exp_date: sdk_options}

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
            new_callable=AsyncMock,
            return_value=sdk_chain,
        ) as mock_get_chain:
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_option_chain("SPY")

            mock_get_chain.assert_called_once_with(mock_session.session, "SPY")
            assert exp_date in result
            contracts = result[exp_date]
            assert len(contracts) == 2
            assert isinstance(contracts[0], OptionContract)
            assert contracts[0].option_type == OptionType.CALL
            assert contracts[1].option_type == OptionType.PUT

    @pytest.mark.asyncio
    async def test_returns_empty_chain(self, mock_session: MagicMock) -> None:
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
            new_callable=AsyncMock,
            return_value={},
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_option_chain("INVALID")
            assert result == {}


class TestGetUnderlyingPrice:
    @pytest.mark.asyncio
    async def test_returns_mid_price(self, mock_session: MagicMock) -> None:
        mock_quote = MagicMock()
        mock_quote.bid_price = Decimal("450.10")
        mock_quote.ask_price = Decimal("450.20")

        mock_streamer = AsyncMock()
        mock_streamer.get_event = AsyncMock(return_value=mock_quote)
        mock_streamer.__aenter__ = AsyncMock(return_value=mock_streamer)
        mock_streamer.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.DXLinkStreamer",
            return_value=mock_streamer,
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_underlying_price("SPY")
            assert result == Decimal("450.15")


class TestConnectDisconnect:
    @pytest.mark.asyncio
    async def test_connect_delegates_to_session(self, mock_session: MagicMock) -> None:
        mock_session.connect = AsyncMock()
        provider = TastyTradeMarketDataProvider(mock_session)
        await provider.connect()
        mock_session.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_delegates_to_session(
        self, mock_session: MagicMock
    ) -> None:
        mock_session.disconnect = AsyncMock()
        provider = TastyTradeMarketDataProvider(mock_session)
        await provider.disconnect()
        mock_session.disconnect.assert_called_once()
