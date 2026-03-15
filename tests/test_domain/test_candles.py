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


class TestAlignSeries:
    """Tests for align_series timestamp-based intersection alignment."""

    @staticmethod
    def _make_series(
        symbol: str, days: list[int], base_close: float = 100.0
    ) -> CandleSeries:
        """Helper: create a CandleSeries with bars on specific days of June 2024."""
        bars = [
            CandleBar(
                symbol=symbol,
                timestamp=datetime(2024, 6, d, 16, 0, tzinfo=UTC),
                open=base_close,
                high=base_close + 10,
                low=base_close - 10,
                close=base_close + d,
                volume=1000 * d,
            )
            for d in days
        ]
        return CandleSeries(bars=bars)

    def test_overlapping_timestamps_aligned_to_intersection(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = self._make_series("A", [1, 2, 3, 4, 5])
        s2 = self._make_series("B", [2, 3, 4, 5, 6])
        a1, a2 = align_series(s1, s2)

        assert len(a1) == 4  # days 2,3,4,5
        assert len(a2) == 4
        assert a1.timestamps == a2.timestamps

    def test_already_aligned_unchanged(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = self._make_series("A", [1, 2, 3])
        s2 = self._make_series("B", [1, 2, 3])
        a1, a2 = align_series(s1, s2)

        assert len(a1) == 3
        assert len(a2) == 3
        # Fast path: should return same objects
        assert a1 is s1
        assert a2 is s2

    def test_three_series_intersection(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = self._make_series("A", [1, 2, 3, 4, 5])
        s2 = self._make_series("B", [2, 3, 4, 5, 6])
        s3 = self._make_series("C", [3, 4, 5, 6, 7])
        a1, a2, a3 = align_series(s1, s2, s3)

        assert len(a1) == 3  # days 3,4,5
        assert len(a2) == 3
        assert len(a3) == 3
        assert a1.timestamps == a2.timestamps == a3.timestamps

    def test_empty_intersection_returns_empty(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = self._make_series("A", [1, 2, 3])
        s2 = self._make_series("B", [4, 5, 6])
        a1, a2 = align_series(s1, s2)

        assert len(a1) == 0
        assert len(a2) == 0

    def test_single_series_returns_unchanged(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = self._make_series("A", [1, 2, 3])
        (a1,) = align_series(s1)

        assert a1 is s1

    def test_preserves_bar_data(self) -> None:
        """Aligned bars retain their original OHLCV data."""
        from options_analyzer.domain.candles import align_series

        s1 = self._make_series("A", [1, 2, 3, 4], base_close=100.0)
        s2 = self._make_series("B", [2, 3], base_close=200.0)
        a1, a2 = align_series(s1, s2)

        # s1 filtered to days 2,3 — close = 100 + day
        np.testing.assert_array_equal(a1.closes, [102.0, 103.0])
        # s2 unchanged — close = 200 + day
        np.testing.assert_array_equal(a2.closes, [202.0, 203.0])

    def test_preserves_chronological_order(self) -> None:
        from options_analyzer.domain.candles import align_series

        s1 = self._make_series("A", [5, 3, 1, 4, 2])  # unsorted input
        s2 = self._make_series("B", [2, 4])
        a1, a2 = align_series(s1, s2)

        ts1 = a1.timestamps
        assert ts1 == sorted(ts1)
