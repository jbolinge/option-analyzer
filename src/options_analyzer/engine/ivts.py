"""IVTS (Implied Volatility Term Structure) warning indicator.

VIX / VIX3M ratio — when the ratio exceeds a threshold the term structure
is inverted (short-term vol > long-term vol), signaling market stress.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from options_analyzer.engine.ta_utils import sma


@dataclass(frozen=True)
class IVTSResult:
    """Result of IVTS computation."""

    ratio: npt.NDArray[np.float64]  # VIX / VIX3M
    smoothed: npt.NDArray[np.float64]  # SMA of ratio
    severity: npt.NDArray[np.float64]  # 0=normal, 1=ratio>=0.9, 2=ratio>=threshold


def compute_ivts(
    vix: npt.NDArray[np.float64],
    vix3m: npt.NDArray[np.float64],
    smooth_period: int = 5,
    threshold: float = 1.0,
) -> IVTSResult:
    """Compute IVTS (VIX/VIX3M) term structure warning.

    Parameters
    ----------
    vix : VIX close prices
    vix3m : VIX3M (3-month VIX) close prices
    smooth_period : SMA smoothing period for the ratio (default 5)
    threshold : Warning threshold — ratio above this triggers warning (default 1.0)

    Returns
    -------
    IVTSResult with ratio, smoothed ratio, and warning signal
    """
    # Avoid division by zero
    safe_vix3m = np.where(vix3m == 0, np.nan, vix3m)
    ratio = vix / safe_vix3m

    smoothed = sma(ratio, smooth_period)

    # Severity: based on raw ratio (not smoothed), matching PineScript
    # 0=normal, 1=ratio>=0.9, 2=ratio>=threshold (default 1.0)
    severity = np.full_like(vix, np.nan)
    valid = ~np.isnan(ratio)
    severity[valid] = np.where(
        ratio[valid] >= threshold,
        2.0,
        np.where(ratio[valid] >= 0.9, 1.0, 0.0),
    )

    return IVTSResult(
        ratio=ratio,
        smoothed=smoothed,
        severity=severity,
    )
