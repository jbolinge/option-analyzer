"""Tests for TastyTrade DXLink streaming wrapper."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from options_analyzer.adapters.tastytrade.session import TastyTradeSession
from options_analyzer.adapters.tastytrade.streaming import DXLinkStreamerWrapper
from options_analyzer.domain.greeks import FirstOrderGreeks


@pytest.fixture
def mock_session() -> MagicMock:
    mock = MagicMock(spec=TastyTradeSession)
    mock.session = MagicMock()
    return mock


def _make_greeks_event(
    symbol: str = ".SPY260220C450",
    delta: Decimal = Decimal("0.55"),
    gamma: Decimal = Decimal("0.04"),
    theta: Decimal = Decimal("-0.05"),
    vega: Decimal = Decimal("0.20"),
    rho: Decimal = Decimal("0.01"),
    volatility: Decimal = Decimal("0.25"),
) -> MagicMock:
    mock = MagicMock()
    mock.event_symbol = symbol
    mock.delta = delta
    mock.gamma = gamma
    mock.theta = theta
    mock.vega = vega
    mock.rho = rho
    mock.volatility = volatility
    return mock


def _make_quote_event(
    symbol: str = "SPY",
    bid: Decimal = Decimal("450.10"),
    ask: Decimal = Decimal("450.20"),
) -> MagicMock:
    mock = MagicMock()
    mock.event_symbol = symbol
    mock.bid_price = bid
    mock.ask_price = ask
    return mock


class TestDXLinkStreamerWrapperInit:
    def test_stores_session(self, mock_session: MagicMock) -> None:
        wrapper = DXLinkStreamerWrapper(mock_session)
        assert wrapper._session is mock_session


class TestSubscribeGreeks:
    @pytest.mark.asyncio
    async def test_yields_greeks_tuples(self, mock_session: MagicMock) -> None:
        events = [
            _make_greeks_event(".SPY260220C450"),
            _make_greeks_event(".SPY260220P450", delta=Decimal("-0.45")),
        ]

        mock_streamer = AsyncMock()
        mock_streamer.__aenter__ = AsyncMock(return_value=mock_streamer)
        mock_streamer.__aexit__ = AsyncMock(return_value=False)

        async def mock_listen(_event_type: object) -> object:
            for e in events:
                yield e

        mock_streamer.listen = mock_listen

        with patch(
            "options_analyzer.adapters.tastytrade.streaming.DXLinkStreamer",
            return_value=mock_streamer,
        ):
            wrapper = DXLinkStreamerWrapper(mock_session)
            results = []
            async for symbol, greeks in wrapper.subscribe_greeks(
                [".SPY260220C450", ".SPY260220P450"]
            ):
                results.append((symbol, greeks))

            assert len(results) == 2
            assert results[0][0] == ".SPY260220C450"
            assert isinstance(results[0][1], FirstOrderGreeks)
            assert results[0][1].delta == pytest.approx(0.55)
            assert results[1][1].delta == pytest.approx(-0.45)

    @pytest.mark.asyncio
    async def test_empty_symbols_yields_nothing(
        self, mock_session: MagicMock
    ) -> None:
        wrapper = DXLinkStreamerWrapper(mock_session)
        results = []
        async for item in wrapper.subscribe_greeks([]):
            results.append(item)
        assert results == []


class TestSubscribeQuotes:
    @pytest.mark.asyncio
    async def test_yields_quote_tuples(self, mock_session: MagicMock) -> None:
        events = [
            _make_quote_event("SPY", Decimal("450.10"), Decimal("450.20")),
            _make_quote_event("QQQ", Decimal("380.50"), Decimal("380.60")),
        ]

        mock_streamer = AsyncMock()
        mock_streamer.__aenter__ = AsyncMock(return_value=mock_streamer)
        mock_streamer.__aexit__ = AsyncMock(return_value=False)

        async def mock_listen(_event_type: object) -> object:
            for e in events:
                yield e

        mock_streamer.listen = mock_listen

        with patch(
            "options_analyzer.adapters.tastytrade.streaming.DXLinkStreamer",
            return_value=mock_streamer,
        ):
            wrapper = DXLinkStreamerWrapper(mock_session)
            results = []
            async for symbol, bid, ask in wrapper.subscribe_quotes(["SPY", "QQQ"]):
                results.append((symbol, bid, ask))

            assert len(results) == 2
            assert results[0] == ("SPY", Decimal("450.10"), Decimal("450.20"))
            assert results[1] == ("QQQ", Decimal("380.50"), Decimal("380.60"))

    @pytest.mark.asyncio
    async def test_empty_symbols_yields_nothing(
        self, mock_session: MagicMock
    ) -> None:
        wrapper = DXLinkStreamerWrapper(mock_session)
        results = []
        async for item in wrapper.subscribe_quotes([]):
            results.append(item)
        assert results == []
