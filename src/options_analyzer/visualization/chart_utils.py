"""Shared chart utilities for indicator visualization."""

from __future__ import annotations

import datetime as dt
from collections.abc import Sequence
from typing import Any

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go

from options_analyzer.visualization.theme import LINE_WIDTH


def compute_rangebreaks(x: Sequence[Any]) -> list[dict[str, Any]]:
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


def add_colored_line(
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
        # rising -> falling: extend rising one step to connect
        if prev == 1.0 and curr == -1.0:
            rising_y[i] = y[i]
        # falling -> rising: extend falling one step to connect
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


def add_cloud_fill(
    fig: go.Figure,
    x: Sequence[Any],
    upper: npt.NDArray[np.float64],
    lower: npt.NDArray[np.float64],
    is_bullish: npt.NDArray[np.float64],
    bull_fill: str,
    bear_fill: str,
    row: int,
    col: int,
) -> None:
    """Add continuous cloud fill between two EMA lines.

    Uses zero-width collapse instead of NaN gaps: when a regime is
    inactive, the fill trace collapses to match its reference trace,
    producing an invisible zero-width fill. This avoids the Plotly
    rendering issues caused by NaN-gapped ``fill="tonexty"`` traces.
    """
    x_list = list(x)

    # Bullish: fill from lower up to upper when bullish, collapse to lower otherwise
    bull_y = np.where(is_bullish == 1.0, upper, lower)
    fig.add_trace(
        go.Scatter(
            x=x_list, y=lower, mode="lines",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ),
        row=row, col=col,
    )
    fig.add_trace(
        go.Scatter(
            x=x_list, y=bull_y, mode="lines",
            line=dict(width=0), fill="tonexty",
            fillcolor=bull_fill, name="Cloud Bull", hoverinfo="skip",
        ),
        row=row, col=col,
    )

    # Bearish: fill from upper down to lower when bearish, collapse to upper otherwise
    bear_y = np.where(is_bullish == -1.0, lower, upper)
    fig.add_trace(
        go.Scatter(
            x=x_list, y=upper, mode="lines",
            line=dict(width=0), showlegend=False, hoverinfo="skip",
        ),
        row=row, col=col,
    )
    fig.add_trace(
        go.Scatter(
            x=x_list, y=bear_y, mode="lines",
            line=dict(width=0), fill="tonexty",
            fillcolor=bear_fill, name="Cloud Bear", hoverinfo="skip",
        ),
        row=row, col=col,
    )


def add_threshold_colored_line(
    fig: go.Figure,
    x: Sequence[Any],
    y: npt.NDArray[np.float64],
    thresholds: list[float],
    colors: list[str],
    names: list[str],
    row: int,
    col: int,
    line_width: int = LINE_WIDTH,
) -> None:
    """Add an N-segment colored line split by value thresholds.

    Parameters
    ----------
    thresholds : ascending threshold values, e.g. [0.9, 0.95, 1.0]
    colors : N+1 colors for each band (below first threshold ... above last)
    names : N+1 legend names

    Uses NaN-gap technique with bridging at transitions.
    """
    n_segments = len(thresholds) + 1
    segments: list[npt.NDArray[np.float64]] = [
        np.full_like(y, np.nan) for _ in range(n_segments)
    ]

    # Assign each point to its segment
    for i in range(len(y)):
        if np.isnan(y[i]):
            continue
        seg = 0
        for t in thresholds:
            if y[i] >= t:
                seg += 1
            else:
                break
        segments[seg][i] = y[i]

    # Bridge transitions
    for i in range(1, len(y)):
        if np.isnan(y[i]) or np.isnan(y[i - 1]):
            continue
        seg_prev = 0
        for t in thresholds:
            if y[i - 1] >= t:
                seg_prev += 1
            else:
                break
        seg_curr = 0
        for t in thresholds:
            if y[i] >= t:
                seg_curr += 1
            else:
                break
        if seg_prev != seg_curr:
            # Extend previous segment to current point for visual connection
            segments[seg_prev][i] = y[i]

    x_list = list(x)
    for seg_idx in range(n_segments):
        fig.add_trace(
            go.Scatter(
                x=x_list, y=segments[seg_idx],
                mode="lines",
                name=names[seg_idx],
                line=dict(color=colors[seg_idx], width=line_width),
                connectgaps=False,
            ),
            row=row, col=col,
        )
