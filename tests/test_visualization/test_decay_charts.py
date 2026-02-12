"""Tests for decay chart functions."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.decay_charts import (
    plot_decay_profiles,
    plot_payoff_with_delta,
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


class TestPlotPayoffWithDelta:
    """Tests for plot_payoff_with_delta."""

    def setup_method(self) -> None:
        self.price_range = np.linspace(80.0, 120.0, 21)
        self.payoff = np.where(self.price_range > 100, self.price_range - 100, 0) - 5
        self.delta_by_dte = {
            "60 DTE": np.linspace(20.0, 80.0, 21),
            "30 DTE": np.linspace(10.0, 90.0, 21),
            "7 DTE": np.linspace(2.0, 98.0, 21),
        }

    def test_returns_figure(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        assert isinstance(fig, go.Figure)

    def test_total_trace_count(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        # 1 payoff + 3 delta traces
        assert len(fig.data) == 4

    def test_payoff_trace_is_first(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        assert fig.data[0].name == "P&L at Expiration"

    def test_delta_trace_names_match_keys(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        delta_names = [t.name for t in fig.data[1:]]
        assert delta_names == ["60 DTE", "30 DTE", "7 DTE"]

    def test_has_secondary_yaxis(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        assert fig.layout.yaxis2 is not None

    def test_primary_yaxis_label(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        assert fig.layout.yaxis.title.text == "P&L ($)"  # type: ignore[union-attr]

    def test_secondary_yaxis_label(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        assert fig.layout.yaxis2.title.text == "Delta"  # type: ignore[union-attr]

    def test_xaxis_label(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        assert fig.layout.xaxis.title.text == "Underlying Price"  # type: ignore[union-attr]

    def test_bloomberg_theme_applied(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        assert fig.layout.template == BLOOMBERG_TEMPLATE

    def test_custom_title(self) -> None:
        fig = plot_payoff_with_delta(
            self.price_range, self.payoff, self.delta_by_dte, title="My Chart"
        )
        assert fig.layout.title.text == "My Chart"  # type: ignore[union-attr]

    def test_has_zero_line_shape(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        shapes = fig.layout.shapes
        assert len(shapes) >= 1  # type: ignore[arg-type]
        zero_line = shapes[0]  # type: ignore[index]
        assert zero_line.line.dash == "dash"  # type: ignore[union-attr]

    def test_payoff_trace_on_primary_axis(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        # Primary axis: yaxis is "y" (or absent, defaults to "y")
        assert fig.data[0].yaxis in (None, "y")

    def test_delta_traces_on_secondary_axis(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, self.delta_by_dte)
        for trace in fig.data[1:]:
            assert trace.yaxis == "y2"

    def test_single_delta_curve(self) -> None:
        fig = plot_payoff_with_delta(
            self.price_range, self.payoff, {"30 DTE": self.delta_by_dte["30 DTE"]}
        )
        assert len(fig.data) == 2  # 1 payoff + 1 delta

    def test_empty_delta_dict(self) -> None:
        fig = plot_payoff_with_delta(self.price_range, self.payoff, {})
        assert len(fig.data) == 1  # just payoff
