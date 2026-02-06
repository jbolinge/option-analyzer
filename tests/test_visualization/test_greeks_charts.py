"""Tests for Greeks chart functions."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.greeks_charts import (
    plot_greeks_summary,
    plot_greeks_vs_price,
    plot_per_leg_greeks,
)
from options_analyzer.visualization.theme import BLOOMBERG_TEMPLATE


class TestPlotGreeksVsPrice:
    """Tests for plot_greeks_vs_price (2x2 subplots)."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(100, 200, 50)
        self.greeks = {
            "delta": np.linspace(0.1, 0.9, 50),
            "gamma": np.full(50, 0.05),
            "theta": np.full(50, -0.03),
            "vega": np.full(50, 0.2),
        }

    def test_returns_figure(self) -> None:
        fig = plot_greeks_vs_price(self.price_range, self.greeks)
        assert isinstance(fig, go.Figure)

    def test_has_four_traces(self) -> None:
        fig = plot_greeks_vs_price(self.price_range, self.greeks)
        assert len(fig.data) == 4

    def test_trace_names(self) -> None:
        fig = plot_greeks_vs_price(self.price_range, self.greeks)
        names = [t.name for t in fig.data]
        assert set(names) == {"Delta", "Gamma", "Theta", "Vega"}

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_greeks_vs_price(self.price_range, self.greeks)
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_has_subplots(self) -> None:
        fig = plot_greeks_vs_price(self.price_range, self.greeks)
        # make_subplots creates xaxis, xaxis2, xaxis3, xaxis4
        assert fig.layout.xaxis2 is not None  # type: ignore[union-attr]
        assert fig.layout.xaxis4 is not None  # type: ignore[union-attr]


class TestPlotGreeksSummary:
    """Tests for plot_greeks_summary (bar chart of current values)."""

    def setup_method(self) -> None:
        self.greeks = {
            "delta": 0.45,
            "gamma": 0.03,
            "theta": -0.05,
            "vega": 0.18,
            "rho": 0.01,
        }

    def test_returns_figure(self) -> None:
        fig = plot_greeks_summary(self.greeks)
        assert isinstance(fig, go.Figure)

    def test_has_bar_trace(self) -> None:
        fig = plot_greeks_summary(self.greeks)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Bar)

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_greeks_summary(self.greeks)
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_custom_title(self) -> None:
        fig = plot_greeks_summary(self.greeks, title="My Greeks")
        assert fig.layout.title.text == "My Greeks"  # type: ignore[union-attr]


class TestPlotPerLegGreeks:
    """Tests for plot_per_leg_greeks (overlaid traces per leg)."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(100, 200, 50)
        self.per_leg = {
            "AAPL C150": {"delta": np.linspace(0.2, 0.8, 50)},
            "AAPL C160": {"delta": np.linspace(0.1, 0.7, 50)},
        }

    def test_returns_figure(self) -> None:
        fig = plot_per_leg_greeks(
            self.price_range, self.per_leg, "delta"
        )
        assert isinstance(fig, go.Figure)

    def test_one_trace_per_leg(self) -> None:
        fig = plot_per_leg_greeks(
            self.price_range, self.per_leg, "delta"
        )
        assert len(fig.data) == 2

    def test_trace_names_match_legs(self) -> None:
        fig = plot_per_leg_greeks(
            self.price_range, self.per_leg, "delta"
        )
        names = [t.name for t in fig.data]
        assert set(names) == {"AAPL C150", "AAPL C160"}

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_per_leg_greeks(
            self.price_range, self.per_leg, "delta"
        )
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_yaxis_label_matches_greek(self) -> None:
        fig = plot_per_leg_greeks(
            self.price_range, self.per_leg, "delta"
        )
        assert fig.layout.yaxis.title.text == "Delta"  # type: ignore[union-attr]
