"""Greeks chart functions — risk profiles and per-leg breakdown."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from options_analyzer.visualization.theme import PALETTE, apply_theme

_GREEK_LABELS = {"delta": "Delta", "gamma": "Gamma", "theta": "Theta", "vega": "Vega"}


def plot_greeks_vs_price(
    price_range: np.ndarray,
    greeks: dict[str, np.ndarray],
    title: str = "Greeks vs Price",
) -> go.Figure:
    """2x2 subplots: delta, gamma, theta, vega vs underlying price."""
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("Delta", "Gamma", "Theta", "Vega"),
    )

    colors = [
        PALETTE["primary"],
        PALETTE["secondary"],
        PALETTE["tertiary"],
        PALETTE["positive"],
    ]
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]

    for (greek_key, label), color, (row, col) in zip(
        _GREEK_LABELS.items(), colors, positions, strict=True
    ):
        fig.add_trace(
            go.Scatter(
                x=price_range,
                y=greeks[greek_key],
                mode="lines",
                name=label,
                line=dict(color=color, width=2),
            ),
            row=row,
            col=col,
        )

    fig.update_layout(title=title, showlegend=True)
    return apply_theme(fig)


def plot_greeks_summary(
    greeks: dict[str, float],
    title: str = "Position Greeks",
) -> go.Figure:
    """Bar chart of current position-level Greeks values."""
    names = [k.capitalize() for k in greeks]
    values = list(greeks.values())

    colors = [
        PALETTE["positive"] if v >= 0 else PALETTE["negative"] for v in values
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=values,
                marker_color=colors,
                name="Greeks",
            )
        ]
    )

    fig.update_layout(
        title=title,
        xaxis_title="Greek",
        yaxis_title="Value",
    )

    return apply_theme(fig)


def plot_per_leg_greeks(
    price_range: np.ndarray,
    per_leg: dict[str, dict[str, np.ndarray]],
    greek_name: str,
    title: str | None = None,
) -> go.Figure:
    """Overlaid traces showing each leg's contribution to a specific Greek."""
    display_title = title or f"{greek_name.capitalize()} by Leg"
    fig = go.Figure()

    for leg_label, leg_greeks in per_leg.items():
        fig.add_trace(
            go.Scatter(
                x=price_range,
                y=leg_greeks[greek_name],
                mode="lines",
                name=leg_label,
                line=dict(width=2),
            )
        )

    fig.update_layout(
        title=display_title,
        xaxis_title="Underlying Price",
        yaxis_title=greek_name.capitalize(),
    )

    return apply_theme(fig)
