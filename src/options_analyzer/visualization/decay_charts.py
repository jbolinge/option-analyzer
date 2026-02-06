"""Decay chart functions — theta, charm, veta over time."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.theme import PALETTE, apply_theme


def plot_theta_decay(
    dte_range: np.ndarray,
    theta: np.ndarray,
    title: str = "Theta Decay",
) -> go.Figure:
    """Theta vs DTE — shows acceleration of time decay near expiration."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dte_range,
            y=theta,
            mode="lines",
            name="Theta",
            line=dict(color=PALETTE["negative"], width=2),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Days to Expiration",
        yaxis_title="Theta",
        xaxis=dict(autorange="reversed"),
    )

    return apply_theme(fig)


def plot_decay_profiles(
    dte_range: np.ndarray,
    greeks: dict[str, np.ndarray],
    title: str = "Time Decay Profiles",
) -> go.Figure:
    """Multiple time-dependent Greeks overlaid (theta, charm, veta)."""
    fig = go.Figure()

    colors = [PALETTE["negative"], PALETTE["tertiary"], PALETTE["secondary"]]

    for (label, values), color in zip(greeks.items(), colors, strict=False):
        fig.add_trace(
            go.Scatter(
                x=dte_range,
                y=values,
                mode="lines",
                name=label.capitalize(),
                line=dict(color=color, width=2),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Days to Expiration",
        yaxis_title="Value",
        xaxis=dict(autorange="reversed"),
    )

    return apply_theme(fig)
