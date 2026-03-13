"""DSTFS (Dave's Simple Trend Following System) indicator computation.

Pure functions for SMA, WMA, HMA, and the composite DSTFS bias signal.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from options_analyzer.engine.ta_utils import direction as _direction
from options_analyzer.engine.ta_utils import hma, sma
from options_analyzer.engine.ta_utils import wma as wma  # noqa: F401 — re-export


@dataclass(frozen=True)
class DSTFSResult:
    """Result of DSTFS computation containing all component signals."""

    sma: npt.NDArray[np.float64]
    hma: npt.NDArray[np.float64]
    sma_rising: npt.NDArray[np.float64]
    hma_rising: npt.NDArray[np.float64]
    bias1: npt.NDArray[np.float64]
    bias2: npt.NDArray[np.float64]
    bias3: npt.NDArray[np.float64]
    bias4: npt.NDArray[np.float64]
    total_bias: npt.NDArray[np.float64]
    close: npt.NDArray[np.float64]


def compute_dstfs(
    close: npt.NDArray[np.float64],
    sma_period: int = 50,
    hma_period: int = 15,
) -> DSTFSResult:
    """Compute DSTFS trend-following indicator.

    Combines 4 bias components into a composite signal from -4 to +4:
    - bias1: SMA direction (+1 rising, -1 falling)
    - bias2: HMA direction (+1 rising, -1 falling)
    - bias3: HMA > SMA → +1, else -1
    - bias4: close > HMA → +1, else -1
    - total_bias = sum → values in {-4, -2, 0, 2, 4}
    """
    sma_values = sma(close, sma_period)
    hma_values = hma(close, hma_period)

    sma_dir = _direction(sma_values)
    hma_dir = _direction(hma_values)

    # bias1: SMA direction
    bias1 = sma_dir.copy()

    # bias2: HMA direction
    bias2 = hma_dir.copy()

    # bias3: HMA > SMA → +1, else -1
    bias3 = np.full_like(close, np.nan)
    valid = ~np.isnan(hma_values) & ~np.isnan(sma_values)
    bias3[valid] = np.where(hma_values[valid] > sma_values[valid], 1.0, -1.0)

    # bias4: close > HMA → +1, else -1
    bias4 = np.full_like(close, np.nan)
    valid_hma = ~np.isnan(hma_values)
    bias4[valid_hma] = np.where(
        close[valid_hma] > hma_values[valid_hma], 1.0, -1.0
    )

    # total_bias = sum of all 4
    total_bias = bias1 + bias2 + bias3 + bias4

    return DSTFSResult(
        sma=sma_values,
        hma=hma_values,
        sma_rising=sma_dir,
        hma_rising=hma_dir,
        bias1=bias1,
        bias2=bias2,
        bias3=bias3,
        bias4=bias4,
        total_bias=total_bias,
        close=close,
    )
