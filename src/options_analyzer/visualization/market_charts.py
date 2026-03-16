"""Market indicator chart functions — 6 panels matching TradingView layout.

Individual ``plot_*()`` functions for standalone use, plus ``plot_full_grid()``
for the complete 6-panel composite. All use Bloomberg dark theme.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from options_analyzer.engine.borg_transwarp import BorgTranswarpResult
from options_analyzer.engine.ema_cloud import EMACloudResult
from options_analyzer.engine.indicators import DSTFSResult
from options_analyzer.engine.ivts import IVTSResult
from options_analyzer.engine.mc_warnings import MCWarningsResult
from options_analyzer.visualization.chart_utils import (
    add_cloud_fill,
    add_colored_line,
    add_threshold_colored_line,
    compute_rangebreaks,
)
from options_analyzer.visualization.theme import (
    BORG_PALETTE,
    DSTFS_PALETTE,
    EMA_CLOUD_PALETTE,
    IVTS_PALETTE,
    MC_WARNINGS_PALETTE,
    REFERENCE_DASH,
    REFERENCE_LINE_WIDTH,
    apply_theme,
)

# ---------------------------------------------------------------------------
# Panel 1: EMA Cloud + HMA
# ---------------------------------------------------------------------------


def plot_ema_cloud(
    result: EMACloudResult,
    opens: npt.NDArray[np.float64],
    highs: npt.NDArray[np.float64],
    lows: npt.NDArray[np.float64],
    closes: npt.NDArray[np.float64],
    timestamps: Sequence[Any] | None = None,
    title: str = "EMA Cloud",
    fig: go.Figure | None = None,
    row: int = 1,
    col: int = 1,
) -> go.Figure:
    """Candlestick + EMA cloud fill + colored HMA line."""
    x = list(timestamps) if timestamps is not None else list(range(len(closes)))
    standalone = fig is None
    if standalone:
        fig = make_subplots(rows=1, cols=1)
    assert fig is not None

    # Candlestick
    fig.add_trace(
        go.Candlestick(
            x=x, open=opens, high=highs, low=lows, close=closes,
            increasing_line_color=DSTFS_PALETTE["candle_up"],
            decreasing_line_color=DSTFS_PALETTE["candle_down"],
            name="Price", showlegend=False,
        ),
        row=row, col=col,
    )

    # EMA cloud fill
    add_cloud_fill(
        fig, x, result.ema_fast, result.ema_slow,
        result.cloud_bullish,
        EMA_CLOUD_PALETTE["cloud_bullish_fill"],
        EMA_CLOUD_PALETTE["cloud_bearish_fill"],
        row=row, col=col,
    )

    # HMA colored line (thick)
    add_colored_line(
        fig, x, result.hma_values, result.hma_direction,
        EMA_CLOUD_PALETTE["hma_rising"],
        EMA_CLOUD_PALETTE["hma_falling"],
        "HMA Rising", "HMA Falling",
        row=row, col=col,
    )
    # Override HMA line width to 3
    for trace in fig.data[-2:]:
        trace.line.width = 3

    # Last-close badge
    last_close = float(closes[-1])
    last_color = (
        DSTFS_PALETTE["candle_up"]
        if last_close >= float(opens[-1])
        else DSTFS_PALETTE["candle_down"]
    )
    yref = f"y{row}" if row > 1 else "y"
    fig.add_annotation(
        x=1.0, xref="paper", xanchor="left",
        y=last_close, yref=yref,
        text=f" {last_close:,.2f} ",
        showarrow=False,
        font=dict(color="#000000", size=11),
        bgcolor=last_color, borderpad=2,
    )

    if standalone:
        fig.update_layout(title=title, xaxis_rangeslider_visible=False)
        fig.update_yaxes(side="right")
        rangebreaks = compute_rangebreaks(x)
        if rangebreaks:
            fig.update_xaxes(rangebreaks=rangebreaks)
        apply_theme(fig)
    return fig


# ---------------------------------------------------------------------------
# Panel 2: DSTFS Bias
# ---------------------------------------------------------------------------


def _bias_color(value: float | int) -> str:
    key = f"bias_{int(value)}"
    return DSTFS_PALETTE[key]


def plot_dstfs_bias(
    result: DSTFSResult,
    timestamps: Sequence[Any] | None = None,
    title: str = "DSTFS Bias",
    fig: go.Figure | None = None,
    row: int = 1,
    col: int = 1,
) -> go.Figure:
    """Bias histogram with 5-color mapping and zero reference line."""
    x = list(timestamps) if timestamps is not None else list(range(len(result.close)))
    standalone = fig is None
    if standalone:
        fig = make_subplots(rows=1, cols=1)
    assert fig is not None

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
            name="Bias", showlegend=False,
        ),
        row=row, col=col,
    )

    # Dashed zero reference line
    yref = f"y{row}" if row > 1 else "y"
    fig.add_shape(
        type="line", x0=0, x1=1, xref="paper",
        y0=0, y1=0, yref=yref,
        line=dict(color="#555555", width=REFERENCE_LINE_WIDTH, dash=REFERENCE_DASH),
    )

    if standalone:
        fig.update_layout(title=title, bargap=0.5)
        fig.update_yaxes(zeroline=False, side="right")
        rangebreaks = compute_rangebreaks(x)
        if rangebreaks:
            fig.update_xaxes(rangebreaks=rangebreaks)
        apply_theme(fig)
    return fig


# ---------------------------------------------------------------------------
# Panel 3: MC Warnings Squares
# ---------------------------------------------------------------------------

# Row labels for the 5 sub-indicators
_MC_SQUARE_LABELS = ["FI", "IVTS", "OBV", "ATR", "DSTFS"]

# Severity → color for squares (ATR/OBV/IVTS/FI)
_SEVERITY_COLOR = {
    0.0: MC_WARNINGS_PALETTE["square_white"],
    1.0: MC_WARNINGS_PALETTE["square_fuchsia"],
    2.0: MC_WARNINGS_PALETTE["square_red"],
}

# DSTFS bias → color (5-level)
_DSTFS_SQUARE_COLOR = {
    4: MC_WARNINGS_PALETTE["square_green"],
    2: MC_WARNINGS_PALETTE["square_aqua"],
    0: MC_WARNINGS_PALETTE["square_white"],
    -2: MC_WARNINGS_PALETTE["square_fuchsia"],
    -4: MC_WARNINGS_PALETTE["square_red"],
}


def plot_mc_warnings_squares(
    mc_result: MCWarningsResult,
    dstfs_result: DSTFSResult | None = None,
    timestamps: Sequence[Any] | None = None,
    title: str = "MC Warnings",
    fig: go.Figure | None = None,
    row: int = 1,
    col: int = 1,
) -> go.Figure:
    """5-row marker grid showing sub-indicator severity as colored squares."""
    n = len(mc_result.total)
    x = list(timestamps) if timestamps is not None else list(range(n))
    standalone = fig is None
    if standalone:
        fig = make_subplots(rows=1, cols=1)
    assert fig is not None

    # Build per-color groups to minimize trace count
    color_groups: dict[str, tuple[list[Any], list[float]]] = {}

    for i in range(n):
        # Row 0: FI severity
        # Row 1: IVTS severity
        # Row 2: OBV severity
        # Row 3: ATR severity
        severities = [
            mc_result.fi_severity[i],
            mc_result.ivts_severity[i],
            mc_result.obv_severity[i],
            mc_result.atr_severity[i],
        ]
        for y_idx, sev in enumerate(severities):
            if np.isnan(sev):
                sev = 0.0
            color = _SEVERITY_COLOR.get(sev, MC_WARNINGS_PALETTE["square_white"])
            color_groups.setdefault(color, ([], []))
            color_groups[color][0].append(x[i])
            color_groups[color][1].append(float(y_idx))

        # Row 4: DSTFS bias
        if dstfs_result is not None:
            bias_val = dstfs_result.total_bias[i]
            if np.isnan(bias_val):
                bias_int = 0
            else:
                bias_int = int(bias_val)
            default_sq = MC_WARNINGS_PALETTE["square_white"]
            color = _DSTFS_SQUARE_COLOR.get(bias_int, default_sq)
        else:
            dstfs_w = mc_result.dstfs_warning[i]
            color = (
                MC_WARNINGS_PALETTE["square_fuchsia"]
                if (not np.isnan(dstfs_w) and dstfs_w > 0)
                else MC_WARNINGS_PALETTE["square_white"]
            )
        color_groups.setdefault(color, ([], []))
        color_groups[color][0].append(x[i])
        color_groups[color][1].append(4.0)

    for color, (xs, ys) in color_groups.items():
        fig.add_trace(
            go.Scatter(
                x=xs, y=ys, mode="markers",
                marker=dict(symbol="square", size=14, color=color),
                showlegend=False, hoverinfo="skip",
            ),
            row=row, col=col,
        )

    # Y-axis labels
    yaxis_key = f"yaxis{row}" if row > 1 else "yaxis"
    fig.update_layout(**{
        yaxis_key: dict(
            tickvals=[0, 1, 2, 3, 4],
            ticktext=_MC_SQUARE_LABELS,
        ),
    })

    if standalone:
        fig.update_layout(title=title)
        fig.update_yaxes(side="right")
        rangebreaks = compute_rangebreaks(x)
        if rangebreaks:
            fig.update_xaxes(rangebreaks=rangebreaks)
        apply_theme(fig)
    return fig


# ---------------------------------------------------------------------------
# Panel 4: MC Warnings Totals
# ---------------------------------------------------------------------------

_TOTAL_COLORS = {
    0: MC_WARNINGS_PALETTE["total_white"],
    1: MC_WARNINGS_PALETTE["total_white"],
    2: MC_WARNINGS_PALETTE["total_white"],
    3: MC_WARNINGS_PALETTE["total_yellow"],
    4: MC_WARNINGS_PALETTE["total_fuchsia"],
    5: MC_WARNINGS_PALETTE["total_red"],
}


def plot_mc_warnings_totals(
    mc_result: MCWarningsResult,
    timestamps: Sequence[Any] | None = None,
    title: str = "MC Warning Totals",
    fig: go.Figure | None = None,
    row: int = 1,
    col: int = 1,
) -> go.Figure:
    """Histogram 0-5 with per-bar colors indicating severity level."""
    n = len(mc_result.total)
    x = list(timestamps) if timestamps is not None else list(range(n))
    standalone = fig is None
    if standalone:
        fig = make_subplots(rows=1, cols=1)
    assert fig is not None

    default_tc = MC_WARNINGS_PALETTE["total_white"]
    bar_colors = [
        _TOTAL_COLORS.get(int(v) if not np.isnan(v) else 0, default_tc)
        for v in mc_result.total
    ]

    fig.add_trace(
        go.Bar(
            x=x, y=mc_result.total,
            marker=dict(color=bar_colors),
            name="Warnings", showlegend=False,
        ),
        row=row, col=col,
    )

    # Black spacer at Y=5
    yref = f"y{row}" if row > 1 else "y"
    fig.add_shape(
        type="line", x0=0, x1=1, xref="paper",
        y0=5, y1=5, yref=yref,
        line=dict(color="#000000", width=1),
    )

    if standalone:
        fig.update_layout(title=title, bargap=0.5)
        fig.update_yaxes(side="right", range=[0, 5.5])
        rangebreaks = compute_rangebreaks(x)
        if rangebreaks:
            fig.update_xaxes(rangebreaks=rangebreaks)
        apply_theme(fig)
    return fig


# ---------------------------------------------------------------------------
# Panel 5: IVTS
# ---------------------------------------------------------------------------


def plot_ivts(
    result: IVTSResult,
    timestamps: Sequence[Any] | None = None,
    title: str = "IVTS",
    fig: go.Figure | None = None,
    row: int = 1,
    col: int = 1,
) -> go.Figure:
    """4-color IVTS line with threshold reference lines."""
    n = len(result.ratio)
    x = list(timestamps) if timestamps is not None else list(range(n))
    standalone = fig is None
    if standalone:
        fig = make_subplots(rows=1, cols=1)
    assert fig is not None

    add_threshold_colored_line(
        fig, x, result.ratio,
        thresholds=[0.9, 0.95, 1.0],
        colors=[
            IVTS_PALETTE["line_green"],
            IVTS_PALETTE["line_yellow"],
            IVTS_PALETTE["line_fuchsia"],
            IVTS_PALETTE["line_red"],
        ],
        names=["IVTS <0.9", "IVTS 0.9-0.95", "IVTS 0.95-1.0", "IVTS >1.0"],
        row=row, col=col,
    )

    # Threshold reference lines
    yref = f"y{row}" if row > 1 else "y"
    for level, color in [
        (0.9, IVTS_PALETTE["thresh_09"]),
        (0.95, IVTS_PALETTE["thresh_095"]),
        (1.0, IVTS_PALETTE["thresh_10"]),
    ]:
        fig.add_shape(
            type="line", x0=0, x1=1, xref="paper",
            y0=level, y1=level, yref=yref,
            line=dict(color=color, width=REFERENCE_LINE_WIDTH, dash=REFERENCE_DASH),
        )

    if standalone:
        fig.update_layout(title=title)
        fig.update_yaxes(side="right")
        rangebreaks = compute_rangebreaks(x)
        if rangebreaks:
            fig.update_xaxes(rangebreaks=rangebreaks)
        apply_theme(fig)
    return fig


# ---------------------------------------------------------------------------
# Panel 6: Borg Transwarp
# ---------------------------------------------------------------------------


def plot_borg_transwarp(
    results: list[BorgTranswarpResult],
    timestamps: Sequence[Any] | None = None,
    title: str = "Borg Transwarp",
    fig: go.Figure | None = None,
    row: int = 1,
    col: int = 1,
) -> go.Figure:
    """QQQ allocation bars + overbought/oversold markers."""
    n = len(results)
    x = list(timestamps) if timestamps is not None else list(range(n))
    standalone = fig is None
    if standalone:
        fig = make_subplots(rows=1, cols=1)
    assert fig is not None

    qqq_values = np.array([r.qqq for r in results])

    # Bar colors by QQQ allocation level
    bar_colors = []
    for v in qqq_values:
        if v >= 0.66:
            bar_colors.append(BORG_PALETTE["qqq_bullish"])
        elif v >= 0.33:
            bar_colors.append(BORG_PALETTE["qqq_mixed"])
        else:
            bar_colors.append(BORG_PALETTE["qqq_bearish"])

    fig.add_trace(
        go.Bar(
            x=x, y=qqq_values,
            marker=dict(color=bar_colors),
            name="QQQ Alloc", showlegend=False,
        ),
        row=row, col=col,
    )

    # Overbought markers
    ob_x = [x[i] for i in range(n) if results[i].overbought]
    ob_y = [1.1] * len(ob_x)
    if ob_x:
        fig.add_trace(
            go.Scatter(
                x=ob_x, y=ob_y, mode="markers",
                marker=dict(symbol="circle", size=8, color=BORG_PALETTE["overbought"]),
                name="Overbought", showlegend=False,
            ),
            row=row, col=col,
        )

    # Oversold markers
    os_x = [x[i] for i in range(n) if results[i].oversold]
    os_y = [-0.15] * len(os_x)
    if os_x:
        fig.add_trace(
            go.Scatter(
                x=os_x, y=os_y, mode="markers",
                marker=dict(symbol="circle", size=8, color=BORG_PALETTE["oversold"]),
                name="Oversold", showlegend=False,
            ),
            row=row, col=col,
        )

    # Threshold lines at 0.33 and 0.66
    yref = f"y{row}" if row > 1 else "y"
    for level in [0.33, 0.66]:
        fig.add_shape(
            type="line", x0=0, x1=1, xref="paper",
            y0=level, y1=level, yref=yref,
            line=dict(color="#555555", width=REFERENCE_LINE_WIDTH, dash=REFERENCE_DASH),
        )

    if standalone:
        fig.update_layout(title=title, bargap=0.5)
        fig.update_yaxes(side="right", range=[-0.2, 1.15])
        rangebreaks = compute_rangebreaks(x)
        if rangebreaks:
            fig.update_xaxes(rangebreaks=rangebreaks)
        apply_theme(fig)
    return fig


# ---------------------------------------------------------------------------
# Borg Candlestick (2-panel debugging chart)
# ---------------------------------------------------------------------------


def plot_borg_candlestick(
    borg_results: list[BorgTranswarpResult],
    opens: npt.NDArray[np.float64],
    highs: npt.NDArray[np.float64],
    lows: npt.NDArray[np.float64],
    closes: npt.NDArray[np.float64],
    timestamps: Sequence[Any] | None = None,
    title: str = "Borg Transwarp Analysis",
) -> go.Figure:
    """Two-panel chart: SPX candlestick (top 70%), Borg bars (bottom 30%)."""
    x = list(timestamps) if timestamps is not None else list(range(len(closes)))

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.7, 0.3], vertical_spacing=0.05,
    )

    # Top panel: candlestick with DSTFS candle colors
    fig.add_trace(
        go.Candlestick(
            x=x, open=opens, high=highs, low=lows, close=closes,
            increasing_line_color=DSTFS_PALETTE["candle_up"],
            decreasing_line_color=DSTFS_PALETTE["candle_down"],
            name="Price",
        ),
        row=1, col=1,
    )

    # Last-close price badge
    last_close = float(closes[-1])
    last_color = (
        DSTFS_PALETTE["candle_up"]
        if last_close >= float(opens[-1])
        else DSTFS_PALETTE["candle_down"]
    )
    fig.add_annotation(
        x=1.0, xref="paper", xanchor="left",
        y=last_close, yref="y",
        text=f" {last_close:,.2f} ",
        showarrow=False,
        font=dict(color="#000000", size=11),
        bgcolor=last_color, borderpad=2,
    )

    # Bottom panel: reuse existing Borg Transwarp plot
    plot_borg_transwarp(borg_results, timestamps=timestamps, fig=fig, row=2, col=1)

    # Layout
    fig.update_layout(
        title=title,
        yaxis_title="Price",
        yaxis2_title="QQQ Alloc",
        showlegend=False,
        bargap=0.5,
        xaxis_rangeslider_visible=False,
    )

    fig.update_yaxes(side="right")
    fig.update_yaxes(range=[-0.2, 1.15], row=2, col=1)

    rangebreaks = compute_rangebreaks(x)
    if rangebreaks:
        fig.update_xaxes(rangebreaks=rangebreaks)

    return apply_theme(fig)


# ---------------------------------------------------------------------------
# Full Grid Composite
# ---------------------------------------------------------------------------


def plot_full_grid(
    ema_cloud_result: EMACloudResult,
    dstfs_result: DSTFSResult,
    mc_result: MCWarningsResult,
    ivts_result: IVTSResult,
    borg_results: list[BorgTranswarpResult],
    opens: npt.NDArray[np.float64],
    highs: npt.NDArray[np.float64],
    lows: npt.NDArray[np.float64],
    closes: npt.NDArray[np.float64],
    timestamps: Sequence[Any] | None = None,
    title: str = "Market Conditions Dashboard",
) -> go.Figure:
    """Assemble all 5 panels into a single vertically-stacked figure."""
    fig = make_subplots(
        rows=5, cols=1, shared_xaxes=True,
        row_heights=[0.50, 0.12, 0.08, 0.14, 0.16],
        vertical_spacing=0.02,
    )

    x = list(timestamps) if timestamps is not None else list(range(len(closes)))

    # Row 1: EMA Cloud + Candlestick
    plot_ema_cloud(ema_cloud_result, opens, highs, lows, closes,
                   timestamps=timestamps, fig=fig, row=1, col=1)

    # Row 2: MC Warnings Squares
    plot_mc_warnings_squares(mc_result, dstfs_result,
                             timestamps=timestamps, fig=fig, row=2, col=1)

    # Row 3: MC Warnings Totals
    plot_mc_warnings_totals(mc_result, timestamps=timestamps, fig=fig, row=3, col=1)

    # Row 4: IVTS
    plot_ivts(ivts_result, timestamps=timestamps, fig=fig, row=4, col=1)

    # Row 5: Borg Transwarp
    plot_borg_transwarp(borg_results, timestamps=timestamps, fig=fig, row=5, col=1)

    # Layout
    fig.update_layout(
        title=title,
        height=1200,
        width=1400,
        showlegend=False,
        xaxis_rangeslider_visible=False,
        bargap=0.5,
    )

    # All Y-axes on right side
    fig.update_yaxes(side="right")

    # Panel-specific Y-axis settings
    fig.update_yaxes(range=[0, 5.5], row=3, col=1)
    fig.update_yaxes(range=[-0.2, 1.15], row=5, col=1)

    # Rangebreaks on all X-axes
    rangebreaks = compute_rangebreaks(x)
    if rangebreaks:
        fig.update_xaxes(rangebreaks=rangebreaks)

    # Default zoom: last 3 months with fitted Y-axis
    zoom_bars = min(63, len(closes))
    fig.update_xaxes(range=[x[-zoom_bars], x[-1]])
    zoom_lows = lows[-zoom_bars:]
    zoom_highs = highs[-zoom_bars:]
    y_min, y_max = float(np.nanmin(zoom_lows)), float(np.nanmax(zoom_highs))
    y_pad = (y_max - y_min) * 0.02
    fig.update_yaxes(range=[y_min - y_pad, y_max + y_pad], row=1, col=1)

    return apply_theme(fig)
