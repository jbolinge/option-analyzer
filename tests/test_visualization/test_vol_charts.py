"""Tests for vol chart functions."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.theme import BLOOMBERG_TEMPLATE
from options_analyzer.visualization.vol_charts import (
    plot_vanna_profile,
    plot_vol_sensitivity,
    plot_volga_profile,
)


class TestPlotVannaProfile:
    """Tests for plot_vanna_profile."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(100, 200, 50)
        self.vanna = np.sin(np.linspace(-1, 1, 50)) * 0.01

    def test_returns_figure(self) -> None:
        fig = plot_vanna_profile(self.price_range, self.vanna)
        assert isinstance(fig, go.Figure)

    def test_has_one_trace(self) -> None:
        fig = plot_vanna_profile(self.price_range, self.vanna)
        assert len(fig.data) == 1

    def test_xaxis_label(self) -> None:
        fig = plot_vanna_profile(self.price_range, self.vanna)
        assert fig.layout.xaxis.title.text == "Underlying Price"  # type: ignore[union-attr]

    def test_yaxis_label(self) -> None:
        fig = plot_vanna_profile(self.price_range, self.vanna)
        assert fig.layout.yaxis.title.text == "Vanna"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_vanna_profile(self.price_range, self.vanna)
        assert fig.layout.template == BLOOMBERG_TEMPLATE


class TestPlotVolgaProfile:
    """Tests for plot_volga_profile."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(100, 200, 50)
        self.volga = np.abs(np.sin(np.linspace(-1, 1, 50))) * 0.02

    def test_returns_figure(self) -> None:
        fig = plot_volga_profile(self.price_range, self.volga)
        assert isinstance(fig, go.Figure)

    def test_has_one_trace(self) -> None:
        fig = plot_volga_profile(self.price_range, self.volga)
        assert len(fig.data) == 1

    def test_yaxis_label(self) -> None:
        fig = plot_volga_profile(self.price_range, self.volga)
        assert fig.layout.yaxis.title.text == "Volga"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_volga_profile(self.price_range, self.volga)
        assert fig.layout.template == BLOOMBERG_TEMPLATE


class TestPlotVolSensitivity:
    """Tests for plot_vol_sensitivity (combined subplots)."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(100, 200, 50)
        self.greeks = {
            "vanna": np.sin(np.linspace(-1, 1, 50)) * 0.01,
            "volga": np.abs(np.sin(np.linspace(-1, 1, 50))) * 0.02,
        }

    def test_returns_figure(self) -> None:
        fig = plot_vol_sensitivity(self.price_range, self.greeks)
        assert isinstance(fig, go.Figure)

    def test_has_two_traces(self) -> None:
        fig = plot_vol_sensitivity(self.price_range, self.greeks)
        assert len(fig.data) == 2

    def test_has_subplots(self) -> None:
        fig = plot_vol_sensitivity(self.price_range, self.greeks)
        # 2-row subplots create xaxis and xaxis2
        assert fig.layout.xaxis2 is not None  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_vol_sensitivity(self.price_range, self.greeks)
        assert fig.layout.template == BLOOMBERG_TEMPLATE
