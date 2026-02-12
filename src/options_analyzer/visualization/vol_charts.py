"""Vol chart functions — vanna, volga profiles."""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from options_analyzer.visualization.theme import LINE_WIDTH, PALETTE, apply_theme


def plot_vanna_profile(
    price_range: np.ndarray,
    vanna: np.ndarray,
    title: str = "Vanna Profile",
) -> go.Figure:
    """Vanna vs underlying price — delta sensitivity to IV changes."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=price_range,
            y=vanna,
            mode="lines",
            name="Vanna",
            line=dict(color=PALETTE["secondary"], width=LINE_WIDTH),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Underlying Price",
        yaxis_title="Vanna",
    )

    return apply_theme(fig)


def plot_volga_profile(
    price_range: np.ndarray,
    volga: np.ndarray,
    title: str = "Volga Profile",
) -> go.Figure:
    """Volga vs underlying price — vega sensitivity to IV changes."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=price_range,
            y=volga,
            mode="lines",
            name="Volga",
            line=dict(color=PALETTE["tertiary"], width=LINE_WIDTH),
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Underlying Price",
        yaxis_title="Volga",
    )

    return apply_theme(fig)


def plot_vol_sensitivity(
    price_range: np.ndarray,
    greeks: dict[str, np.ndarray],
    title: str = "Vol Sensitivity",
) -> go.Figure:
    """Combined vanna + volga subplots."""
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=("Vanna", "Volga"),
        shared_xaxes=True,
    )

    colors = [PALETTE["secondary"], PALETTE["tertiary"]]
    for i, ((label, values), color) in enumerate(
        zip(greeks.items(), colors, strict=False), start=1
    ):
        fig.add_trace(
            go.Scatter(
                x=price_range,
                y=values,
                mode="lines",
                name=label.capitalize(),
                line=dict(color=color, width=LINE_WIDTH),
            ),
            row=i,
            col=1,
        )

    fig.update_layout(title=title)
    fig.update_xaxes(title_text="Underlying Price", row=2, col=1)

    return apply_theme(fig)
