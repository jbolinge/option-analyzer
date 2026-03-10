"""Tests for candle fetching — mapping and adapter."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from options_analyzer.adapters.tastytrade.mapping import map_candle_to_bar
from options_analyzer.adapters.tastytrade.market_data import (
    TastyTradeMarketDataProvider,
)


def _make_sdk_candle(**overrides: object) -> MagicMock:
    """Create a mock tastytrade Candle event with realistic defaults."""
    defaults = {
        "event_symbol": "$SPX{=1d}",
        "time": datetime(2024, 6, 15, 16, 0, tzinfo=UTC),
        "open": 5500.0,
        "high": 5520.0,
        "low": 5480.0,
        "close": 5510.0,
        "volume": 1_000_000.0,
        "event_flags": 0,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


class TestMapCandleToBar:
    """Tests for map_candle_to_bar mapping function."""

    def test_maps_all_fields(self) -> None:
        candle = _make_sdk_candle()
        bar = map_candle_to_bar(candle, "SPX")
        assert bar.symbol == "SPX"
        assert bar.open == 5500.0
        assert bar.high == 5520.0
        assert bar.low == 5480.0
        assert bar.close == 5510.0
        assert bar.volume == 1_000_000

    def test_timestamp_from_candle(self) -> None:
        ts = datetime(2024, 7, 1, 16, 0, tzinfo=UTC)
        candle = _make_sdk_candle(time=ts)
        bar = map_candle_to_bar(candle, "SPX")
        assert bar.timestamp == ts

    def test_timestamp_override(self) -> None:
        override_ts = datetime(2024, 8, 1, 16, 0, tzinfo=UTC)
        candle = _make_sdk_candle()
        bar = map_candle_to_bar(candle, "SPX", timestamp=override_ts)
        assert bar.timestamp == override_ts

    def test_zero_volume(self) -> None:
        candle = _make_sdk_candle(volume=0)
        bar = map_candle_to_bar(candle, "SPX")
        assert bar.volume == 0

    def test_none_volume_defaults_to_zero(self) -> None:
        candle = _make_sdk_candle(volume=None)
        bar = map_candle_to_bar(candle, "SPX")
        assert bar.volume == 0

    def test_symbol_passthrough(self) -> None:
        candle = _make_sdk_candle()
        bar = map_candle_to_bar(candle, "AAPL")
        assert bar.symbol == "AAPL"

    def test_float_conversion(self) -> None:
        candle = _make_sdk_candle(open=100, high=110, low=90, close=105)
        bar = map_candle_to_bar(candle, "SPX")
        assert isinstance(bar.open, float)
        assert isinstance(bar.close, float)


def _make_provider() -> TastyTradeMarketDataProvider:
    """Create a provider with a mocked session."""
    session = MagicMock()
    session.session = MagicMock()
    return TastyTradeMarketDataProvider(session)


def _candle_events(n: int = 3) -> list[MagicMock]:
    """Create a list of mock candle events with distinct timestamps."""
    events = []
    for i in range(n):
        events.append(
            _make_sdk_candle(
                time=datetime(2024, 6, 15 + i, 16, 0, tzinfo=UTC),
                close=5500.0 + i,
                snapshot_end=(i == n - 1),
                snapshot_snip=False,
                remove=False,
            )
        )
    return events


class TestGetCandlesRetry:
    """Tests for retry logic in get_candles."""

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self) -> None:
        provider = _make_provider()
        events = _candle_events(3)
        with patch.object(
            provider, "_fetch_candle_events", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = events
            result = await provider.get_candles("SPX", days_back=30)

        assert len(result.bars) == 3
        assert mock_fetch.await_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_empty_then_success(self) -> None:
        provider = _make_provider()
        events = _candle_events(2)
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock
            ) as mock_fetch,
            patch("options_analyzer.adapters.tastytrade.market_data.asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
        ):
            mock_fetch.side_effect = [[], events]
            result = await provider.get_candles("SPX", days_back=30)

        assert len(result.bars) == 2
        assert mock_fetch.await_count == 2
        mock_sleep.assert_awaited_once_with(2)

    @pytest.mark.asyncio
    async def test_all_attempts_fail_falls_back_to_yfinance(self) -> None:
        provider = _make_provider()
        mock_series = MagicMock()
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock
            ) as mock_fetch,
            patch("options_analyzer.adapters.tastytrade.market_data.asyncio.sleep", new_callable=AsyncMock),
            patch(
                "options_analyzer.adapters.yfinance_candles.fetch_candles_yfinance",
                new_callable=AsyncMock,
            ) as mock_yf,
        ):
            mock_fetch.return_value = []
            mock_yf.return_value = mock_series
            result = await provider.get_candles("SPX", days_back=30)

        assert mock_fetch.await_count == 3
        mock_yf.assert_awaited_once()
        assert result is mock_series

    @pytest.mark.asyncio
    async def test_dollar_prefix_not_doubled(self) -> None:
        """Symbol already prefixed with $ should not be doubled."""
        provider = _make_provider()
        events = _candle_events(1)
        with patch.object(
            provider, "_fetch_candle_events", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = events
            await provider.get_candles("$SPX", days_back=30)

        call_args = mock_fetch.call_args
        assert call_args[0][0] == "$SPX"  # not "$$SPX"


class TestYfinanceFallback:
    """Tests for yfinance fallback when DXLink returns 0 events."""

    @pytest.mark.asyncio
    async def test_fallback_called_when_dxlink_empty(self) -> None:
        """When all DXLink attempts fail, yfinance fallback is used."""
        provider = _make_provider()
        mock_series = MagicMock()
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock
            ) as mock_fetch,
            patch("options_analyzer.adapters.tastytrade.market_data.asyncio.sleep", new_callable=AsyncMock),
            patch(
                "options_analyzer.adapters.yfinance_candles.fetch_candles_yfinance",
                new_callable=AsyncMock,
            ) as mock_yf,
        ):
            mock_fetch.return_value = []
            mock_yf.return_value = mock_series
            result = await provider.get_candles("SPX", days_back=30)

        mock_yf.assert_awaited_once_with("SPX", "1d", 30)
        assert result is mock_series

    @pytest.mark.asyncio
    async def test_fallback_not_called_when_dxlink_succeeds(self) -> None:
        """When DXLink returns data, yfinance is not called."""
        provider = _make_provider()
        events = _candle_events(3)
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock
            ) as mock_fetch,
            patch(
                "options_analyzer.adapters.yfinance_candles.fetch_candles_yfinance",
                new_callable=AsyncMock,
            ) as mock_yf,
        ):
            mock_fetch.return_value = events
            result = await provider.get_candles("SPX", days_back=30)

        mock_yf.assert_not_awaited()
        assert len(result.bars) == 3
