"""Borg Transwarp V2 — 14-block multi-factor allocation model.

Analyzes 20 ETFs across 14 logic blocks to derive normalized allocations
across three signals: QQQ (bullish), SHV (neutral), PSQ (bearish).
Includes overbought/oversold market condition detection.

Translated from PineScript: 05-BorgTranswarp.txt
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from options_analyzer.engine.ta_utils import pct_change, rsi, sma

# The 20 ETFs tracked by Borg Transwarp
BORG_TICKERS: list[str] = [
    "SPY", "IOO", "QQQ", "VTV", "XLF", "XLP", "TLT", "SHV",
    "AGG", "IEF", "PSQ", "SH", "BND", "VWO", "FDN", "XLU",
    "XLK", "KMLM", "SMH", "HYD",
]


@dataclass(frozen=True)
class BorgTickerData:
    """Pre-computed derived arrays for all 20 ETFs at a single bar.

    Each field is a scalar float representing the indicator value at the
    current bar index. Built by prepare_borg_ticker_data().
    """

    # SPY
    spy_close: float
    spy_rsi10: float
    spy_rsi21: float
    spy_sma100: float
    spy_sma200: float

    # IOO
    ioo_rsi10: float

    # QQQ
    qqq_close: float
    qqq_rsi10: float
    qqq_sma20: float
    qqq_sma25: float
    qqq_pct10: float
    qqq_pct20: float
    qqq_pct60: float
    qqq_return_sma10: float  # SMA(10) of daily return

    # VTV
    vtv_rsi10: float

    # XLF
    xlf_rsi10: float

    # XLP
    xlp_rsi10: float

    # TLT
    tlt_rsi20: float
    tlt_rsi21: float
    tlt_rsi126: float

    # SHV
    shv_pct60: float
    shv_pct63: float
    shv_pct126: float

    # AGG
    agg_rsi10: float
    agg_rsi20: float
    agg_rsi21: float
    agg_pct60: float

    # IEF
    ief_rsi7: float
    ief_rsi10: float

    # PSQ
    psq_rsi20: float
    psq_rsi21: float

    # SH
    sh_rsi60: float

    # BND
    bnd_pct60: float

    # VWO
    vwo_close: float
    vwo_sma63: float
    vwo_sma126: float
    vwo_pct60: float
    vwo_pct63: float
    vwo_pct126: float

    # FDN
    fdn_rsi200: float

    # XLU
    xlu_rsi126: float
    xlu_rsi200: float

    # XLK
    xlk_rsi10: float
    xlk_rsi126: float

    # KMLM
    kmlm_close: float
    kmlm_rsi10: float
    kmlm_sma20: float

    # SMH
    smh_rsi10: float

    # HYD
    hyd_rsi10: float


@dataclass(frozen=True)
class BlockResult:
    """Result of a single allocation block."""

    psq: float = 0.0
    qqq: float = 0.0
    shv: float = 0.0
    weight: float = 1.0


@dataclass(frozen=True)
class BorgTranswarpResult:
    """Result of Borg Transwarp computation at a single bar."""

    psq: float  # Bearish allocation (0-1)
    qqq: float  # Bullish allocation (0-1)
    shv: float  # Neutral allocation (0-1)
    overbought: bool
    oversold: bool


def _block1_tlt20_psq20(d: BorgTickerData) -> BlockResult:
    if d.tlt_rsi20 > d.psq_rsi20:
        return BlockResult(qqq=1.0)
    return BlockResult(shv=1.0)


def _block2_agg20_sh60(d: BorgTickerData) -> BlockResult:
    if d.agg_rsi20 > d.sh_rsi60:
        return BlockResult(qqq=1.0)
    return BlockResult(shv=1.0)


def _block3_twenty_sixty_ten_twenty(d: BorgTickerData) -> BlockResult:
    if d.agg_rsi20 > d.sh_rsi60:
        return BlockResult(qqq=1.0)
    if d.ief_rsi10 > d.psq_rsi20:
        return BlockResult(qqq=1.0)
    return BlockResult(shv=1.0)


def _block4_bnd60_shv60(d: BorgTickerData) -> BlockResult:
    if d.bnd_pct60 > d.shv_pct60:
        return BlockResult(qqq=1.0)
    return BlockResult(shv=1.0)


def _block5_vwo_momentum_126(d: BorgTickerData) -> BlockResult:
    if d.vwo_pct126 > d.shv_pct126:
        if d.vwo_close > d.vwo_sma126:
            return BlockResult(qqq=1.0, weight=0.5)
        return BlockResult(qqq=0.5, shv=0.5, weight=0.5)
    return BlockResult(shv=1.0, weight=0.5)


def _block6_vwo_momentum_63(d: BorgTickerData) -> BlockResult:
    if d.vwo_pct63 > d.shv_pct63:
        if d.vwo_close > d.vwo_sma63:
            return BlockResult(qqq=1.0, weight=0.5)
        return BlockResult(qqq=0.5, shv=0.5, weight=0.5)
    return BlockResult(shv=1.0, weight=0.5)


def _block7_kmlm_spy(d: BorgTickerData) -> BlockResult:
    if d.spy_rsi10 > d.kmlm_rsi10:
        return BlockResult(qqq=1.0, weight=0.25)
    if d.kmlm_close < d.kmlm_sma20:
        return BlockResult(qqq=1.0, weight=0.25)
    if d.qqq_rsi10 < 32.5:
        return BlockResult(shv=1.0, weight=0.25)
    return BlockResult(psq=1.0, weight=0.25)


def _block8_kmlm_xlk(d: BorgTickerData) -> BlockResult:
    if d.xlk_rsi10 > d.kmlm_rsi10:
        return BlockResult(qqq=1.0, weight=0.25)
    if d.kmlm_close < d.kmlm_sma20:
        return BlockResult(qqq=1.0, weight=0.25)
    if d.qqq_rsi10 < 32.5:
        return BlockResult(shv=1.0, weight=0.25)
    return BlockResult(psq=1.0, weight=0.25)


def _block9_kmlm_smh(d: BorgTickerData) -> BlockResult:
    if d.smh_rsi10 > d.kmlm_rsi10:
        return BlockResult(qqq=1.0, weight=0.25)
    if d.kmlm_close < d.kmlm_sma20:
        return BlockResult(qqq=1.0, weight=0.25)
    if d.qqq_rsi10 < 32.5:
        return BlockResult(shv=1.0, weight=0.25)
    return BlockResult(psq=1.0, weight=0.25)


def _block10_kmlm_hyd(d: BorgTickerData) -> BlockResult:
    if d.hyd_rsi10 > d.kmlm_rsi10:
        return BlockResult(qqq=1.0, weight=0.25)
    if d.qqq_rsi10 < 32.5:
        return BlockResult(shv=1.0, weight=0.25)
    return BlockResult(psq=1.0, weight=0.25)


def _block11_twenty_sixty_200ma(d: BorgTickerData) -> BlockResult:
    if d.spy_close > d.spy_sma200:
        if d.agg_rsi20 > d.sh_rsi60:
            return BlockResult(qqq=1.0)
        if d.qqq_rsi10 < 32.5:
            return BlockResult(shv=1.0)
        return BlockResult(psq=1.0)
    if d.qqq_pct60 < -0.11:
        if d.agg_rsi10 > d.qqq_rsi10:
            return BlockResult(qqq=1.0)
        if d.qqq_rsi10 < 32.5:
            return BlockResult(shv=1.0)
        return BlockResult(psq=1.0)
    if d.qqq_close > d.qqq_sma20:
        if d.tlt_rsi21 > d.psq_rsi21:
            return BlockResult(qqq=1.0)
        if d.qqq_rsi10 < 32.5:
            return BlockResult(shv=1.0)
        return BlockResult(psq=1.0)
    if d.qqq_rsi10 < 32.5:
        return BlockResult(shv=1.0)
    return BlockResult(psq=1.0)


def _block12_ftlt_bull_bonds(d: BorgTickerData) -> BlockResult:
    if d.xlu_rsi126 < d.xlk_rsi126:
        if d.agg_rsi20 > d.sh_rsi60:
            return BlockResult(qqq=1.0)
        if d.agg_rsi21 > d.spy_rsi21:
            return BlockResult(qqq=1.0)
        if d.qqq_rsi10 < 32.5:
            return BlockResult(shv=1.0)
        return BlockResult(psq=1.0)
    if d.tlt_rsi126 < 50.0:
        if d.agg_rsi20 > d.sh_rsi60:
            return BlockResult(qqq=1.0)
        if d.qqq_rsi10 < 32.5:
            return BlockResult(shv=1.0)
        return BlockResult(psq=1.0)
    if d.qqq_rsi10 < 32.5:
        return BlockResult(shv=1.0)
    return BlockResult(psq=1.0)


def _block13_ftlt_1999_100ma(d: BorgTickerData) -> BlockResult:
    if d.spy_close > d.spy_sma100:
        if d.qqq_close > d.qqq_sma25:
            return BlockResult(qqq=1.0)
        if d.qqq_pct20 > d.qqq_return_sma10:
            return BlockResult(qqq=1.0)
        if d.agg_pct60 > d.shv_pct60:
            return BlockResult(qqq=1.0)
        if d.vwo_pct60 > d.shv_pct60:
            return BlockResult(qqq=1.0)
        if d.ief_rsi7 > d.psq_rsi20:
            return BlockResult(shv=1.0)
        if d.qqq_rsi10 < 32.5:
            return BlockResult(shv=1.0)
        return BlockResult(psq=1.0)
    if d.qqq_close > d.qqq_sma25:
        if d.qqq_pct10 > 0.05:
            if d.qqq_rsi10 < 32.5:
                return BlockResult(shv=1.0)
            return BlockResult(psq=1.0)
        return BlockResult(qqq=1.0)
    return BlockResult(shv=1.0)


def _block14_fdn200_xlu200(d: BorgTickerData) -> BlockResult:
    if d.fdn_rsi200 > d.xlu_rsi200:
        return BlockResult(qqq=1.0)
    return BlockResult(shv=1.0)


_ALL_BLOCKS = [
    _block1_tlt20_psq20,
    _block2_agg20_sh60,
    _block3_twenty_sixty_ten_twenty,
    _block4_bnd60_shv60,
    _block5_vwo_momentum_126,
    _block6_vwo_momentum_63,
    _block7_kmlm_spy,
    _block8_kmlm_xlk,
    _block9_kmlm_smh,
    _block10_kmlm_hyd,
    _block11_twenty_sixty_200ma,
    _block12_ftlt_bull_bonds,
    _block13_ftlt_1999_100ma,
    _block14_fdn200_xlu200,
]


def _check_overbought_oversold(d: BorgTickerData) -> tuple[bool, bool]:
    """Check overbought/oversold conditions."""
    overbought = (
        d.spy_rsi10 > 80
        or d.ioo_rsi10 > 79
        or d.qqq_rsi10 > 79
        or d.vtv_rsi10 > 78
        or d.xlf_rsi10 > 80
        or d.xlp_rsi10 > 76
    )
    oversold = False
    if not overbought:
        if d.qqq_rsi10 < 32.5:
            oversold = True
        elif d.spy_rsi10 < 30:
            oversold = True
    return overbought, oversold


def prepare_borg_ticker_data(
    closes: dict[str, npt.NDArray[np.float64]],
) -> list[BorgTickerData]:
    """Compute all derived indicators from raw closes for all 20 tickers.

    Parameters
    ----------
    closes : dict mapping ticker symbol to close price array.
             All arrays must have the same length.

    Returns
    -------
    List of BorgTickerData, one per bar. Early bars with insufficient
    warmup data will have NaN values.
    """
    n = len(next(iter(closes.values())))

    # Pre-compute all needed indicators
    spy_c = closes["SPY"]
    spy_rsi10 = rsi(spy_c, 10)
    spy_rsi21 = rsi(spy_c, 21)
    spy_sma100 = sma(spy_c, 100)
    spy_sma200 = sma(spy_c, 200)

    ioo_rsi10 = rsi(closes["IOO"], 10)

    qqq_c = closes["QQQ"]
    qqq_rsi10 = rsi(qqq_c, 10)
    qqq_sma20 = sma(qqq_c, 20)
    qqq_sma25 = sma(qqq_c, 25)
    qqq_pct10 = pct_change(qqq_c, 10)
    qqq_pct20 = pct_change(qqq_c, 20)
    qqq_pct60 = pct_change(qqq_c, 60)
    # daily return and its SMA(10)
    qqq_daily_ret = pct_change(qqq_c, 1)
    qqq_ret_sma10 = sma(qqq_daily_ret, 10)

    vtv_rsi10 = rsi(closes["VTV"], 10)
    xlf_rsi10 = rsi(closes["XLF"], 10)
    xlp_rsi10 = rsi(closes["XLP"], 10)

    tlt_c = closes["TLT"]
    tlt_rsi20 = rsi(tlt_c, 20)
    tlt_rsi21 = rsi(tlt_c, 21)
    tlt_rsi126 = rsi(tlt_c, 126)

    shv_c = closes["SHV"]
    shv_pct60 = pct_change(shv_c, 60)
    shv_pct63 = pct_change(shv_c, 63)
    shv_pct126 = pct_change(shv_c, 126)

    agg_c = closes["AGG"]
    agg_rsi10 = rsi(agg_c, 10)
    agg_rsi20 = rsi(agg_c, 20)
    agg_rsi21 = rsi(agg_c, 21)
    agg_pct60 = pct_change(agg_c, 60)

    ief_c = closes["IEF"]
    ief_rsi7 = rsi(ief_c, 7)
    ief_rsi10 = rsi(ief_c, 10)

    psq_c = closes["PSQ"]
    psq_rsi20 = rsi(psq_c, 20)
    psq_rsi21 = rsi(psq_c, 21)

    sh_rsi60 = rsi(closes["SH"], 60)
    bnd_pct60 = pct_change(closes["BND"], 60)

    vwo_c = closes["VWO"]
    vwo_sma63 = sma(vwo_c, 63)
    vwo_sma126 = sma(vwo_c, 126)
    vwo_pct60 = pct_change(vwo_c, 60)
    vwo_pct63 = pct_change(vwo_c, 63)
    vwo_pct126 = pct_change(vwo_c, 126)

    fdn_rsi200 = rsi(closes["FDN"], 200)

    xlu_c = closes["XLU"]
    xlu_rsi126 = rsi(xlu_c, 126)
    xlu_rsi200 = rsi(xlu_c, 200)

    xlk_c = closes["XLK"]
    xlk_rsi10 = rsi(xlk_c, 10)
    xlk_rsi126 = rsi(xlk_c, 126)

    kmlm_c = closes["KMLM"]
    kmlm_rsi10 = rsi(kmlm_c, 10)
    kmlm_sma20 = sma(kmlm_c, 20)

    smh_rsi10 = rsi(closes["SMH"], 10)
    hyd_rsi10 = rsi(closes["HYD"], 10)

    def _val(arr: npt.NDArray[np.float64], i: int) -> float:
        v = arr[i]
        return float(v) if not np.isnan(v) else float("nan")

    result: list[BorgTickerData] = []
    for i in range(n):
        result.append(
            BorgTickerData(
                spy_close=_val(spy_c, i),
                spy_rsi10=_val(spy_rsi10, i),
                spy_rsi21=_val(spy_rsi21, i),
                spy_sma100=_val(spy_sma100, i),
                spy_sma200=_val(spy_sma200, i),
                ioo_rsi10=_val(ioo_rsi10, i),
                qqq_close=_val(qqq_c, i),
                qqq_rsi10=_val(qqq_rsi10, i),
                qqq_sma20=_val(qqq_sma20, i),
                qqq_sma25=_val(qqq_sma25, i),
                qqq_pct10=_val(qqq_pct10, i),
                qqq_pct20=_val(qqq_pct20, i),
                qqq_pct60=_val(qqq_pct60, i),
                qqq_return_sma10=_val(qqq_ret_sma10, i),
                vtv_rsi10=_val(vtv_rsi10, i),
                xlf_rsi10=_val(xlf_rsi10, i),
                xlp_rsi10=_val(xlp_rsi10, i),
                tlt_rsi20=_val(tlt_rsi20, i),
                tlt_rsi21=_val(tlt_rsi21, i),
                tlt_rsi126=_val(tlt_rsi126, i),
                shv_pct60=_val(shv_pct60, i),
                shv_pct63=_val(shv_pct63, i),
                shv_pct126=_val(shv_pct126, i),
                agg_rsi10=_val(agg_rsi10, i),
                agg_rsi20=_val(agg_rsi20, i),
                agg_rsi21=_val(agg_rsi21, i),
                agg_pct60=_val(agg_pct60, i),
                ief_rsi7=_val(ief_rsi7, i),
                ief_rsi10=_val(ief_rsi10, i),
                psq_rsi20=_val(psq_rsi20, i),
                psq_rsi21=_val(psq_rsi21, i),
                sh_rsi60=_val(sh_rsi60, i),
                bnd_pct60=_val(bnd_pct60, i),
                vwo_close=_val(vwo_c, i),
                vwo_sma63=_val(vwo_sma63, i),
                vwo_sma126=_val(vwo_sma126, i),
                vwo_pct60=_val(vwo_pct60, i),
                vwo_pct63=_val(vwo_pct63, i),
                vwo_pct126=_val(vwo_pct126, i),
                fdn_rsi200=_val(fdn_rsi200, i),
                xlu_rsi126=_val(xlu_rsi126, i),
                xlu_rsi200=_val(xlu_rsi200, i),
                xlk_rsi10=_val(xlk_rsi10, i),
                xlk_rsi126=_val(xlk_rsi126, i),
                kmlm_close=_val(kmlm_c, i),
                kmlm_rsi10=_val(kmlm_rsi10, i),
                kmlm_sma20=_val(kmlm_sma20, i),
                smh_rsi10=_val(smh_rsi10, i),
                hyd_rsi10=_val(hyd_rsi10, i),
            )
        )

    return result


def compute_borg_transwarp(d: BorgTickerData) -> BorgTranswarpResult:
    """Compute Borg Transwarp allocation for a single bar.

    Runs all 14 blocks, normalizes allocations by total weight,
    and checks overbought/oversold conditions.

    Parameters
    ----------
    d : BorgTickerData for the current bar

    Returns
    -------
    BorgTranswarpResult with normalized allocations and market state
    """
    # Skip bars with NaN data — return neutral allocation
    import math

    # Check a few critical fields for NaN
    critical = [d.spy_close, d.qqq_close, d.spy_rsi10, d.qqq_rsi10]
    if any(math.isnan(v) for v in critical):
        return BorgTranswarpResult(
            psq=0.0, qqq=0.0, shv=1.0, overbought=False, oversold=False
        )

    total_psq = 0.0
    total_qqq = 0.0
    total_shv = 0.0
    total_weight = 0.0

    for block_fn in _ALL_BLOCKS:
        br = block_fn(d)
        total_psq += br.psq * br.weight
        total_qqq += br.qqq * br.weight
        total_shv += br.shv * br.weight
        total_weight += br.weight

    if total_weight > 0:
        total_psq /= total_weight
        total_qqq /= total_weight
        total_shv /= total_weight

    overbought, oversold = _check_overbought_oversold(d)

    return BorgTranswarpResult(
        psq=total_psq,
        qqq=total_qqq,
        shv=total_shv,
        overbought=overbought,
        oversold=oversold,
    )


def compute_borg_transwarp_series(
    closes: dict[str, npt.NDArray[np.float64]],
) -> list[BorgTranswarpResult]:
    """Compute Borg Transwarp for an entire time series.

    Convenience function that calls prepare_borg_ticker_data() then
    compute_borg_transwarp() for each bar.
    """
    ticker_data = prepare_borg_ticker_data(closes)
    return [compute_borg_transwarp(d) for d in ticker_data]
