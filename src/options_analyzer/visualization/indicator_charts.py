"""DSTFS indicator chart functions — two-panel Bloomberg-themed charts."""

from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from typing import Any

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from options_analyzer.engine.indicators import DSTFSResult
from options_analyzer.visualization.theme import (
    DSTFS_PALETTE,
    LINE_WIDTH,
    apply_theme,
)


def _compute_rangebreaks(x: Sequence[Any]) -> list[dict[str, Any]]:
    """Compute Plotly rangebreaks to hide weekends and holidays from a date axis."""
    if not x or not isinstance(x[0], (dt.datetime, dt.date)):
        return []

    dates = [v.date() if isinstance(v, dt.datetime) else v for v in x]
    holidays: list[str] = []
    one_day = dt.timedelta(days=1)

    for i in range(1, len(dates)):
        d = dates[i - 1] + one_day
        while d < dates[i]:
            if d.weekday() < 5:  # weekday gap = holiday
                holidays.append(d.isoformat())
            d += one_day

    breaks: list[dict[str, Any]] = [{"bounds": ["sat", "mon"]}]
    if holidays:
        breaks.append({"values": holidays})
    return breaks


def _bias_color(value: float | int) -> str:
    """Map a bias value to its DSTFS_PALETTE color."""
    key = f"bias_{int(value)}"
    return DSTFS_PALETTE[key]


def _add_colored_line(
    fig: go.Figure,
    x: Sequence[Any],
    y: npt.NDArray[np.float64],
    is_rising: npt.NDArray[np.float64],
    rising_color: str,
    falling_color: str,
    rising_name: str,
    falling_name: str,
    row: int,
    col: int,
) -> None:
    """Add a color-segmented line using NaN-gap technique."""
    rising_y = np.where(is_rising == 1.0, y, np.nan)
    falling_y = np.where(is_rising == -1.0, y, np.nan)

    # Bridge transitions so color segments visually connect
    for i in range(1, len(y)):
        if np.isnan(y[i]) or np.isnan(y[i - 1]):
            continue
        prev, curr = is_rising[i - 1], is_rising[i]
        # rising → falling: extend rising one step to connect
        if prev == 1.0 and curr == -1.0:
            rising_y[i] = y[i]
        # falling → rising: extend falling one step to connect
        elif prev == -1.0 and curr == 1.0:
            falling_y[i] = y[i]

    fig.add_trace(
        go.Scatter(
            x=list(x),
            y=rising_y,
            mode="lines",
            name=rising_name,
            line=dict(color=rising_color, width=LINE_WIDTH),
            connectgaps=False,
        ),
        row=row,
        col=col,
    )
    fig.add_trace(
        go.Scatter(
            x=list(x),
            y=falling_y,
            mode="lines",
            name=falling_name,
            line=dict(color=falling_color, width=LINE_WIDTH),
            connectgaps=False,
        ),
        row=row,
        col=col,
    )


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
        bargap=0.3,
    )

    fig.update_yaxes(
        zeroline=True,
        zerolinecolor="#555555",
        zerolinewidth=1,
        row=2,
        col=1,
    )

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
        bargap=0.3,
        xaxis_rangeslider_visible=False,
    )

    fig.update_yaxes(
        zeroline=True,
        zerolinecolor="#555555",
        zerolinewidth=1,
        row=2,
        col=1,
    )

    rangebreaks = _compute_rangebreaks(x)
    if rangebreaks:
        fig.update_xaxes(rangebreaks=rangebreaks)

    return apply_theme(fig)
