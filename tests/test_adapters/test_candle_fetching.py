"""Tests for candle fetching — mapping and adapter."""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from options_analyzer.adapters.tastytrade.mapping import (
    instrument_type_for_symbol,
    map_candle_to_bar,
    map_market_data_to_bar,
)
from options_analyzer.adapters.tastytrade.market_data import (
    TastyTradeMarketDataProvider,
)
from options_analyzer.domain.candles import CandleBar, CandleSeries


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


class TestGetCandles:
    """Tests for get_candles with single-attempt + yfinance fallback."""

    @pytest.mark.asyncio
    async def test_success_returns_bars(self) -> None:
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

    @pytest.mark.asyncio
    async def test_uses_3s_timeout(self) -> None:
        """get_candles passes a 3-second timeout to _fetch_candle_events."""
        provider = _make_provider()
        events = _candle_events(1)
        with patch.object(
            provider, "_fetch_candle_events", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.return_value = events
            await provider.get_candles("SPX", days_back=30)

        _, kwargs = mock_fetch.call_args
        assert kwargs.get("timeout_seconds") == 3

    @pytest.mark.asyncio
    async def test_fallback_on_empty_events(self) -> None:
        """When DXLink returns no events, yfinance fallback is used."""
        provider = _make_provider()
        mock_series = MagicMock()
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock
            ) as mock_fetch,
            patch(
                "options_analyzer.adapters.yfinance_candles.fetch_candles_yfinance",
                new_callable=AsyncMock,
            ) as mock_yf,
        ):
            mock_fetch.return_value = []
            mock_yf.return_value = mock_series
            result = await provider.get_candles("SPX", days_back=30)

        assert mock_fetch.await_count == 1
        mock_yf.assert_awaited_once_with("SPX", "1d", 30)
        assert result is mock_series

    @pytest.mark.asyncio
    async def test_no_fallback_when_dxlink_succeeds(self) -> None:
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


class TestFetchCandleEventsExceptionHandling:
    """Tests for exception handling in _fetch_candle_events."""

    @pytest.mark.asyncio
    async def test_timeout_error_returns_partial_events(self) -> None:
        """TimeoutError is caught and partial events are returned."""
        provider = _make_provider()

        async def _timeout_streamer(*_args: object, **_kwargs: object) -> list:
            raise TimeoutError

        with patch.object(
            provider, "_fetch_candle_events", wraps=provider._fetch_candle_events
        ):
            # Use the real method but mock DXLinkStreamer to raise TimeoutError
            with patch(
                "options_analyzer.adapters.tastytrade.market_data.DXLinkStreamer",
                side_effect=TimeoutError,
            ):
                result = await provider._fetch_candle_events(
                    "$SPX", "1d", datetime(2024, 1, 1, tzinfo=UTC),
                    timeout_seconds=1,
                )

        assert result == []

    @pytest.mark.asyncio
    async def test_httpx_connect_timeout_returns_empty(self) -> None:
        """httpx.ConnectTimeout (non-asyncio) is caught and returns empty list."""
        import httpx

        provider = _make_provider()
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.DXLinkStreamer",
            side_effect=httpx.ConnectTimeout("connection timed out"),
        ):
            result = await provider._fetch_candle_events(
                "$SPX", "1d", datetime(2024, 1, 1, tzinfo=UTC),
                timeout_seconds=1,
            )

        assert result == []

    @pytest.mark.asyncio
    async def test_generic_exception_returns_empty(self) -> None:
        """Any unexpected exception is caught and returns empty list."""
        provider = _make_provider()
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.DXLinkStreamer",
            side_effect=RuntimeError("something broke"),
        ):
            result = await provider._fetch_candle_events(
                "$SPX", "1d", datetime(2024, 1, 1, tzinfo=UTC),
                timeout_seconds=1,
            )

        assert result == []


# ---------------------------------------------------------------------------
# Helpers for latest-candle tests
# ---------------------------------------------------------------------------


def _make_market_data(**overrides: object) -> MagicMock:
    """Create a mock TastyTrade MarketData REST response with realistic defaults."""
    defaults: dict[str, object] = {
        "open": Decimal("5500.00"),
        "day_high_price": Decimal("5520.00"),
        "day_low_price": Decimal("5480.00"),
        "last": Decimal("5510.00"),
        "volume": Decimal("1000000"),
        "summary_date": date(2026, 3, 14),
        "updated_at": datetime(2026, 3, 14, 18, 30, tzinfo=UTC),
        # Fallback fields (may be None on some instruments)
        "day_high": None,
        "day_low": None,
    }
    defaults.update(overrides)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


def _make_provider_with_latest(
    include_latest: bool = True,
) -> TastyTradeMarketDataProvider:
    """Create a provider with include_latest_candle flag set."""
    session = MagicMock()
    session.session = MagicMock()
    session.include_latest_candle = include_latest
    session.use_dxlink_candles = True
    return TastyTradeMarketDataProvider(session)


def _make_historical_series(
    last_date: date = date(2026, 3, 13),
    n: int = 3,
) -> CandleSeries:
    """Create a CandleSeries with n bars ending on last_date."""
    bars = []
    for i in range(n):
        day = date(
            last_date.year, last_date.month, last_date.day - (n - 1 - i)
        )
        bars.append(
            CandleBar(
                symbol="SPY",
                timestamp=datetime(day.year, day.month, day.day, 16, 0, tzinfo=UTC),
                open=550.0 + i,
                high=555.0 + i,
                low=545.0 + i,
                close=552.0 + i,
                volume=1_000_000 + i,
            )
        )
    return CandleSeries(bars=bars)


# ---------------------------------------------------------------------------
# Tests for instrument_type_for_symbol
# ---------------------------------------------------------------------------


class TestInstrumentTypeForSymbol:
    """Tests for the symbol-to-InstrumentType classification helper."""

    def test_spx_is_index(self) -> None:
        assert instrument_type_for_symbol("SPX") == "INDEX"

    def test_dollar_spx_is_index(self) -> None:
        assert instrument_type_for_symbol("$SPX") == "INDEX"

    def test_vix_is_index(self) -> None:
        assert instrument_type_for_symbol("VIX") == "INDEX"

    def test_vix3m_is_index(self) -> None:
        assert instrument_type_for_symbol("VIX3M") == "INDEX"

    def test_ndx_is_index(self) -> None:
        assert instrument_type_for_symbol("NDX") == "INDEX"

    def test_rut_is_index(self) -> None:
        assert instrument_type_for_symbol("RUT") == "INDEX"

    def test_djx_is_index(self) -> None:
        assert instrument_type_for_symbol("DJX") == "INDEX"

    def test_spy_is_equity(self) -> None:
        assert instrument_type_for_symbol("SPY") == "EQUITY"

    def test_qqq_is_equity(self) -> None:
        assert instrument_type_for_symbol("QQQ") == "EQUITY"

    def test_aapl_is_equity(self) -> None:
        assert instrument_type_for_symbol("AAPL") == "EQUITY"

    def test_tlt_is_equity(self) -> None:
        assert instrument_type_for_symbol("TLT") == "EQUITY"


# ---------------------------------------------------------------------------
# Tests for map_market_data_to_bar
# ---------------------------------------------------------------------------


class TestMapMarketDataToBar:
    """Tests for mapping REST MarketData to CandleBar."""

    def test_maps_all_ohlcv_fields(self) -> None:
        data = _make_market_data()
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is not None
        assert bar.open == 5500.0
        assert bar.high == 5520.0
        assert bar.low == 5480.0
        assert bar.close == 5510.0
        assert bar.volume == 1_000_000

    def test_symbol_passthrough(self) -> None:
        data = _make_market_data()
        bar = map_market_data_to_bar(data, "QQQ")
        assert bar is not None
        assert bar.symbol == "QQQ"

    def test_timestamp_uses_summary_date(self) -> None:
        data = _make_market_data(summary_date=date(2026, 3, 14))
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is not None
        assert bar.timestamp.date() == date(2026, 3, 14)

    def test_returns_none_when_open_is_none(self) -> None:
        data = _make_market_data(open=None)
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is None

    def test_returns_none_when_last_is_none(self) -> None:
        data = _make_market_data(last=None)
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is None

    def test_falls_back_to_day_high_when_day_high_price_is_none(self) -> None:
        data = _make_market_data(
            day_high_price=None, day_high=Decimal("5525.00")
        )
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is not None
        assert bar.high == 5525.0

    def test_falls_back_to_day_low_when_day_low_price_is_none(self) -> None:
        data = _make_market_data(
            day_low_price=None, day_low=Decimal("5475.00")
        )
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is not None
        assert bar.low == 5475.0

    def test_high_defaults_to_open_when_both_none(self) -> None:
        data = _make_market_data(
            day_high_price=None, day_high=None, open=Decimal("5500.00")
        )
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is not None
        assert bar.high == 5500.0

    def test_low_defaults_to_open_when_both_none(self) -> None:
        data = _make_market_data(
            day_low_price=None, day_low=None, open=Decimal("5500.00")
        )
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is not None
        assert bar.low == 5500.0

    def test_zero_volume_when_none(self) -> None:
        data = _make_market_data(volume=None)
        bar = map_market_data_to_bar(data, "SPY")
        assert bar is not None
        assert bar.volume == 0


# ---------------------------------------------------------------------------
# Tests for _fetch_latest_bar
# ---------------------------------------------------------------------------


class TestFetchLatestBar:
    """Tests for the _fetch_latest_bar private method."""

    @pytest.mark.asyncio
    async def test_equity_uses_get_market_data(self) -> None:
        provider = _make_provider_with_latest()
        mock_data = _make_market_data()
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_market_data",
            new_callable=AsyncMock,
            return_value=mock_data,
        ) as mock_get:
            bar = await provider._fetch_latest_bar("SPY")

        mock_get.assert_awaited_once()
        assert bar is not None
        assert bar.symbol == "SPY"

    @pytest.mark.asyncio
    async def test_index_uses_get_market_data_by_type(self) -> None:
        provider = _make_provider_with_latest()
        mock_data = _make_market_data()
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_market_data_by_type",
            new_callable=AsyncMock,
            return_value=[mock_data],
        ) as mock_get_by_type:
            bar = await provider._fetch_latest_bar("SPX")

        mock_get_by_type.assert_awaited_once()
        call_kwargs = mock_get_by_type.call_args[1]
        assert call_kwargs.get("indices") == ["SPX"]
        assert bar is not None

    @pytest.mark.asyncio
    async def test_strips_dollar_prefix(self) -> None:
        provider = _make_provider_with_latest()
        mock_data = _make_market_data()
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_market_data_by_type",
            new_callable=AsyncMock,
            return_value=[mock_data],
        ) as mock_get_by_type:
            bar = await provider._fetch_latest_bar("$SPX")

        call_kwargs = mock_get_by_type.call_args[1]
        assert call_kwargs.get("indices") == ["SPX"]
        assert bar is not None
        assert bar.symbol == "SPX"

    @pytest.mark.asyncio
    async def test_returns_none_on_exception(self) -> None:
        provider = _make_provider_with_latest()
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_market_data",
            new_callable=AsyncMock,
            side_effect=RuntimeError("API error"),
        ):
            bar = await provider._fetch_latest_bar("SPY")

        assert bar is None

    @pytest.mark.asyncio
    async def test_returns_none_when_index_returns_empty_list(self) -> None:
        provider = _make_provider_with_latest()
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_market_data_by_type",
            new_callable=AsyncMock,
            return_value=[],
        ):
            bar = await provider._fetch_latest_bar("SPX")

        assert bar is None


# ---------------------------------------------------------------------------
# Tests for _append_latest_bar
# ---------------------------------------------------------------------------


class TestAppendLatestBar:
    """Tests for the _append_latest_bar deduplication logic."""

    @pytest.mark.asyncio
    async def test_appends_when_dates_differ(self) -> None:
        provider = _make_provider_with_latest()
        series = _make_historical_series(last_date=date(2026, 3, 13), n=3)
        latest_bar = CandleBar(
            symbol="SPY",
            timestamp=datetime(2026, 3, 14, 16, 0, tzinfo=UTC),
            open=555.0, high=560.0, low=550.0, close=558.0, volume=2_000_000,
        )
        with patch.object(
            provider, "_fetch_latest_bar", new_callable=AsyncMock,
            return_value=latest_bar,
        ):
            result = await provider._append_latest_bar(series, "SPY")

        assert len(result.bars) == 4
        assert result.bars[-1].close == 558.0

    @pytest.mark.asyncio
    async def test_replaces_when_same_date(self) -> None:
        series = _make_historical_series(last_date=date(2026, 3, 14), n=3)
        provider = _make_provider_with_latest()
        latest_bar = CandleBar(
            symbol="SPY",
            timestamp=datetime(2026, 3, 14, 16, 0, tzinfo=UTC),
            open=555.0, high=565.0, low=548.0, close=560.0, volume=3_000_000,
        )
        with patch.object(
            provider, "_fetch_latest_bar", new_callable=AsyncMock,
            return_value=latest_bar,
        ):
            result = await provider._append_latest_bar(series, "SPY")

        assert len(result.bars) == 3  # same count — replaced, not appended
        assert result.bars[-1].close == 560.0

    @pytest.mark.asyncio
    async def test_returns_original_when_fetch_fails(self) -> None:
        provider = _make_provider_with_latest()
        series = _make_historical_series(n=3)
        with patch.object(
            provider, "_fetch_latest_bar", new_callable=AsyncMock,
            return_value=None,
        ):
            result = await provider._append_latest_bar(series, "SPY")

        assert len(result.bars) == 3
        assert result.bars[-1].close == series.bars[-1].close

    @pytest.mark.asyncio
    async def test_handles_empty_series(self) -> None:
        provider = _make_provider_with_latest()
        series = CandleSeries(bars=[])
        latest_bar = CandleBar(
            symbol="SPY",
            timestamp=datetime(2026, 3, 14, 16, 0, tzinfo=UTC),
            open=555.0, high=560.0, low=550.0, close=558.0, volume=2_000_000,
        )
        with patch.object(
            provider, "_fetch_latest_bar", new_callable=AsyncMock,
            return_value=latest_bar,
        ):
            result = await provider._append_latest_bar(series, "SPY")

        assert len(result.bars) == 1
        assert result.bars[0].close == 558.0


# ---------------------------------------------------------------------------
# Tests for get_candles with include_latest_candle
# ---------------------------------------------------------------------------


class TestGetCandlesWithLatestCandle:
    """Tests for the include_latest_candle integration in get_candles."""

    @pytest.mark.asyncio
    async def test_appends_latest_when_enabled_and_daily(self) -> None:
        provider = _make_provider_with_latest(include_latest=True)
        events = _candle_events(3)
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock,
                return_value=events,
            ),
            patch.object(
                provider, "_append_latest_bar", new_callable=AsyncMock,
            ) as mock_append,
        ):
            mock_append.return_value = CandleSeries(bars=[])
            await provider.get_candles("SPX", interval="1d", days_back=30)

        mock_append.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_latest_when_disabled(self) -> None:
        provider = _make_provider_with_latest(include_latest=False)
        events = _candle_events(3)
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock,
                return_value=events,
            ),
            patch.object(
                provider, "_append_latest_bar", new_callable=AsyncMock,
            ) as mock_append,
        ):
            await provider.get_candles("SPX", interval="1d", days_back=30)

        mock_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_skips_latest_for_non_daily_interval(self) -> None:
        provider = _make_provider_with_latest(include_latest=True)
        events = _candle_events(3)
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock,
                return_value=events,
            ),
            patch.object(
                provider, "_append_latest_bar", new_callable=AsyncMock,
            ) as mock_append,
        ):
            await provider.get_candles("SPX", interval="1h", days_back=30)

        mock_append.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_appends_latest_to_yfinance_fallback(self) -> None:
        provider = _make_provider_with_latest(include_latest=True)
        mock_series = _make_historical_series(n=3)
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "options_analyzer.adapters.yfinance_candles.fetch_candles_yfinance",
                new_callable=AsyncMock,
                return_value=mock_series,
            ),
            patch.object(
                provider, "_append_latest_bar", new_callable=AsyncMock,
            ) as mock_append,
        ):
            mock_append.return_value = mock_series
            await provider.get_candles("SPX", interval="1d", days_back=30)

        mock_append.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_include_latest_defaults_to_false(self) -> None:
        """When session lacks include_latest_candle attr, defaults to False."""
        session = MagicMock(spec=[])
        session.session = MagicMock()
        session.use_dxlink_candles = True
        provider = TastyTradeMarketDataProvider(session)
        events = _candle_events(3)
        with (
            patch.object(
                provider, "_fetch_candle_events", new_callable=AsyncMock,
                return_value=events,
            ),
            patch.object(
                provider, "_append_latest_bar", new_callable=AsyncMock,
            ) as mock_append,
        ):
            await provider.get_candles("SPX", interval="1d", days_back=30)

        mock_append.assert_not_awaited()


# ---------------------------------------------------------------------------
# Tests for get_candles_batch
# ---------------------------------------------------------------------------


def _make_series_for_symbol(
    symbol: str, days: list[int],
) -> CandleSeries:
    """Create a CandleSeries with bars on specific days of June 2024."""
    bars = [
        CandleBar(
            symbol=symbol,
            timestamp=datetime(2024, 6, d, 16, 0, tzinfo=UTC),
            open=100.0,
            high=110.0,
            low=90.0,
            close=100.0 + d,
            volume=1000 * d,
        )
        for d in days
    ]
    return CandleSeries(bars=bars)


class TestGetCandlesBatch:
    """Tests for get_candles_batch with alignment."""

    @pytest.mark.asyncio
    async def test_different_length_series_are_aligned(self) -> None:
        """Series with different trading calendars get aligned to common dates."""
        provider = _make_provider()
        # VIX has an extra day (day 6), VIX3M does not
        vix_series = _make_series_for_symbol("VIX", [1, 2, 3, 4, 5, 6])
        vix3m_series = _make_series_for_symbol("VIX3M", [1, 2, 3, 4, 5])

        async def mock_get_candles(
            symbol: str, interval: str = "1d", days_back: int = 365,
        ) -> CandleSeries:
            return {"VIX": vix_series, "VIX3M": vix3m_series}[symbol]

        with patch.object(provider, "get_candles", side_effect=mock_get_candles):
            result = await provider.get_candles_batch(
                ["VIX", "VIX3M"], interval="1d", days_back=365,
            )

        assert len(result) == 2
        assert len(result["VIX"]) == 5
        assert len(result["VIX3M"]) == 5
        assert result["VIX"].timestamps == result["VIX3M"].timestamps

    @pytest.mark.asyncio
    async def test_failed_symbols_excluded_with_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """Symbols that fail to fetch are excluded from the result."""
        provider = _make_provider()
        spy_series = _make_series_for_symbol("SPY", [1, 2, 3])

        async def mock_get_candles(
            symbol: str, interval: str = "1d", days_back: int = 365,
        ) -> CandleSeries:
            if symbol == "BAD":
                raise RuntimeError("API error")
            return spy_series

        with patch.object(provider, "get_candles", side_effect=mock_get_candles):
            import logging
            with caplog.at_level(logging.WARNING):
                result = await provider.get_candles_batch(
                    ["SPY", "BAD"], interval="1d", days_back=365,
                )

        assert "BAD" not in result
        assert "SPY" in result
        assert "BAD" in caplog.text

    @pytest.mark.asyncio
    async def test_single_symbol_returns_unmodified(self) -> None:
        """A single symbol should be returned without alignment issues."""
        provider = _make_provider()
        spy_series = _make_series_for_symbol("SPY", [1, 2, 3])

        async def mock_get_candles(
            symbol: str, interval: str = "1d", days_back: int = 365,
        ) -> CandleSeries:
            return spy_series

        with patch.object(provider, "get_candles", side_effect=mock_get_candles):
            result = await provider.get_candles_batch(
                ["SPY"], interval="1d", days_back=365,
            )

        assert len(result["SPY"]) == 3

    @pytest.mark.asyncio
    async def test_all_symbols_fetched_concurrently(self) -> None:
        """All symbols should be fetched (verifies get_candles called for each)."""
        provider = _make_provider()
        symbols = ["SPY", "QQQ", "VIX"]
        series_map = {s: _make_series_for_symbol(s, [1, 2, 3]) for s in symbols}

        async def mock_get_candles(
            symbol: str, interval: str = "1d", days_back: int = 365,
        ) -> CandleSeries:
            return series_map[symbol]

        with patch.object(provider, "get_candles", side_effect=mock_get_candles) as mock:
            result = await provider.get_candles_batch(symbols, interval="1d", days_back=30)

        assert mock.call_count == 3
        assert set(result.keys()) == set(symbols)
