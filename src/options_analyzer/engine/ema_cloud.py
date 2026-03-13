"""EMA Cloud + HMA direction indicator.

Translated from PineScript: EMA(8)/EMA(34) cloud with HMA(15) trend direction.
Cloud state: bullish when EMA-fast > EMA-slow, bearish otherwise.
HMA direction: +1 rising, -1 falling.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from options_analyzer.engine.ta_utils import direction, ema, hma


@dataclass(frozen=True)
class EMACloudResult:
    """Result of EMA Cloud + HMA computation."""

    ema_fast: npt.NDArray[np.float64]
    ema_slow: npt.NDArray[np.float64]
    cloud_bullish: npt.NDArray[np.float64]  # +1 bullish, -1 bearish, NaN warmup
    hma_values: npt.NDArray[np.float64]
    hma_direction: npt.NDArray[np.float64]  # +1 rising, -1 falling, NaN warmup


def compute_ema_cloud(
    close: npt.NDArray[np.float64],
    fast_period: int = 8,
    slow_period: int = 34,
    hma_period: int = 15,
) -> EMACloudResult:
    """Compute EMA Cloud and HMA direction.

    Parameters
    ----------
    close : array of closing prices
    fast_period : EMA fast period (default 8)
    slow_period : EMA slow period (default 34)
    hma_period : HMA period (default 15)

    Returns
    -------
    EMACloudResult with cloud state and HMA direction
    """
    ema_fast = ema(close, fast_period)
    ema_slow = ema(close, slow_period)

    # Cloud: bullish when fast > slow
    cloud_bullish = np.full_like(close, np.nan)
    valid = ~np.isnan(ema_fast) & ~np.isnan(ema_slow)
    cloud_bullish[valid] = np.where(
        ema_fast[valid] > ema_slow[valid], 1.0, -1.0
    )

    hma_values = hma(close, hma_period)
    hma_dir = direction(hma_values)

    return EMACloudResult(
        ema_fast=ema_fast,
        ema_slow=ema_slow,
        cloud_bullish=cloud_bullish,
        hma_values=hma_values,
        hma_direction=hma_dir,
    )
