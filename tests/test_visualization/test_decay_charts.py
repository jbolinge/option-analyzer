"""Tests for decay chart functions."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.decay_charts import (
    plot_decay_profiles,
    plot_theta_decay,
)
from options_analyzer.visualization.theme import BLOOMBERG_TEMPLATE


class TestPlotThetaDecay:
    """Tests for plot_theta_decay."""

    def setup_method(self) -> None:
        self.dte_range = np.array([60, 45, 30, 15, 5, 1])
        self.theta = np.array([-0.02, -0.025, -0.035, -0.06, -0.15, -0.50])

    def test_returns_figure(self) -> None:
        fig = plot_theta_decay(self.dte_range, self.theta)
        assert isinstance(fig, go.Figure)

    def test_has_one_trace(self) -> None:
        fig = plot_theta_decay(self.dte_range, self.theta)
        assert len(fig.data) == 1

    def test_xaxis_label(self) -> None:
        fig = plot_theta_decay(self.dte_range, self.theta)
        assert fig.layout.xaxis.title.text == "Days to Expiration"  # type: ignore[union-attr]

    def test_xaxis_reversed(self) -> None:
        fig = plot_theta_decay(self.dte_range, self.theta)
        assert fig.layout.xaxis.autorange == "reversed"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_theta_decay(self.dte_range, self.theta)
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_custom_title(self) -> None:
        fig = plot_theta_decay(self.dte_range, self.theta, title="My Theta")
        assert fig.layout.title.text == "My Theta"  # type: ignore[union-attr]


class TestPlotDecayProfiles:
    """Tests for plot_decay_profiles."""

    def setup_method(self) -> None:
        self.dte_range = np.array([60, 45, 30, 15, 5, 1])
        self.greeks = {
            "theta": np.array([-0.02, -0.025, -0.035, -0.06, -0.15, -0.50]),
            "charm": np.array([-0.001, -0.002, -0.003, -0.005, -0.01, -0.03]),
            "veta": np.array([-0.005, -0.006, -0.008, -0.012, -0.025, -0.06]),
        }

    def test_returns_figure(self) -> None:
        fig = plot_decay_profiles(self.dte_range, self.greeks)
        assert isinstance(fig, go.Figure)

    def test_one_trace_per_greek(self) -> None:
        fig = plot_decay_profiles(self.dte_range, self.greeks)
        assert len(fig.data) == 3

    def test_trace_names(self) -> None:
        fig = plot_decay_profiles(self.dte_range, self.greeks)
        names = [t.name for t in fig.data]
        assert set(names) == {"Theta", "Charm", "Veta"}

    def test_xaxis_reversed(self) -> None:
        fig = plot_decay_profiles(self.dte_range, self.greeks)
        assert fig.layout.xaxis.autorange == "reversed"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_decay_profiles(self.dte_range, self.greeks)
        assert fig.layout.template == BLOOMBERG_TEMPLATE
