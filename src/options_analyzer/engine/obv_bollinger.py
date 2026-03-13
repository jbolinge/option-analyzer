"""OBV Bollinger Bands volume warning indicator.

Translated from PineScript: On-Balance Volume with Bollinger Bands.

NOTE: The original PineScript has a bug where ``spy_volume = close`` is used
instead of actual volume. This implementation uses actual volume correctly.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from options_analyzer.engine.ta_utils import obv, sma, stdev


@dataclass(frozen=True)
class OBVBollingerResult:
    """Result of OBV Bollinger computation."""

    obv: npt.NDArray[np.float64]  # On-Balance Volume
    bb_basis: npt.NDArray[np.float64]  # SMA of OBV (Bollinger midline)
    bb_upper: npt.NDArray[np.float64]  # Upper Bollinger Band
    bb_lower_1: npt.NDArray[np.float64]  # Lower Bollinger Band (1 stdev)
    bb_lower_2: npt.NDArray[np.float64]  # Lower Bollinger Band (2 stdev)
    severity: npt.NDArray[np.float64]  # 0=normal, 1=obv<lower_1, 2=obv<=lower_2


def compute_obv_bollinger(
    close: npt.NDArray[np.float64],
    volume: npt.NDArray[np.float64],
    bb_period: int = 20,
    bb_mult: float = 2.0,
) -> OBVBollingerResult:
    """Compute OBV Bollinger Bands.

    Parameters
    ----------
    close : closing prices
    volume : volume array
    bb_period : Bollinger Band SMA period (default 20)
    bb_mult : Bollinger Band standard deviation multiplier (default 2.0)

    Returns
    -------
    OBVBollingerResult with warning when OBV breaks below lower band
    """
    obv_values = obv(close, volume)

    bb_basis = sma(obv_values, bb_period)
    bb_std = stdev(obv_values, bb_period)

    bb_upper = bb_basis + bb_mult * bb_std
    bb_lower_1 = bb_basis - bb_std            # 1 stdev
    bb_lower_2 = bb_basis - bb_mult * bb_std  # 2 stdev (default bb_mult=2.0)

    # Severity: 0=normal, 1=obv<lower_1, 2=obv<=lower_2
    severity = np.full_like(close, np.nan)
    valid = ~np.isnan(obv_values) & ~np.isnan(bb_lower_2)
    severity[valid] = np.where(
        obv_values[valid] <= bb_lower_2[valid],
        2.0,
        np.where(obv_values[valid] < bb_lower_1[valid], 1.0, 0.0),
    )

    return OBVBollingerResult(
        obv=obv_values,
        bb_basis=bb_basis,
        bb_upper=bb_upper,
        bb_lower_1=bb_lower_1,
        bb_lower_2=bb_lower_2,
        severity=severity,
    )
