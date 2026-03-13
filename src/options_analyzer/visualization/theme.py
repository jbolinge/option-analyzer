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

GRID_COLOR = "#2d2d44"

LINE_WIDTH = 2
REFERENCE_LINE_WIDTH = 1
REFERENCE_DASH = "dash"
OVERLAY_DASH = "dot"
MARKER_SIZE = 10
MARKER_SYMBOL = "diamond"
SURFACE_COLORSCALE = "Plasma"

DSTFS_PALETTE: dict[str, str] = {
    "sma_rising": PALETTE["positive"],
    "sma_falling": PALETTE["negative"],
    "hma_rising": PALETTE["secondary"],
    "hma_falling": PALETTE["tertiary"],
    "bias_4": PALETTE["positive"],
    "bias_2": PALETTE["secondary"],
    "bias_0": "#ffffff",
    "bias_-2": PALETTE["tertiary"],
    "bias_-4": PALETTE["negative"],
    "candle_up": PALETTE["positive"],
    "candle_down": PALETTE["negative"],
}

EMA_CLOUD_PALETTE: dict[str, str] = {
    "ema_fast": PALETTE["primary"],
    "ema_slow": PALETTE["secondary"],
    "cloud_bullish": PALETTE["positive"],
    "cloud_bearish": PALETTE["negative"],
    "cloud_bullish_fill": "rgba(0, 204, 102, 0.3)",
    "cloud_bearish_fill": "rgba(204, 51, 51, 0.3)",
    "hma_rising": PALETTE["secondary"],
    "hma_falling": PALETTE["tertiary"],
}

ATR_BOLLINGER_PALETTE: dict[str, str] = {
    "atr_ema": PALETTE["primary"],
    "bb_upper": PALETTE["negative"],
    "bb_lower": PALETTE["secondary"],
    "bb_basis": PALETTE["neutral"],
    "warning": PALETTE["negative"],
}

OBV_BOLLINGER_PALETTE: dict[str, str] = {
    "obv": PALETTE["primary"],
    "bb_upper": PALETTE["secondary"],
    "bb_lower": PALETTE["negative"],
    "bb_basis": PALETTE["neutral"],
    "warning": PALETTE["negative"],
}

IVTS_PALETTE: dict[str, str] = {
    "ratio": PALETTE["primary"],
    "smoothed": PALETTE["secondary"],
    "threshold": PALETTE["negative"],
    "warning": PALETTE["negative"],
    "line_green": PALETTE["positive"],
    "line_yellow": "#ffff00",
    "line_fuchsia": PALETTE["tertiary"],
    "line_red": PALETTE["negative"],
    "thresh_09": "#ffff00",
    "thresh_095": PALETTE["tertiary"],
    "thresh_10": PALETTE["negative"],
}

FORCE_INDEX_PALETTE: dict[str, str] = {
    "primary_positive": PALETTE["positive"],
    "primary_negative": PALETTE["negative"],
    "secondary_positive": PALETTE["secondary"],
    "secondary_negative": PALETTE["tertiary"],
}

MC_WARNINGS_PALETTE: dict[str, str] = {
    "warning_0": PALETTE["positive"],
    "warning_1": PALETTE["secondary"],
    "warning_2": PALETTE["primary"],
    "warning_3": PALETTE["tertiary"],
    "warning_4": PALETTE["negative"],
    "warning_5": "#ff0000",
    "square_white": "#ffffff",
    "square_green": PALETTE["positive"],
    "square_aqua": PALETTE["secondary"],
    "square_fuchsia": PALETTE["tertiary"],
    "square_red": PALETTE["negative"],
    "total_white": "#ffffff",
    "total_yellow": "#ffff00",
    "total_fuchsia": PALETTE["tertiary"],
    "total_red": PALETTE["negative"],
}

BORG_PALETTE: dict[str, str] = {
    "qqq_bullish": PALETTE["positive"],
    "qqq_mixed": PALETTE["secondary"],
    "qqq_bearish": PALETTE["negative"],
    "psq": PALETTE["negative"],
    "shv": "#4488ff",
    "overbought": PALETTE["negative"],
    "oversold": PALETTE["positive"],
    "threshold_bull": PALETTE["positive"],
    "threshold_bear": PALETTE["negative"],
}

COLOR_CYCLE: list[str] = [
    PALETTE["primary"],
    PALETTE["secondary"],
    PALETTE["tertiary"],
    PALETTE["positive"],
    PALETTE["negative"],
    PALETTE["neutral"],
]

BLOOMBERG_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#1a1a2e",
        font=dict(family=_FONT_FAMILY, size=12, color=_TEXT_COLOR),
        title=dict(font=dict(size=16, color=_TEXT_COLOR)),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            gridwidth=1,
            zerolinecolor=GRID_COLOR,
            title=dict(font=dict(size=14)),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            gridwidth=1,
            zerolinecolor=GRID_COLOR,
            title=dict(font=dict(size=14)),
        ),
        colorway=COLOR_CYCLE,
        scene=dict(
            xaxis=dict(gridcolor=GRID_COLOR, backgroundcolor="#1a1a2e"),
            yaxis=dict(gridcolor=GRID_COLOR, backgroundcolor="#1a1a2e"),
            zaxis=dict(gridcolor=GRID_COLOR, backgroundcolor="#1a1a2e"),
        ),
    )
)

pio.templates["bloomberg"] = BLOOMBERG_TEMPLATE


def apply_theme(fig: go.Figure) -> go.Figure:
    """Apply Bloomberg theme to a figure. Returns the figure for chaining."""
    fig.layout.template = BLOOMBERG_TEMPLATE
    return fig
