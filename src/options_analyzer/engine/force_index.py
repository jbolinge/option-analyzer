"""Elder's Force Index indicator.

Force Index = close_change * volume, smoothed with EMA.
Dual-instrument variant compares two symbols' force indices for divergence.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from options_analyzer.engine.ta_utils import ema


@dataclass(frozen=True)
class ForceIndexResult:
    """Result of single-instrument Force Index computation."""

    raw: npt.NDArray[np.float64]  # Unsmoothed force index
    smoothed: npt.NDArray[np.float64]  # EMA-smoothed force index
    warning: npt.NDArray[np.float64]  # +1 if smoothed < 0, 0 otherwise


@dataclass(frozen=True)
class ForceIndexDualResult:
    """Result of dual-instrument Force Index computation."""

    primary: ForceIndexResult  # Primary instrument (e.g., SPY)
    secondary: ForceIndexResult  # Secondary instrument (e.g., QQQ)
    severity: npt.NDArray[np.float64]  # 0=neither, 1=one warning, 2=both warning


def compute_force_index(
    close: npt.NDArray[np.float64],
    volume: npt.NDArray[np.float64],
    period: int = 13,
) -> ForceIndexResult:
    """Compute Elder's Force Index for a single instrument.

    Parameters
    ----------
    close : closing prices
    volume : volume array
    period : EMA smoothing period (default 13)

    Returns
    -------
    ForceIndexResult with raw, smoothed, and warning signal
    """
    # Raw force index: price change * volume
    raw = np.full_like(close, np.nan)
    for i in range(1, len(close)):
        raw[i] = (close[i] - close[i - 1]) * volume[i]

    smoothed = ema(raw, period)

    # Warning: negative smoothed force index = selling pressure
    warning = np.full_like(close, np.nan)
    valid = ~np.isnan(smoothed)
    warning[valid] = np.where(smoothed[valid] < 0, 1.0, 0.0)

    return ForceIndexResult(raw=raw, smoothed=smoothed, warning=warning)


def compute_force_index_dual(
    close1: npt.NDArray[np.float64],
    volume1: npt.NDArray[np.float64],
    close2: npt.NDArray[np.float64],
    volume2: npt.NDArray[np.float64],
    period: int = 13,
) -> ForceIndexDualResult:
    """Compute dual-instrument Force Index.

    Warning triggers when BOTH instruments show selling pressure.

    Parameters
    ----------
    close1, volume1 : Primary instrument (e.g., SPY)
    close2, volume2 : Secondary instrument (e.g., QQQ)
    period : EMA smoothing period (default 13)
    """
    primary = compute_force_index(close1, volume1, period)
    secondary = compute_force_index(close2, volume2, period)

    # Severity: count how many instruments show selling pressure
    severity = np.full_like(close1, np.nan)
    valid = ~np.isnan(primary.warning) & ~np.isnan(secondary.warning)
    severity[valid] = primary.warning[valid] + secondary.warning[valid]

    return ForceIndexDualResult(
        primary=primary,
        secondary=secondary,
        severity=severity,
    )
