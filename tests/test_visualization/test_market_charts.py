"""Tests for market indicator chart functions."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.engine.atr_bollinger import compute_atr_bollinger
from options_analyzer.engine.borg_transwarp import (
    BorgTranswarpResult,
    compute_borg_transwarp_series,
)
from options_analyzer.engine.ema_cloud import compute_ema_cloud
from options_analyzer.engine.force_index import compute_force_index_dual
from options_analyzer.engine.indicators import compute_dstfs
from options_analyzer.engine.ivts import IVTSResult, compute_ivts
from options_analyzer.engine.mc_warnings import compute_mc_warnings
from options_analyzer.engine.obv_bollinger import compute_obv_bollinger
from options_analyzer.visualization.market_charts import (
    plot_borg_transwarp,
    plot_dstfs_bias,
    plot_ema_cloud,
    plot_full_grid,
    plot_ivts,
    plot_mc_warnings_squares,
    plot_mc_warnings_totals,
)
from options_analyzer.visualization.theme import BLOOMBERG_TEMPLATE
from tests.factories import (
    make_multi_ticker_closes,
    make_ohlcv_arrays,
    make_vix_arrays,
)


def _make_test_data() -> dict:
    """Create all test data needed for chart functions."""
    data = make_ohlcv_arrays(n=200, seed=42)
    data2 = make_ohlcv_arrays(n=200, seed=99)
    vix, vix3m = make_vix_arrays(n=200, seed=42)

    dstfs = compute_dstfs(data["close"])
    ema_cloud = compute_ema_cloud(data["close"])
    atr = compute_atr_bollinger(data["high"], data["low"], data["close"])
    obv = compute_obv_bollinger(data["close"], data["volume"])
    ivts = compute_ivts(vix, vix3m)
    fi = compute_force_index_dual(
        data["close"], data["volume"],
        data2["close"], data2["volume"],
    )
    mc = compute_mc_warnings(atr, obv, ivts, fi, dstfs)

    closes = make_multi_ticker_closes(n=300, seed=42)
    borg = compute_borg_transwarp_series(closes)
    # Trim borg to match our 200-bar data
    borg = borg[-200:]

    return {
        "data": data,
        "dstfs": dstfs,
        "ema_cloud": ema_cloud,
        "ivts": ivts,
        "mc": mc,
        "borg": borg,
    }


class TestPlotDSTFSBias:
    def setup_method(self) -> None:
        self.td = _make_test_data()

    def test_returns_figure(self) -> None:
        fig = plot_dstfs_bias(self.td["dstfs"])
        assert isinstance(fig, go.Figure)

    def test_has_bar_trace(self) -> None:
        fig = plot_dstfs_bias(self.td["dstfs"])
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) >= 1

    def test_bloomberg_theme(self) -> None:
        fig = plot_dstfs_bias(self.td["dstfs"])
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_yaxis_right(self) -> None:
        fig = plot_dstfs_bias(self.td["dstfs"])
        assert fig.layout.yaxis.side == "right"

    def test_has_zero_reference_line(self) -> None:
        fig = plot_dstfs_bias(self.td["dstfs"])
        zero_lines = [
            s for s in fig.layout.shapes
            if s.y0 == 0 and s.y1 == 0
        ]
        assert len(zero_lines) >= 1

    def test_composable_with_fig_row(self) -> None:
        from plotly.subplots import make_subplots
        fig = make_subplots(rows=2, cols=1)
        result = plot_dstfs_bias(self.td["dstfs"], fig=fig, row=2, col=1)
        assert result is fig
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) >= 1


class TestPlotMCWarningsTotals:
    def setup_method(self) -> None:
        self.td = _make_test_data()

    def test_returns_figure(self) -> None:
        fig = plot_mc_warnings_totals(self.td["mc"])
        assert isinstance(fig, go.Figure)

    def test_has_bar_trace(self) -> None:
        fig = plot_mc_warnings_totals(self.td["mc"])
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) >= 1

    def test_bloomberg_theme(self) -> None:
        fig = plot_mc_warnings_totals(self.td["mc"])
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_yaxis_range(self) -> None:
        fig = plot_mc_warnings_totals(self.td["mc"])
        assert fig.layout.yaxis.range[1] == 5.5


class TestPlotIVTS:
    def setup_method(self) -> None:
        self.td = _make_test_data()

    def test_returns_figure(self) -> None:
        fig = plot_ivts(self.td["ivts"])
        assert isinstance(fig, go.Figure)

    def test_has_scatter_traces(self) -> None:
        fig = plot_ivts(self.td["ivts"])
        scatter_traces = [t for t in fig.data if isinstance(t, go.Scatter)]
        # 4-color line = 4 scatter traces
        assert len(scatter_traces) == 4

    def test_has_threshold_lines(self) -> None:
        fig = plot_ivts(self.td["ivts"])
        h_lines = [
            s for s in fig.layout.shapes
            if s.type == "line" and s.y0 in (0.9, 0.95, 1.0)
        ]
        assert len(h_lines) == 3

    def test_bloomberg_theme(self) -> None:
        fig = plot_ivts(self.td["ivts"])
        assert fig.layout.template == BLOOMBERG_TEMPLATE


class TestPlotBorgTranswarp:
    def setup_method(self) -> None:
        self.td = _make_test_data()

    def test_returns_figure(self) -> None:
        fig = plot_borg_transwarp(self.td["borg"])
        assert isinstance(fig, go.Figure)

    def test_has_bar_trace(self) -> None:
        fig = plot_borg_transwarp(self.td["borg"])
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        assert len(bar_traces) >= 1

    def test_yaxis_range(self) -> None:
        fig = plot_borg_transwarp(self.td["borg"])
        assert tuple(fig.layout.yaxis.range) == (-0.2, 1.15)

    def test_has_threshold_lines(self) -> None:
        fig = plot_borg_transwarp(self.td["borg"])
        h_lines = [
            s for s in fig.layout.shapes
            if s.type == "line" and s.y0 in (0.33, 0.66)
        ]
        assert len(h_lines) == 2

    def test_bloomberg_theme(self) -> None:
        fig = plot_borg_transwarp(self.td["borg"])
        assert fig.layout.template == BLOOMBERG_TEMPLATE


class TestPlotMCWarningsSquares:
    def setup_method(self) -> None:
        self.td = _make_test_data()

    def test_returns_figure(self) -> None:
        fig = plot_mc_warnings_squares(self.td["mc"])
        assert isinstance(fig, go.Figure)

    def test_has_scatter_markers(self) -> None:
        fig = plot_mc_warnings_squares(self.td["mc"])
        scatter_traces = [t for t in fig.data if isinstance(t, go.Scatter)]
        assert len(scatter_traces) >= 1
        # All should be marker mode
        for t in scatter_traces:
            assert "markers" in t.mode

    def test_yaxis_labels(self) -> None:
        fig = plot_mc_warnings_squares(self.td["mc"])
        assert fig.layout.yaxis.tickvals == (0, 1, 2, 3, 4)
        assert fig.layout.yaxis.ticktext == ("FI", "IVTS", "OBV", "ATR", "DSTFS")

    def test_with_dstfs_result(self) -> None:
        fig = plot_mc_warnings_squares(self.td["mc"], self.td["dstfs"])
        assert isinstance(fig, go.Figure)

    def test_bloomberg_theme(self) -> None:
        fig = plot_mc_warnings_squares(self.td["mc"])
        assert fig.layout.template == BLOOMBERG_TEMPLATE


class TestPlotEMACloud:
    def setup_method(self) -> None:
        self.td = _make_test_data()
        self.data = self.td["data"]

    def test_returns_figure(self) -> None:
        fig = plot_ema_cloud(
            self.td["ema_cloud"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        assert isinstance(fig, go.Figure)

    def test_has_candlestick_trace(self) -> None:
        fig = plot_ema_cloud(
            self.td["ema_cloud"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        candle_traces = [t for t in fig.data if isinstance(t, go.Candlestick)]
        assert len(candle_traces) == 1

    def test_has_cloud_fill_traces(self) -> None:
        fig = plot_ema_cloud(
            self.td["ema_cloud"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        # Cloud fill = 4 traces (lower+upper for bull, lower+upper for bear)
        fill_traces = [t for t in fig.data if getattr(t, "fill", None) == "tonexty"]
        assert len(fill_traces) == 2  # bull fill + bear fill

    def test_has_hma_lines(self) -> None:
        fig = plot_ema_cloud(
            self.td["ema_cloud"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        hma_traces = [t for t in fig.data if t.name and "HMA" in t.name]
        assert len(hma_traces) == 2  # rising + falling

    def test_hma_line_width_3(self) -> None:
        fig = plot_ema_cloud(
            self.td["ema_cloud"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        hma_traces = [t for t in fig.data if t.name and "HMA" in t.name]
        for t in hma_traces:
            assert t.line.width == 3

    def test_last_close_annotation(self) -> None:
        fig = plot_ema_cloud(
            self.td["ema_cloud"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        last_close = float(self.data["close"][-1])
        annotations = [a for a in fig.layout.annotations if f"{last_close:,.2f}" in a.text]
        assert len(annotations) == 1

    def test_bloomberg_theme(self) -> None:
        fig = plot_ema_cloud(
            self.td["ema_cloud"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        assert fig.layout.template == BLOOMBERG_TEMPLATE


class TestPlotFullGrid:
    def setup_method(self) -> None:
        self.td = _make_test_data()
        self.data = self.td["data"]

    def test_returns_figure(self) -> None:
        fig = plot_full_grid(
            self.td["ema_cloud"], self.td["dstfs"], self.td["mc"],
            self.td["ivts"], self.td["borg"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        assert isinstance(fig, go.Figure)

    def test_has_6_subplots(self) -> None:
        fig = plot_full_grid(
            self.td["ema_cloud"], self.td["dstfs"], self.td["mc"],
            self.td["ivts"], self.td["borg"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        # 6 rows → yaxis through yaxis6
        assert fig.layout.yaxis6 is not None

    def test_layout_dimensions(self) -> None:
        fig = plot_full_grid(
            self.td["ema_cloud"], self.td["dstfs"], self.td["mc"],
            self.td["ivts"], self.td["borg"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        assert fig.layout.height == 1200
        assert fig.layout.width == 1400

    def test_bloomberg_theme(self) -> None:
        fig = plot_full_grid(
            self.td["ema_cloud"], self.td["dstfs"], self.td["mc"],
            self.td["ivts"], self.td["borg"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_yaxes_on_right(self) -> None:
        fig = plot_full_grid(
            self.td["ema_cloud"], self.td["dstfs"], self.td["mc"],
            self.td["ivts"], self.td["borg"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        for i in range(1, 7):
            yaxis = getattr(fig.layout, f"yaxis{i}" if i > 1 else "yaxis")
            assert yaxis.side == "right"

    def test_has_candlestick(self) -> None:
        fig = plot_full_grid(
            self.td["ema_cloud"], self.td["dstfs"], self.td["mc"],
            self.td["ivts"], self.td["borg"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        candle_traces = [t for t in fig.data if isinstance(t, go.Candlestick)]
        assert len(candle_traces) == 1

    def test_has_bar_traces(self) -> None:
        fig = plot_full_grid(
            self.td["ema_cloud"], self.td["dstfs"], self.td["mc"],
            self.td["ivts"], self.td["borg"],
            self.data["open"], self.data["high"],
            self.data["low"], self.data["close"],
        )
        bar_traces = [t for t in fig.data if isinstance(t, go.Bar)]
        # At least 3: DSTFS bias + MC totals + Borg transwarp
        assert len(bar_traces) >= 3
