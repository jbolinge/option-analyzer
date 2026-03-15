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


def _make_series(
    symbol: str, days: list[int], base_close: float = 100.0,
    hour: int = 16,
) -> CandleSeries:
    """Helper: create a CandleSeries with bars on specific days of June 2024."""
    bars = [
        CandleBar(
            symbol=symbol,
            timestamp=datetime(2024, 6, d, hour, 0, tzinfo=UTC),
            open=base_close,
            high=base_close + 10,
            low=base_close - 10,
            close=base_close + d,
            volume=1000 * d,
        )
        for d in days
    ]
    return CandleSeries(bars=bars)


class TestAlignSeriesIntersect:
    """Tests for align_series with method='intersect'."""

    def test_overlapping_timestamps_aligned_to_intersection(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3, 4, 5])
        s2 = _make_series("B", [2, 3, 4, 5, 6])
        a1, a2 = align_series(s1, s2, method="intersect")

        assert len(a1) == 4  # days 2,3,4,5
        assert len(a2) == 4
        assert a1.timestamps == a2.timestamps

    def test_already_aligned_unchanged(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3])
        s2 = _make_series("B", [1, 2, 3])
        a1, a2 = align_series(s1, s2, method="intersect")

        assert len(a1) == 3
        assert len(a2) == 3
        # Fast path: should return same objects
        assert a1 is s1
        assert a2 is s2

    def test_three_series_intersection(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3, 4, 5])
        s2 = _make_series("B", [2, 3, 4, 5, 6])
        s3 = _make_series("C", [3, 4, 5, 6, 7])
        a1, a2, a3 = align_series(s1, s2, s3, method="intersect")

        assert len(a1) == 3  # days 3,4,5
        assert len(a2) == 3
        assert len(a3) == 3
        assert a1.timestamps == a2.timestamps == a3.timestamps

    def test_empty_intersection_returns_empty(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3])
        s2 = _make_series("B", [4, 5, 6])
        a1, a2 = align_series(s1, s2, method="intersect")

        assert len(a1) == 0
        assert len(a2) == 0

    def test_single_series_returns_unchanged(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3])
        (a1,) = align_series(s1, method="intersect")

        assert a1 is s1

    def test_preserves_bar_data(self) -> None:
        """Aligned bars retain their original OHLCV data."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3, 4], base_close=100.0)
        s2 = _make_series("B", [2, 3], base_close=200.0)
        a1, a2 = align_series(s1, s2, method="intersect")

        # s1 filtered to days 2,3 — close = 100 + day
        np.testing.assert_array_equal(a1.closes, [102.0, 103.0])
        # s2 unchanged — close = 200 + day
        np.testing.assert_array_equal(a2.closes, [202.0, 203.0])

    def test_preserves_chronological_order(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [5, 3, 1, 4, 2])  # unsorted input
        s2 = _make_series("B", [2, 4])
        a1, a2 = align_series(s1, s2, method="intersect")

        ts1 = a1.timestamps
        assert ts1 == sorted(ts1)


class TestAlignSeriesFfill:
    """Tests for align_series with method='ffill' (default)."""

    def test_ffill_is_default(self) -> None:
        """Default method produces union-length results, not intersection."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3, 4, 5])
        s2 = _make_series("B", [2, 3, 4, 5, 6])
        a1, a2 = align_series(s1, s2)

        # s1 gets day 6 filled; s2 has no data before day 2 so skips day 1
        assert len(a1) == 6  # days 1-6
        assert len(a2) == 5  # days 2-6 (no data before day 2)

    def test_forward_fills_missing_bar_with_prev_close(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3])
        s2 = _make_series("B", [1, 3])  # missing day 2
        a1, a2 = align_series(s1, s2, method="ffill")

        assert len(a2) == 3
        # Day 2 should be filled from day 1's close (100 + 1 = 101)
        filled_bar = a2.bars[1]
        # Timestamps normalized to midnight by _align_ffill
        assert filled_bar.timestamp == datetime(2024, 6, 2, 0, 0, tzinfo=UTC)
        assert filled_bar.open == 101.0
        assert filled_bar.high == 101.0
        assert filled_bar.low == 101.0
        assert filled_bar.close == 101.0
        assert filled_bar.volume == 0

    def test_latest_timestamp_preserved(self) -> None:
        """Even if one series is shorter, the latest timestamp is kept."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3, 4, 5, 6])
        s2 = _make_series("B", [1, 2, 3, 4, 5])  # missing day 6
        a1, a2 = align_series(s1, s2, method="ffill")

        assert len(a1) == 6
        assert len(a2) == 6
        assert a1.timestamps == a2.timestamps
        # Day 6 in s2 filled from day 5 close (timestamps normalized to midnight)
        assert a2.bars[-1].timestamp == datetime(2024, 6, 6, 0, 0, tzinfo=UTC)
        assert a2.bars[-1].close == 105.0  # 100 + 5
        assert a2.bars[-1].volume == 0

    def test_no_fabrication_before_series_start(self) -> None:
        """Series with later start doesn't get synthetic bars before its first bar."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3, 4, 5])
        s2 = _make_series("B", [3, 4, 5])  # starts at day 3
        a1, a2 = align_series(s1, s2, method="ffill")

        assert len(a1) == 5
        # s2 has no data before day 3, so only days 3,4,5
        assert len(a2) == 3
        # Timestamps normalized to midnight by _align_ffill
        assert a2.bars[0].timestamp == datetime(2024, 6, 3, 0, 0, tzinfo=UTC)

    def test_already_aligned_returns_unchanged(self) -> None:
        """Fast path: identical timestamps returns same objects."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3])
        s2 = _make_series("B", [1, 2, 3])
        a1, a2 = align_series(s1, s2, method="ffill")

        assert a1 is s1
        assert a2 is s2

    def test_original_bars_preserved(self) -> None:
        """Non-filled bars retain their original OHLCV data."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3], base_close=100.0)
        s2 = _make_series("B", [1, 3], base_close=200.0)
        a1, a2 = align_series(s1, s2, method="ffill")

        # s1 unchanged
        np.testing.assert_array_equal(a1.closes, [101.0, 102.0, 103.0])
        # s2: day1=original, day2=filled, day3=original
        assert a2.bars[0].close == 201.0
        assert a2.bars[1].close == 201.0  # filled from day 1
        assert a2.bars[2].close == 203.0  # original

    def test_symbol_preserved_in_filled_bars(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("VIX", [1, 2, 3])
        s2 = _make_series("VIX3M", [1, 3])
        _, a2 = align_series(s1, s2, method="ffill")

        assert a2.bars[1].symbol == "VIX3M"


class TestAlignSeriesMixedTimes:
    """Tests for alignment when series have same dates but different time components."""

    def test_ffill_no_duplicate_day_with_different_times(self) -> None:
        """Same dates at midnight vs 16:00 should produce one bar per day, not two."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3], hour=0)   # midnight
        s2 = _make_series("B", [1, 2, 3], hour=16)   # 16:00
        a1, a2 = align_series(s1, s2, method="ffill")

        assert len(a1) == 3
        assert len(a2) == 3
        assert a1.timestamps == a2.timestamps

    def test_different_times_same_dates_normalized(self) -> None:
        """Series with same dates but different times get normalized, not duplicated."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3], hour=0)
        s2 = _make_series("B", [1, 2, 3], hour=16)
        a1, a2 = align_series(s1, s2, method="ffill")

        # All timestamps normalized to midnight
        for bar in a1.bars:
            assert bar.timestamp.hour == 0
        for bar in a2.bars:
            assert bar.timestamp.hour == 0

    def test_mixed_times_preserves_bar_data(self) -> None:
        """Bars with different times on same day retain original OHLCV data."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3], base_close=100.0, hour=0)
        s2 = _make_series("B", [1, 3], base_close=200.0, hour=16)
        a1, a2 = align_series(s1, s2, method="ffill")

        assert len(a1) == 3
        assert len(a2) == 3
        # Original close values preserved
        np.testing.assert_array_equal(a1.closes, [101.0, 102.0, 103.0])
        assert a2.bars[0].close == 201.0
        assert a2.bars[1].close == 201.0  # filled from day 1
        assert a2.bars[2].close == 203.0  # original

    def test_timestamps_normalized_to_midnight(self) -> None:
        """After ffill alignment, all timestamps have midnight time component."""
        from options_analyzer.domain.candles import align_series

        s1 = _make_series("A", [1, 2, 3], hour=0)
        s2 = _make_series("B", [1, 3], hour=16)
        a1, a2 = align_series(s1, s2, method="ffill")

        for bar in a2.bars:
            assert bar.timestamp.hour == 0
            assert bar.timestamp.minute == 0
