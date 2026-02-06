"""Bloomberg dark theme for plotly charts."""

import plotly.graph_objects as go
import plotly.io as pio

PALETTE: dict[str, str] = {
    "primary": "#ff6600",
    "secondary": "#00cccc",
    "tertiary": "#cc00cc",
    "positive": "#00cc66",
    "negative": "#cc3333",
    "neutral": "#888888",
}

_FONT_FAMILY = "Consolas, Monaco, 'Courier New', monospace"
_TEXT_COLOR = "#e0e0e0"
_GRID_COLOR = "#2d2d44"

BLOOMBERG_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#1a1a2e",
        font=dict(family=_FONT_FAMILY, size=12, color=_TEXT_COLOR),
        title=dict(font=dict(size=16, color=_TEXT_COLOR)),
        xaxis=dict(
            gridcolor=_GRID_COLOR,
            gridwidth=1,
            zerolinecolor=_GRID_COLOR,
            title=dict(font=dict(size=14)),
        ),
        yaxis=dict(
            gridcolor=_GRID_COLOR,
            gridwidth=1,
            zerolinecolor=_GRID_COLOR,
            title=dict(font=dict(size=14)),
        ),
        colorway=[
            PALETTE["primary"],
            PALETTE["secondary"],
            PALETTE["tertiary"],
            PALETTE["positive"],
            PALETTE["negative"],
            PALETTE["neutral"],
        ],
        scene=dict(
            xaxis=dict(gridcolor=_GRID_COLOR, backgroundcolor="#1a1a2e"),
            yaxis=dict(gridcolor=_GRID_COLOR, backgroundcolor="#1a1a2e"),
            zaxis=dict(gridcolor=_GRID_COLOR, backgroundcolor="#1a1a2e"),
        ),
    )
)

pio.templates["bloomberg"] = BLOOMBERG_TEMPLATE


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply Bloomberg theme to a figure. Returns the figure for chaining."""
    fig.layout.template = BLOOMBERG_TEMPLATE
    return fig
