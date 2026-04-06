"""Market conditions service — orchestrates indicator computation and plotting."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from options_analyzer.engine.atr_bollinger import compute_atr_bollinger
from options_analyzer.engine.borg_transwarp import (
    BORG_TICKERS,
    compute_borg_transwarp_series,
)
from options_analyzer.engine.ema_cloud import compute_ema_cloud
from options_analyzer.engine.force_index import compute_force_index_dual
from options_analyzer.engine.indicators import compute_dstfs
from options_analyzer.engine.ivts import compute_ivts
from options_analyzer.engine.mc_warnings import compute_mc_warnings
from options_analyzer.engine.obv_bollinger import compute_obv_bollinger
from options_analyzer.ports.market_data import MarketDataProvider
from options_analyzer.visualization.market_charts import (
    plot_borg_transwarp,
    plot_dstfs_bias,
    plot_ema_cloud,
    plot_full_grid,
    plot_ivts,
    plot_mc_warnings_squares,
    plot_mc_warnings_totals,
)

# All symbols needed: 20 Borg tickers + SPX + VIX + VIX3M (deduplicated)
_ALL_SYMBOLS = list(dict.fromkeys(BORG_TICKERS + ["SPX", "VIX", "VIX3M"]))


async def compute_dashboard(
    market_data: MarketDataProvider,
    days_back: int = 1500,
) -> dict[str, Any]:
    """Fetch candles, compute all indicators, return full grid figure JSON.

    Returns dict with keys: figure, computed_at, symbol.
    """
    candle_data = await market_data.get_candles_batch(
        _ALL_SYMBOLS, interval="1d", days_back=days_back
    )

    spy = candle_data["SPY"]
    spx = candle_data["SPX"]
    qqq = candle_data["QQQ"]
    vix = candle_data["VIX"]
    vix3m = candle_data["VIX3M"]

    # Compute all indicators
    ema_result = compute_ema_cloud(spx.closes)
    dstfs_spy = compute_dstfs(spy.closes)
    atr_result = compute_atr_bollinger(spy.highs, spy.lows, spy.closes)
    obv_result = compute_obv_bollinger(spy.closes, spy.volumes)
    ivts_result = compute_ivts(vix.closes, vix3m.closes)
    fi_result = compute_force_index_dual(
        spy.closes, spy.volumes, qqq.closes, qqq.volumes
    )
    mc_result = compute_mc_warnings(
        atr_result, obv_result, ivts_result, fi_result, dstfs_spy
    )

    borg_closes = {
        sym: candle_data[sym].closes
        for sym in BORG_TICKERS
        if sym in candle_data
    }
    borg_results = compute_borg_transwarp_series(borg_closes)

    # Plot full grid
    fig = plot_full_grid(
        ema_cloud_result=ema_result,
        dstfs_result=dstfs_spy,
        mc_result=mc_result,
        ivts_result=ivts_result,
        borg_results=borg_results,
        opens=spx.opens,
        highs=spx.highs,
        lows=spx.lows,
        closes=spx.closes,
        timestamps=spx.timestamps,
        title="SPX — Market Conditions Dashboard (Daily)",
    )

    return {
        "figure": fig.to_plotly_json(),
        "computed_at": datetime.now(tz=UTC).isoformat(),
        "symbol": "SPX",
    }


# Panel name → standalone plot function mapping
_PANEL_BUILDERS = {
    "ema-cloud": "_build_ema_cloud",
    "dstfs-bias": "_build_dstfs_bias",
    "mc-squares": "_build_mc_squares",
    "mc-totals": "_build_mc_totals",
    "ivts": "_build_ivts",
    "borg": "_build_borg",
}

VALID_PANELS = list(_PANEL_BUILDERS.keys())


async def compute_panel(
    panel_name: str,
    market_data: MarketDataProvider,
    days_back: int = 1500,
) -> dict[str, Any]:
    """Compute and return a single panel figure JSON.

    Raises ValueError for unknown panel names.
    """
    if panel_name not in _PANEL_BUILDERS:
        raise ValueError(
            f"Unknown panel: {panel_name!r}. Valid: {VALID_PANELS}"
        )

    candle_data = await market_data.get_candles_batch(
        _ALL_SYMBOLS, interval="1d", days_back=days_back
    )

    spy = candle_data["SPY"]
    spx = candle_data["SPX"]
    qqq = candle_data["QQQ"]
    vix = candle_data["VIX"]
    vix3m = candle_data["VIX3M"]

    # Compute needed indicators
    dstfs_spy = compute_dstfs(spy.closes)

    if panel_name == "ema-cloud":
        ema_result = compute_ema_cloud(spx.closes)
        fig = plot_ema_cloud(
            ema_result, spx.opens, spx.highs, spx.lows, spx.closes,
            timestamps=spx.timestamps, title="EMA Cloud",
        )
    elif panel_name == "dstfs-bias":
        fig = plot_dstfs_bias(
            dstfs_spy, timestamps=spy.timestamps, title="DSTFS Bias",
        )
    elif panel_name in ("mc-squares", "mc-totals"):
        atr_result = compute_atr_bollinger(spy.highs, spy.lows, spy.closes)
        obv_result = compute_obv_bollinger(spy.closes, spy.volumes)
        ivts_result = compute_ivts(vix.closes, vix3m.closes)
        fi_result = compute_force_index_dual(
            spy.closes, spy.volumes, qqq.closes, qqq.volumes
        )
        mc_result = compute_mc_warnings(
            atr_result, obv_result, ivts_result, fi_result, dstfs_spy
        )
        if panel_name == "mc-squares":
            fig = plot_mc_warnings_squares(
                mc_result, dstfs_spy, timestamps=spy.timestamps,
            )
        else:
            fig = plot_mc_warnings_totals(
                mc_result, timestamps=spy.timestamps,
            )
    elif panel_name == "ivts":
        ivts_result = compute_ivts(vix.closes, vix3m.closes)
        fig = plot_ivts(
            ivts_result, timestamps=spy.timestamps, title="IVTS",
        )
    elif panel_name == "borg":
        borg_closes = {
            sym: candle_data[sym].closes
            for sym in BORG_TICKERS
            if sym in candle_data
        }
        borg_results = compute_borg_transwarp_series(borg_closes)
        fig = plot_borg_transwarp(
            borg_results, timestamps=spy.timestamps, title="Borg Transwarp",
        )
    else:
        raise ValueError(f"Unknown panel: {panel_name!r}")

    return {
        "figure": fig.to_plotly_json(),
        "computed_at": datetime.now(tz=UTC).isoformat(),
        "symbol": "SPX",
        "panel": panel_name,
    }
