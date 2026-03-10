"""Tests for DSTFS indicator chart functions."""

import plotly.graph_objects as go

from options_analyzer.engine.indicators import compute_dstfs
from options_analyzer.visualization.indicator_charts import (
    _bias_color,
    plot_dstfs,
    plot_dstfs_candlestick,
)
from options_analyzer.visualization.theme import BLOOMBERG_TEMPLATE, DSTFS_PALETTE
from tests.factories import make_candle_series


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
