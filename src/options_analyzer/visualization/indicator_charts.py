"""DSTFS indicator chart functions — two-panel Bloomberg-themed charts."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from options_analyzer.engine.indicators import DSTFSResult
from options_analyzer.visualization.chart_utils import (
    add_colored_line as _add_colored_line,
)
from options_analyzer.visualization.chart_utils import (
    compute_rangebreaks as _compute_rangebreaks,
)
from options_analyzer.visualization.theme import (
    DSTFS_PALETTE,
    apply_theme,
)


def _bias_color(value: float | int) -> str:
    """Map a bias value to its DSTFS_PALETTE color."""
    key = f"bias_{int(value)}"
    return DSTFS_PALETTE[key]


def plot_dstfs(
    result: DSTFSResult,
    timestamps: Sequence[Any] | None = None,
    title: str = "DSTFS Trend Analysis",
) -> go.Figure:
    """Two-panel chart: close with colored SMA/HMA (top), bias (bottom)."""
    x = list(timestamps) if timestamps is not None else list(range(len(result.close)))

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
    )

    # Top panel: close price line
    fig.add_trace(
        go.Scatter(
            x=x,
            y=result.close,
            mode="lines",
            name="Close",
            line=dict(color="#e0e0e0", width=1),
        ),
        row=1,
        col=1,
    )

    # Colored SMA
    _add_colored_line(
        fig,
        x,
        result.sma,
        result.sma_rising,
        DSTFS_PALETTE["sma_rising"],
        DSTFS_PALETTE["sma_falling"],
        "SMA Rising",
        "SMA Falling",
        row=1,
        col=1,
    )

    # Colored HMA
    _add_colored_line(
        fig,
        x,
        result.hma,
        result.hma_rising,
        DSTFS_PALETTE["hma_rising"],
        DSTFS_PALETTE["hma_falling"],
        "HMA Rising",
        "HMA Falling",
        row=1,
        col=1,
    )

    # Bottom panel: bias histogram
    valid_mask = ~np.isnan(result.total_bias)
    bias_colors = [
        _bias_color(v) if not np.isnan(v) else DSTFS_PALETTE["bias_0"]
        for v in result.total_bias
    ]
    bias_opacities = [
        0.0 if (not np.isnan(v) and int(v) == 0) else 1.0
        for v in result.total_bias
    ]

    fig.add_trace(
        go.Bar(
            x=x,
            y=np.where(valid_mask, result.total_bias, 0),
            marker=dict(color=bias_colors, opacity=bias_opacities),
            name="Bias",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        title=title,
        yaxis_title="Price",
        yaxis2_title="Bias",
        showlegend=True,
        bargap=0.5,
    )

    fig.update_yaxes(zeroline=False, row=2, col=1)

    fig.add_shape(
        type="line",
        x0=0, x1=1, xref="paper",
        y0=0, y1=0, yref="y2",
        line=dict(color="#555555", width=1, dash="dash"),
    )

    fig.update_yaxes(side="right")

    rangebreaks = _compute_rangebreaks(x)
    if rangebreaks:
        fig.update_xaxes(rangebreaks=rangebreaks)

    return apply_theme(fig)


def plot_dstfs_candlestick(
    result: DSTFSResult,
    opens: npt.NDArray[np.float64],
    highs: npt.NDArray[np.float64],
    lows: npt.NDArray[np.float64],
    timestamps: Sequence[Any] | None = None,
    title: str = "DSTFS Trend Analysis",
) -> go.Figure:
    """Two-panel chart: candlestick with colored MAs (top), bias (bottom)."""
    x = list(timestamps) if timestamps is not None else list(range(len(result.close)))

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
    )

    # Top panel: candlestick
    fig.add_trace(
        go.Candlestick(
            x=x,
            open=opens,
            high=highs,
            low=lows,
            close=result.close,
            increasing_line_color=DSTFS_PALETTE["candle_up"],
            decreasing_line_color=DSTFS_PALETTE["candle_down"],
            name="Price",
        ),
        row=1,
        col=1,
    )

    # Colored SMA
    _add_colored_line(
        fig,
        x,
        result.sma,
        result.sma_rising,
        DSTFS_PALETTE["sma_rising"],
        DSTFS_PALETTE["sma_falling"],
        "SMA Rising",
        "SMA Falling",
        row=1,
        col=1,
    )

    # Colored HMA
    _add_colored_line(
        fig,
        x,
        result.hma,
        result.hma_rising,
        DSTFS_PALETTE["hma_rising"],
        DSTFS_PALETTE["hma_falling"],
        "HMA Rising",
        "HMA Falling",
        row=1,
        col=1,
    )

    # Bottom panel: bias histogram
    valid_mask = ~np.isnan(result.total_bias)
    bias_colors = [
        _bias_color(v) if not np.isnan(v) else DSTFS_PALETTE["bias_0"]
        for v in result.total_bias
    ]
    bias_opacities = [
        0.0 if (not np.isnan(v) and int(v) == 0) else 1.0
        for v in result.total_bias
    ]

    fig.add_trace(
        go.Bar(
            x=x,
            y=np.where(valid_mask, result.total_bias, 0),
            marker=dict(color=bias_colors, opacity=bias_opacities),
            name="Bias",
            showlegend=False,
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        title=title,
        yaxis_title="Price",
        yaxis2_title="Bias",
        showlegend=True,
        bargap=0.5,
        xaxis_rangeslider_visible=False,
    )

    fig.update_yaxes(zeroline=False, row=2, col=1)

    fig.add_shape(
        type="line",
        x0=0, x1=1, xref="paper",
        y0=0, y1=0, yref="y2",
        line=dict(color="#555555", width=1, dash="dash"),
    )

    fig.update_yaxes(side="right")

    # Last-close price annotation
    last_close = float(result.close[-1])
    last_color = (
        DSTFS_PALETTE["candle_up"]
        if last_close >= float(opens[-1])
        else DSTFS_PALETTE["candle_down"]
    )
    fig.add_annotation(
        x=1.0,
        xref="paper",
        xanchor="left",
        y=last_close,
        yref="y",
        text=f" {last_close:,.2f} ",
        showarrow=False,
        font=dict(color="#000000", size=11),
        bgcolor=last_color,
        borderpad=2,
    )

    rangebreaks = _compute_rangebreaks(x)
    if rangebreaks:
        fig.update_xaxes(rangebreaks=rangebreaks)

    return apply_theme(fig)
