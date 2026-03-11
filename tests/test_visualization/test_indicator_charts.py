"""Tests for DSTFS indicator chart functions."""

import datetime as dt

import plotly.graph_objects as go

from options_analyzer.engine.indicators import compute_dstfs
import numpy as np

from options_analyzer.visualization.indicator_charts import (
    _add_colored_line,
    _bias_color,
    _compute_rangebreaks,
    plot_dstfs,
    plot_dstfs_candlestick,
)
from options_analyzer.visualization.theme import BLOOMBERG_TEMPLATE, DSTFS_PALETTE
from tests.factories import make_candle_series


def _make_trading_timestamps(n: int, start: dt.date | None = None) -> list[dt.datetime]:
    """Generate *n* weekday-only datetime timestamps starting from *start*."""
    d = start or dt.date(2025, 1, 6)  # a Monday
    result: list[dt.datetime] = []
    while len(result) < n:
        if d.weekday() < 5:
            result.append(dt.datetime(d.year, d.month, d.day, 16, 0))
        d += dt.timedelta(days=1)
    return result


class TestAddColoredLine:
    """Tests for _add_colored_line color-segmentation logic."""

    def _get_traces(
        self,
        y: list[float],
        is_rising: list[float],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Run _add_colored_line and return (rising_y, falling_y) from traces."""
        from plotly.subplots import make_subplots

        fig = make_subplots(rows=1, cols=1)
        _add_colored_line(
            fig,
            x=list(range(len(y))),
            y=np.array(y, dtype=np.float64),
            is_rising=np.array(is_rising, dtype=np.float64),
            rising_color="#00ff00",
            falling_color="#ff0000",
            rising_name="Rising",
            falling_name="Falling",
            row=1,
            col=1,
        )
        rising_y = np.array(fig.data[0].y, dtype=np.float64)
        falling_y = np.array(fig.data[1].y, dtype=np.float64)
        return rising_y, falling_y

    def test_multiple_transitions_no_cascade(self) -> None:
        """Segments should alternate — not cascade to fill all with one color."""
        #              R    R    F    F    R
        y = [10.0, 11.0, 9.0, 8.0, 12.0]
        is_rising = [1.0, 1.0, -1.0, -1.0, 1.0]
        rising_y, falling_y = self._get_traces(y, is_rising)

        # Indices 0,1 are rising
        assert rising_y[0] == 10.0
        assert rising_y[1] == 11.0
        # Index 2 is a bridge ON rising (rising→falling), but index 3 must NOT be rising
        assert rising_y[2] == 9.0  # bridge point
        assert np.isnan(rising_y[3])  # must remain NaN — no cascade
        # Index 4 is rising again
        assert rising_y[4] == 12.0

        # Indices 2,3 are falling
        assert falling_y[2] == 9.0
        assert falling_y[3] == 8.0
        # Index 4 is a bridge ON falling (falling→rising), but index 0,1 must NOT be falling
        assert falling_y[4] == 12.0  # bridge point
        assert np.isnan(falling_y[0])
        assert np.isnan(falling_y[1])

    def test_all_rising(self) -> None:
        """All-rising data should have no falling values."""
        y = [1.0, 2.0, 3.0, 4.0]
        is_rising = [1.0, 1.0, 1.0, 1.0]
        rising_y, falling_y = self._get_traces(y, is_rising)

        np.testing.assert_array_equal(rising_y, y)
        assert all(np.isnan(falling_y))

    def test_all_falling(self) -> None:
        """All-falling data should have no rising values."""
        y = [4.0, 3.0, 2.0, 1.0]
        is_rising = [-1.0, -1.0, -1.0, -1.0]
        rising_y, falling_y = self._get_traces(y, is_rising)

        assert all(np.isnan(rising_y))
        np.testing.assert_array_equal(falling_y, y)

    def test_many_transitions(self) -> None:
        """Rapid alternation should produce distinct segments, not fill one color."""
        #              R    F    R    F    R    F
        y = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        is_rising = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
        rising_y, falling_y = self._get_traces(y, is_rising)

        # Core rising points (indices 0, 2, 4) must have values
        assert rising_y[0] == 1.0
        assert rising_y[2] == 3.0
        assert rising_y[4] == 5.0
        # Core falling points (indices 1, 3, 5) must have values
        assert falling_y[1] == 2.0
        assert falling_y[3] == 4.0
        assert falling_y[5] == 6.0


class TestBiasColor:
    """Tests for _bias_color helper."""

    def test_maps_positive_four(self) -> None:
        assert _bias_color(4) == DSTFS_PALETTE["bias_4"]

    def test_maps_positive_two(self) -> None:
        assert _bias_color(2) == DSTFS_PALETTE["bias_2"]

    def test_maps_zero(self) -> None:
        assert _bias_color(0) == DSTFS_PALETTE["bias_0"]

    def test_maps_negative_two(self) -> None:
        assert _bias_color(-2) == DSTFS_PALETTE["bias_-2"]

    def test_maps_negative_four(self) -> None:
        assert _bias_color(-4) == DSTFS_PALETTE["bias_-4"]


class TestComputeRangebreaks:
    """Tests for _compute_rangebreaks helper."""

    def test_empty_input(self) -> None:
        assert _compute_rangebreaks([]) == []

    def test_integer_input(self) -> None:
        assert _compute_rangebreaks([0, 1, 2, 3]) == []

    def test_weekend_break_always_present(self) -> None:
        # Mon-Fri, no holidays
        ts = _make_trading_timestamps(5)
        breaks = _compute_rangebreaks(ts)
        assert {"bounds": ["sat", "mon"]} in breaks

    def test_no_false_holiday_for_normal_week(self) -> None:
        # A normal Mon-Fri week has no holiday gaps
        ts = _make_trading_timestamps(5)
        breaks = _compute_rangebreaks(ts)
        assert len(breaks) == 1  # only the weekend break

    def test_detects_holiday(self) -> None:
        # Create Mon, Tue, Thu, Fri — Wednesday is a holiday
        base = dt.date(2025, 1, 6)  # Monday
        ts = [
            dt.datetime(2025, 1, 6, 16, 0),
            dt.datetime(2025, 1, 7, 16, 0),
            dt.datetime(2025, 1, 9, 16, 0),   # skip Wed 1/8
            dt.datetime(2025, 1, 10, 16, 0),
        ]
        breaks = _compute_rangebreaks(ts)
        holiday_break = [b for b in breaks if "values" in b]
        assert len(holiday_break) == 1
        assert "2025-01-08" in holiday_break[0]["values"]

    def test_works_with_date_objects(self) -> None:
        dates = [dt.date(2025, 1, 6), dt.date(2025, 1, 7), dt.date(2025, 1, 8)]
        breaks = _compute_rangebreaks(dates)
        assert {"bounds": ["sat", "mon"]} in breaks


class TestPlotDSTFS:
    """Tests for plot_dstfs line chart."""

    def setup_method(self) -> None:
        self.series = make_candle_series(n=200, seed=42)
        self.result = compute_dstfs(self.series.closes)
        self.timestamps = list(range(200))

    def test_returns_figure(self) -> None:
        fig = plot_dstfs(self.result)
        assert isinstance(fig, go.Figure)

    def test_has_two_subplots(self) -> None:
        fig = plot_dstfs(self.result)
        # Two rows → yaxis and yaxis2
        assert fig.layout.yaxis2 is not None

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_dstfs(self.result)
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_has_scatter_traces(self) -> None:
        fig = plot_dstfs(self.result)
        scatter_traces = [t for t in fig.data if isinstance(t, go.Scatter)]
        assert len(scatter_traces) >= 3  # close + SMA segments + HMA segments

    def test_has_bar_trace_for_bias(self) -> None:
        fig = plot_dstfs(self.result)
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) >= 1

    def test_custom_title(self) -> None:
        fig = plot_dstfs(self.result, title="My DSTFS")
        assert fig.layout.title.text == "My DSTFS"  # type: ignore[union-attr]

    def test_with_timestamps(self) -> None:
        fig = plot_dstfs(self.result, timestamps=self.timestamps)
        assert isinstance(fig, go.Figure)

    def test_rangebreaks_with_datetime_timestamps(self) -> None:
        ts = _make_trading_timestamps(200)
        fig = plot_dstfs(self.result, timestamps=ts)
        assert fig.layout.xaxis.rangebreaks is not None
        assert len(fig.layout.xaxis.rangebreaks) >= 1

    def test_no_rangebreaks_with_integer_timestamps(self) -> None:
        fig = plot_dstfs(self.result, timestamps=list(range(200)))
        assert fig.layout.xaxis.rangebreaks is None or len(fig.layout.xaxis.rangebreaks) == 0

    def test_no_rangebreaks_without_timestamps(self) -> None:
        fig = plot_dstfs(self.result)
        assert fig.layout.xaxis.rangebreaks is None or len(fig.layout.xaxis.rangebreaks) == 0


class TestPlotDSTFSCandlestick:
    """Tests for plot_dstfs_candlestick chart."""

    def setup_method(self) -> None:
        self.series = make_candle_series(n=200, seed=42)
        self.result = compute_dstfs(self.series.closes)

    def test_returns_figure(self) -> None:
        fig = plot_dstfs_candlestick(
            self.result,
            opens=self.series.opens,
            highs=self.series.highs,
            lows=self.series.lows,
        )
        assert isinstance(fig, go.Figure)

    def test_has_candlestick_trace(self) -> None:
        fig = plot_dstfs_candlestick(
            self.result,
            opens=self.series.opens,
            highs=self.series.highs,
            lows=self.series.lows,
        )
        candle_traces = [t for t in fig.data if isinstance(t, go.Candlestick)]
        assert len(candle_traces) == 1

    def test_has_two_subplots(self) -> None:
        fig = plot_dstfs_candlestick(
            self.result,
            opens=self.series.opens,
            highs=self.series.highs,
            lows=self.series.lows,
        )
        assert fig.layout.yaxis2 is not None

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_dstfs_candlestick(
            self.result,
            opens=self.series.opens,
            highs=self.series.highs,
            lows=self.series.lows,
        )
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_has_bar_trace_for_bias(self) -> None:
        fig = plot_dstfs_candlestick(
            self.result,
            opens=self.series.opens,
            highs=self.series.highs,
            lows=self.series.lows,
        )
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) >= 1

    def test_yaxis_labels(self) -> None:
        fig = plot_dstfs_candlestick(
            self.result,
            opens=self.series.opens,
            highs=self.series.highs,
            lows=self.series.lows,
        )
        assert fig.layout.yaxis.title.text == "Price"  # type: ignore[union-attr]
        assert fig.layout.yaxis2.title.text == "Bias"  # type: ignore[union-attr]

    def test_rangebreaks_with_datetime_timestamps(self) -> None:
        ts = _make_trading_timestamps(200)
        fig = plot_dstfs_candlestick(
            self.result,
            opens=self.series.opens,
            highs=self.series.highs,
            lows=self.series.lows,
            timestamps=ts,
        )
        assert fig.layout.xaxis.rangebreaks is not None
        assert len(fig.layout.xaxis.rangebreaks) >= 1

    def test_no_rangebreaks_without_timestamps(self) -> None:
        fig = plot_dstfs_candlestick(
            self.result,
            opens=self.series.opens,
            highs=self.series.highs,
            lows=self.series.lows,
        )
        assert fig.layout.xaxis.rangebreaks is None or len(fig.layout.xaxis.rangebreaks) == 0
