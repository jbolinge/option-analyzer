"""Decay chart functions — theta, charm, veta over time."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from options_analyzer.visualization.theme import _GRID_COLOR, PALETTE, apply_theme


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


_DELTA_COLORS = [
    PALETTE["secondary"],   # cyan
    PALETTE["tertiary"],    # magenta
    PALETTE["positive"],    # green
    PALETTE["negative"],    # red
    PALETTE["neutral"],     # gray
]


def plot_payoff_with_delta(
    price_range: np.ndarray,
    payoff: np.ndarray,
    delta_by_dte: dict[str, np.ndarray],
    title: str = "P&L at Expiration with Delta Profiles",
) -> go.Figure:
    """Dual Y-axis chart: expiration P&L (left) + delta curves at multiple DTEs (right).

    The visual separation between delta curves reveals charm (dDelta/dTime).
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # P&L trace on primary axis
    fig.add_trace(
        go.Scatter(
            x=price_range,
            y=payoff,
            mode="lines",
            name="P&L at Expiration",
            line=dict(color=PALETTE["primary"], width=2),
        ),
        secondary_y=False,
    )

    # Delta curves on secondary axis
    for i, (label, deltas) in enumerate(delta_by_dte.items()):
        color = _DELTA_COLORS[i % len(_DELTA_COLORS)]
        fig.add_trace(
            go.Scatter(
                x=price_range,
                y=deltas,
                mode="lines",
                name=label,
                line=dict(color=color, width=2, dash="dot"),
            ),
            secondary_y=True,
        )

    # Zero reference line for P&L
    fig.add_shape(
        type="line",
        x0=price_range[0],
        x1=price_range[-1],
        y0=0,
        y1=0,
        yref="y",
        line=dict(color=PALETTE["neutral"], width=1, dash="dash"),
    )

    fig.update_layout(
        title=title,
        xaxis_title="Underlying Price",
    )
    fig.update_yaxes(title_text="P&L ($)", secondary_y=False)
    fig.update_yaxes(
        title_text="Delta",
        secondary_y=True,
        gridcolor=_GRID_COLOR,
        zerolinecolor=_GRID_COLOR,
    )

    return apply_theme(fig)
