"""Payoff and P&L chart functions."""

import numpy as np
import plotly.graph_objects as go

from options_analyzer.visualization.theme import (
    LINE_WIDTH,
    MARKER_SIZE,
    MARKER_SYMBOL,
    PALETTE,
    REFERENCE_DASH,
    REFERENCE_LINE_WIDTH,
    SURFACE_COLORSCALE,
    apply_theme,
)


def plot_expiration_payoff(
    price_range: np.ndarray,
    payoff: np.ndarray,
    breakevens: list[float] | None = None,
    title: str = "P&L at Expiration",
) -> go.Figure:
    """P&L at expiration diagram with optional breakeven markers."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=price_range,
            y=payoff,
            mode="lines",
            name="P&L",
            line=dict(color=PALETTE["primary"], width=LINE_WIDTH),
        )
    )

    if breakevens:
        fig.add_trace(
            go.Scatter(
                x=breakevens,
                y=[0.0] * len(breakevens),
                mode="markers",
                name="Breakeven",
                marker=dict(
                    color=PALETTE["secondary"], size=MARKER_SIZE, symbol=MARKER_SYMBOL
                ),
            )
        )

    fig.add_shape(
        type="line",
        x0=float(price_range[0]),
        x1=float(price_range[-1]),
        y0=0,
        y1=0,
        line=dict(
            color=PALETTE["neutral"], width=REFERENCE_LINE_WIDTH, dash=REFERENCE_DASH
        ),
    )

    fig.update_layout(
        title=title,
        xaxis_title="Underlying Price",
        yaxis_title="P&L ($)",
    )

    return apply_theme(fig)


def plot_theoretical_pnl(
    price_range: np.ndarray,
    pnl_by_dte: dict[str, np.ndarray],
    title: str = "Theoretical P&L",
) -> go.Figure:
    """Multiple P&L curves at different DTEs overlaid."""
    fig = go.Figure()

    for label, pnl in pnl_by_dte.items():
        fig.add_trace(
            go.Scatter(
                x=price_range,
                y=pnl,
                mode="lines",
                name=label,
                line=dict(width=LINE_WIDTH),
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Underlying Price",
        yaxis_title="P&L ($)",
    )

    return apply_theme(fig)


def plot_pnl_surface(
    price_range: np.ndarray,
    dte_range: np.ndarray,
    surface: np.ndarray,
    title: str = "P&L Surface",
) -> go.Figure:
    """3D surface: price x time x P&L."""
    fig = go.Figure(
        data=[
            go.Surface(
                x=price_range,
                y=dte_range,
                z=surface,
                colorscale=SURFACE_COLORSCALE,
            )
        ]
    )

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="Underlying Price",
            yaxis_title="Days to Expiration",
            zaxis_title="P&L ($)",
        ),
    )

    return apply_theme(fig)
