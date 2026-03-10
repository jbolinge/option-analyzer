"""Tests for candle fetching — mapping and adapter."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from options_analyzer.adapters.tastytrade.mapping import map_candle_to_bar


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
