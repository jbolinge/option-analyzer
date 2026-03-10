"""Tests for CandleBar and CandleSeries domain models."""

from datetime import UTC, datetime

import numpy as np

from options_analyzer.domain.candles import CandleBar, CandleSeries


class TestCandleBar:
    """Tests for CandleBar frozen model."""

    def setup_method(self) -> None:
        self.bar = CandleBar(
            symbol="SPX",
            timestamp=datetime(2024, 6, 15, 16, 0, tzinfo=UTC),
            open=5500.0,
            high=5520.0,
            low=5480.0,
            close=5510.0,
            volume=1_000_000,
        )

    def test_fields_stored(self) -> None:
        assert self.bar.symbol == "SPX"
        assert self.bar.open == 5500.0
        assert self.bar.high == 5520.0
        assert self.bar.low == 5480.0
        assert self.bar.close == 5510.0
        assert self.bar.volume == 1_000_000

    def test_timestamp_stored(self) -> None:
        assert self.bar.timestamp == datetime(2024, 6, 15, 16, 0, tzinfo=UTC)

    def test_immutable(self) -> None:
        import pytest

        with pytest.raises(Exception):  # noqa: B017
            self.bar.close = 9999.0  # type: ignore[misc]


class TestCandleSeries:
    """Tests for CandleSeries frozen model with numpy accessors."""

    def setup_method(self) -> None:
        self.bars = [
            CandleBar(
                symbol="SPX",
                timestamp=datetime(2024, 6, i, 16, 0, tzinfo=UTC),
                open=5500.0 + i,
                high=5520.0 + i,
                low=5480.0 + i,
                close=5510.0 + i,
                volume=1_000_000 + i * 100,
            )
            for i in range(1, 4)
        ]
        self.series = CandleSeries(bars=self.bars)

    def test_length(self) -> None:
        assert len(self.series) == 3

    def test_closes_dtype(self) -> None:
        assert self.series.closes.dtype == np.float64

    def test_closes_values(self) -> None:
        np.testing.assert_array_equal(
            self.series.closes, [5511.0, 5512.0, 5513.0]
        )

    def test_opens_values(self) -> None:
        np.testing.assert_array_equal(
            self.series.opens, [5501.0, 5502.0, 5503.0]
        )

    def test_highs_values(self) -> None:
        np.testing.assert_array_equal(
            self.series.highs, [5521.0, 5522.0, 5523.0]
        )

    def test_lows_values(self) -> None:
        np.testing.assert_array_equal(
            self.series.lows, [5481.0, 5482.0, 5483.0]
        )

    def test_volumes_values(self) -> None:
        np.testing.assert_array_equal(
            self.series.volumes, [1_000_100, 1_000_200, 1_000_300]
        )

    def test_timestamps_values(self) -> None:
        ts = self.series.timestamps
        assert len(ts) == 3
        assert ts[0] == datetime(2024, 6, 1, 16, 0, tzinfo=UTC)

    def test_immutable(self) -> None:
        import pytest

        with pytest.raises(Exception):  # noqa: B017
            self.series.bars = []  # type: ignore[misc]

    def test_empty_series(self) -> None:
        empty = CandleSeries(bars=[])
        assert len(empty) == 0
        assert len(empty.closes) == 0
        assert len(empty.timestamps) == 0
