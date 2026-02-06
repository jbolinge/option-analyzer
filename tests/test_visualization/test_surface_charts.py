"""Tests for 3D surface chart functions."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.surface_charts import (
    plot_delta_surface,
    plot_gamma_surface,
    plot_greek_surface,
)
from options_analyzer.visualization.theme import BLOOMBERG_TEMPLATE


class TestPlotGreekSurface:
    """Tests for the generic plot_greek_surface."""

    def setup_method(self) -> None:
        self.x = np.linspace(100, 200, 10)
        self.y = np.linspace(0.1, 0.5, 8)
        self.z = np.random.default_rng(42).standard_normal((len(self.y), len(self.x)))

    def test_returns_figure(self) -> None:
        fig = plot_greek_surface(
            self.x, self.y, self.z, "Price", "Vol", "Delta"
        )
        assert isinstance(fig, go.Figure)

    def test_has_surface_trace(self) -> None:
        fig = plot_greek_surface(
            self.x, self.y, self.z, "Price", "Vol", "Delta"
        )
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Surface)

    def test_axis_labels(self) -> None:
        fig = plot_greek_surface(
            self.x, self.y, self.z, "Price", "Vol", "Delta"
        )
        scene = fig.layout.scene
        assert scene.xaxis.title.text == "Price"  # type: ignore[union-attr]
        assert scene.yaxis.title.text == "Vol"  # type: ignore[union-attr]
        assert scene.zaxis.title.text == "Delta"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_greek_surface(
            self.x, self.y, self.z, "Price", "Vol", "Delta"
        )
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_custom_title(self) -> None:
        fig = plot_greek_surface(
            self.x, self.y, self.z, "Price", "Vol", "Delta", title="Custom"
        )
        assert fig.layout.title.text == "Custom"  # type: ignore[union-attr]


class TestPlotDeltaSurface:
    """Tests for plot_delta_surface."""

    def setup_method(self) -> None:
        self.prices = np.linspace(100, 200, 10)
        self.vols = np.linspace(0.1, 0.5, 8)
        self.surface = np.random.default_rng(42).standard_normal(
            (len(self.vols), len(self.prices))
        )

    def test_returns_figure(self) -> None:
        fig = plot_delta_surface(self.prices, self.vols, self.surface)
        assert isinstance(fig, go.Figure)

    def test_has_surface_trace(self) -> None:
        fig = plot_delta_surface(self.prices, self.vols, self.surface)
        assert isinstance(fig.data[0], go.Surface)

    def test_axis_labels(self) -> None:
        fig = plot_delta_surface(self.prices, self.vols, self.surface)
        scene = fig.layout.scene
        assert scene.xaxis.title.text == "Underlying Price"  # type: ignore[union-attr]
        assert scene.yaxis.title.text == "Implied Volatility"  # type: ignore[union-attr]
        assert scene.zaxis.title.text == "Delta"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_delta_surface(self.prices, self.vols, self.surface)
        assert fig.layout.template == BLOOMBERG_TEMPLATE


class TestPlotGammaSurface:
    """Tests for plot_gamma_surface."""

    def setup_method(self) -> None:
        self.prices = np.linspace(100, 200, 10)
        self.dtes = np.array([1, 5, 15, 30, 45, 60])
        self.surface = np.random.default_rng(42).standard_normal(
            (len(self.dtes), len(self.prices))
        )

    def test_returns_figure(self) -> None:
        fig = plot_gamma_surface(self.prices, self.dtes, self.surface)
        assert isinstance(fig, go.Figure)

    def test_has_surface_trace(self) -> None:
        fig = plot_gamma_surface(self.prices, self.dtes, self.surface)
        assert isinstance(fig.data[0], go.Surface)

    def test_axis_labels(self) -> None:
        fig = plot_gamma_surface(self.prices, self.dtes, self.surface)
        scene = fig.layout.scene
        assert scene.xaxis.title.text == "Underlying Price"  # type: ignore[union-attr]
        assert scene.yaxis.title.text == "Days to Expiration"  # type: ignore[union-attr]
        assert scene.zaxis.title.text == "Gamma"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_gamma_surface(self.prices, self.dtes, self.surface)
        assert fig.layout.template == BLOOMBERG_TEMPLATE
