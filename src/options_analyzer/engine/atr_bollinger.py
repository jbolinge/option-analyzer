"""ATR Bollinger Bands volatility warning indicator.

Translated from PineScript: EMA of True Range with Bollinger Bands.

IMPORTANT: Uses EMA(TR, period) — NOT Wilder's ATR (RMA). PineScript
``ta.ema(ta.tr, 20)`` differs from ``talib.ATR()`` which uses RMA.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from options_analyzer.engine.ta_utils import ema, sma, stdev, true_range


@dataclass(frozen=True)
class ATRBollingerResult:
    """Result of ATR Bollinger computation."""

    atr_ema: npt.NDArray[np.float64]  # EMA of True Range
    bb_basis: npt.NDArray[np.float64]  # SMA of atr_ema (Bollinger midline)
    bb_upper_1: npt.NDArray[np.float64]  # Upper Bollinger Band (1 stdev)
    bb_upper_2: npt.NDArray[np.float64]  # Upper Bollinger Band (2 stdev)
    bb_lower: npt.NDArray[np.float64]  # Lower Bollinger Band
    severity: npt.NDArray[np.float64]  # 0=normal, 1=atr>=1BB, 2=atr>=2BB


def compute_atr_bollinger(
    high: npt.NDArray[np.float64],
    low: npt.NDArray[np.float64],
    close: npt.NDArray[np.float64],
    atr_period: int = 20,
    bb_period: int = 20,
    bb_mult: float = 2.0,
) -> ATRBollingerResult:
    """Compute ATR Bollinger Bands.

    Parameters
    ----------
    high, low, close : OHLC arrays
    atr_period : Period for EMA of True Range (default 20)
    bb_period : Bollinger Band SMA period (default 20)
    bb_mult : Bollinger Band standard deviation multiplier (default 2.0)
    """
    tr = true_range(high, low, close)
    atr_ema = ema(tr, atr_period)

    bb_basis = sma(atr_ema, bb_period)
    bb_std = stdev(atr_ema, bb_period)

    bb_upper_1 = bb_basis + bb_std          # 1 stdev
    bb_upper_2 = bb_basis + bb_mult * bb_std  # 2 stdev (default bb_mult=2.0)
    bb_lower = bb_basis - bb_mult * bb_std

    # Severity: 0=normal, 1=atr_ema>upper_1, 2=atr_ema>upper_2
    severity = np.full_like(close, np.nan)
    valid = ~np.isnan(atr_ema) & ~np.isnan(bb_upper_2)
    severity[valid] = np.where(
        atr_ema[valid] >= bb_upper_2[valid],
        2.0,
        np.where(atr_ema[valid] >= bb_upper_1[valid], 1.0, 0.0),
    )

    return ATRBollingerResult(
        atr_ema=atr_ema,
        bb_basis=bb_basis,
        bb_upper_1=bb_upper_1,
        bb_upper_2=bb_upper_2,
        bb_lower=bb_lower,
        severity=severity,
    )
