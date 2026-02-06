"""Tests for payoff chart functions."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.payoff_charts import (
    plot_expiration_payoff,
    plot_pnl_surface,
    plot_theoretical_pnl,
)
from options_analyzer.visualization.theme import BLOOMBERG_TEMPLATE


class TestPlotExpirationPayoff:
    """Tests for plot_expiration_payoff."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(100, 200, 50)
        self.payoff = np.maximum(0.0, self.price_range - 150) - 5.0

    def test_returns_figure(self) -> None:
        fig = plot_expiration_payoff(self.price_range, self.payoff)
        assert isinstance(fig, go.Figure)

    def test_has_payoff_trace(self) -> None:
        fig = plot_expiration_payoff(self.price_range, self.payoff)
        assert len(fig.data) >= 1

    def test_has_zero_line(self) -> None:
        fig = plot_expiration_payoff(self.price_range, self.payoff)
        # Should have a horizontal reference line at y=0
        shapes = fig.layout.shapes
        assert len(shapes) == 1  # type: ignore[arg-type]
        assert shapes[0].y0 == 0  # type: ignore[index]

    def test_xaxis_label(self) -> None:
        fig = plot_expiration_payoff(self.price_range, self.payoff)
        assert fig.layout.xaxis.title.text == "Underlying Price"  # type: ignore[union-attr]

    def test_yaxis_label(self) -> None:
        fig = plot_expiration_payoff(self.price_range, self.payoff)
        assert fig.layout.yaxis.title.text == "P&L ($)"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_expiration_payoff(self.price_range, self.payoff)
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_custom_title(self) -> None:
        fig = plot_expiration_payoff(
            self.price_range, self.payoff, title="My Payoff"
        )
        assert fig.layout.title.text == "My Payoff"  # type: ignore[union-attr]

    def test_breakeven_markers(self) -> None:
        fig = plot_expiration_payoff(
            self.price_range, self.payoff, breakevens=[155.0]
        )
        # payoff trace + breakeven scatter
        assert len(fig.data) == 2

    def test_no_breakevens_single_trace(self) -> None:
        fig = plot_expiration_payoff(self.price_range, self.payoff)
        assert len(fig.data) == 1


class TestPlotTheoreticalPnl:
    """Tests for plot_theoretical_pnl."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(100, 200, 50)
        self.pnl_by_dte = {
            "30 DTE": np.maximum(0.0, self.price_range - 150) - 8.0,
            "15 DTE": np.maximum(0.0, self.price_range - 150) - 6.0,
            "0 DTE": np.maximum(0.0, self.price_range - 150) - 5.0,
        }

    def test_returns_figure(self) -> None:
        fig = plot_theoretical_pnl(self.price_range, self.pnl_by_dte)
        assert isinstance(fig, go.Figure)

    def test_one_trace_per_dte(self) -> None:
        fig = plot_theoretical_pnl(self.price_range, self.pnl_by_dte)
        assert len(fig.data) == 3

    def test_trace_names_match_keys(self) -> None:
        fig = plot_theoretical_pnl(self.price_range, self.pnl_by_dte)
        names = [trace.name for trace in fig.data]
        assert set(names) == {"30 DTE", "15 DTE", "0 DTE"}

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_theoretical_pnl(self.price_range, self.pnl_by_dte)
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_xaxis_label(self) -> None:
        fig = plot_theoretical_pnl(self.price_range, self.pnl_by_dte)
        assert fig.layout.xaxis.title.text == "Underlying Price"  # type: ignore[union-attr]


class TestPlotPnlSurface:
    """Tests for plot_pnl_surface."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(100, 200, 20)
        self.dte_range = np.array([0, 15, 30, 45])
        self.surface = np.random.default_rng(42).standard_normal(
            (len(self.dte_range), len(self.price_range))
        )

    def test_returns_figure(self) -> None:
        fig = plot_pnl_surface(
            self.price_range, self.dte_range, self.surface
        )
        assert isinstance(fig, go.Figure)

    def test_has_surface_trace(self) -> None:
        fig = plot_pnl_surface(
            self.price_range, self.dte_range, self.surface
        )
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Surface)

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_pnl_surface(
            self.price_range, self.dte_range, self.surface
        )
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_3d_axis_labels(self) -> None:
        fig = plot_pnl_surface(
            self.price_range, self.dte_range, self.surface
        )
        scene = fig.layout.scene
        assert scene.xaxis.title.text == "Underlying Price"  # type: ignore[union-attr]
        assert scene.yaxis.title.text == "Days to Expiration"  # type: ignore[union-attr]
        assert scene.zaxis.title.text == "P&L ($)"  # type: ignore[union-attr]
