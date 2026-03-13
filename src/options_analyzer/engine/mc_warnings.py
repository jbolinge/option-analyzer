"""Market Conditions Warnings aggregator.

Aggregates sub-indicator warnings into warning squares and totals:
1. ATR Bollinger (volatility) — severity 0/1/2
2. OBV Bollinger (volume distribution) — severity 0/1/2
3. IVTS (term structure) — severity 0/1/2
4. Force Index dual (selling pressure) — severity 0/1/2
5. DSTFS bias (trend) — binary 0/1

Total warnings range from 0 (all clear) to 5 (maximum stress),
counting each sub-indicator as 1 if severity > 0.
"""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from options_analyzer.engine.atr_bollinger import ATRBollingerResult
from options_analyzer.engine.force_index import ForceIndexDualResult
from options_analyzer.engine.indicators import DSTFSResult
from options_analyzer.engine.ivts import IVTSResult
from options_analyzer.engine.obv_bollinger import OBVBollingerResult


@dataclass(frozen=True)
class MCWarningsResult:
    """Result of MC Warnings aggregation."""

    atr_severity: npt.NDArray[np.float64]  # ATR Bollinger severity (0/1/2)
    obv_severity: npt.NDArray[np.float64]  # OBV Bollinger severity (0/1/2)
    ivts_severity: npt.NDArray[np.float64]  # IVTS severity (0/1/2)
    fi_severity: npt.NDArray[np.float64]  # Force Index dual severity (0/1/2)
    dstfs_warning: npt.NDArray[np.float64]  # DSTFS warning (1 if bias<0, else 0)
    total: npt.NDArray[np.float64]  # Sum of binary warnings (0-5)


def compute_mc_warnings(
    atr_result: ATRBollingerResult,
    obv_result: OBVBollingerResult,
    ivts_result: IVTSResult,
    fi_dual_result: ForceIndexDualResult,
    dstfs_result: DSTFSResult | None = None,
) -> MCWarningsResult:
    """Aggregate sub-indicator warnings into total warning count.

    Parameters
    ----------
    atr_result : ATR Bollinger result
    obv_result : OBV Bollinger result
    ivts_result : IVTS result
    fi_dual_result : Dual Force Index result
    dstfs_result : DSTFS result (optional — if None, dstfs_warning is 0)

    Returns
    -------
    MCWarningsResult with individual severities and total (0-5)
    """
    atr_sev = atr_result.severity
    obv_sev = obv_result.severity
    ivts_sev = ivts_result.severity
    fi_sev = fi_dual_result.severity

    # DSTFS warning: 1 if total_bias < 0, else 0
    if dstfs_result is not None:
        dstfs_w = np.full_like(atr_sev, np.nan)
        valid = ~np.isnan(dstfs_result.total_bias)
        dstfs_w[valid] = np.where(dstfs_result.total_bias[valid] < 0, 1.0, 0.0)
    else:
        dstfs_w = np.zeros_like(atr_sev)

    # Replace NaN with 0 for summation, then count binary (severity > 0 → 1)
    def _binary(arr: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        safe = np.where(np.isnan(arr), 0.0, arr)
        return np.where(safe > 0, 1.0, 0.0)

    total = (
        _binary(atr_sev)
        + _binary(obv_sev)
        + _binary(ivts_sev)
        + _binary(fi_sev)
        + _binary(dstfs_w)
    )

    return MCWarningsResult(
        atr_severity=atr_sev,
        obv_severity=obv_sev,
        ivts_severity=ivts_sev,
        fi_severity=fi_sev,
        dstfs_warning=dstfs_w,
        total=total,
    )
