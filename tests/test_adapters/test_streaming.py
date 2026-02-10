"""Tests for TastyTrade DXLink streaming wrapper."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from tastytrade.dxfeed import Greeks, Quote

from options_analyzer.adapters.tastytrade.session import TastyTradeSession
from options_analyzer.adapters.tastytrade.streaming import (
    DXLinkStreamerWrapper,
    GreeksUpdate,
    QuoteUpdate,
)
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


def _make_mock_streamer(
    greeks_events: list[MagicMock] | None = None,
    quote_events: list[MagicMock] | None = None,
) -> AsyncMock:
    """Build a mock DXLinkStreamer that dispatches listen() by event type."""
    mock_streamer = AsyncMock()
    mock_streamer.__aenter__ = AsyncMock(return_value=mock_streamer)
    mock_streamer.__aexit__ = AsyncMock(return_value=False)

    async def mock_listen(event_type: object) -> object:
        if event_type is Greeks and greeks_events:
            for e in greeks_events:
                yield e
        elif event_type is Quote and quote_events:
            for e in quote_events:
                yield e

    mock_streamer.listen = mock_listen
    return mock_streamer


class TestSubscribeGreeksAndQuotes:
    @pytest.mark.asyncio
    async def test_yields_both_greeks_and_quote_updates(
        self, mock_session: MagicMock
    ) -> None:
        greeks_events = [_make_greeks_event(".SPY260220C450")]
        quote_events = [
            _make_quote_event("SPY", Decimal("450.10"), Decimal("450.20")),
        ]
        mock_streamer = _make_mock_streamer(greeks_events, quote_events)

        with patch(
            "options_analyzer.adapters.tastytrade.streaming.DXLinkStreamer",
            return_value=mock_streamer,
        ):
            wrapper = DXLinkStreamerWrapper(mock_session)
            results: list[GreeksUpdate | QuoteUpdate] = []
            async for update in wrapper.subscribe_greeks_and_quotes(
                [".SPY260220C450"], ["SPY"]
            ):
                results.append(update)
                if len(results) >= 2:
                    break

            greeks_results = [r for r in results if isinstance(r, GreeksUpdate)]
            quote_results = [r for r in results if isinstance(r, QuoteUpdate)]

            assert len(greeks_results) == 1
            assert greeks_results[0].event_symbol == ".SPY260220C450"
            assert isinstance(greeks_results[0].greeks, FirstOrderGreeks)
            assert greeks_results[0].greeks.delta == pytest.approx(0.55)

            assert len(quote_results) == 1
            assert quote_results[0].event_symbol == "SPY"
            assert quote_results[0].bid_price == Decimal("450.10")
            assert quote_results[0].ask_price == Decimal("450.20")

    @pytest.mark.asyncio
    async def test_empty_greeks_symbols_still_yields_quotes(
        self, mock_session: MagicMock
    ) -> None:
        quote_events = [
            _make_quote_event("SPY", Decimal("450.10"), Decimal("450.20")),
        ]
        mock_streamer = _make_mock_streamer(quote_events=quote_events)

        with patch(
            "options_analyzer.adapters.tastytrade.streaming.DXLinkStreamer",
            return_value=mock_streamer,
        ):
            wrapper = DXLinkStreamerWrapper(mock_session)
            results = []
            async for update in wrapper.subscribe_greeks_and_quotes([], ["SPY"]):
                results.append(update)
                if len(results) >= 1:
                    break

            assert len(results) == 1
            assert isinstance(results[0], QuoteUpdate)
            assert results[0].event_symbol == "SPY"

    @pytest.mark.asyncio
    async def test_empty_quote_symbols_still_yields_greeks(
        self, mock_session: MagicMock
    ) -> None:
        greeks_events = [_make_greeks_event(".SPY260220C450")]
        mock_streamer = _make_mock_streamer(greeks_events=greeks_events)

        with patch(
            "options_analyzer.adapters.tastytrade.streaming.DXLinkStreamer",
            return_value=mock_streamer,
        ):
            wrapper = DXLinkStreamerWrapper(mock_session)
            results = []
            async for update in wrapper.subscribe_greeks_and_quotes(
                [".SPY260220C450"], []
            ):
                results.append(update)
                if len(results) >= 1:
                    break

            assert len(results) == 1
            assert isinstance(results[0], GreeksUpdate)
            assert results[0].event_symbol == ".SPY260220C450"

    @pytest.mark.asyncio
    async def test_both_empty_yields_nothing(
        self, mock_session: MagicMock
    ) -> None:
        wrapper = DXLinkStreamerWrapper(mock_session)
        results = []
        async for update in wrapper.subscribe_greeks_and_quotes([], []):
            results.append(update)
        assert results == []
