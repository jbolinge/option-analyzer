"""Shared technical analysis primitives.

Pure functions wrapping TA-Lib and numpy for use across all indicator engines.
"""

import numpy as np
import numpy.typing as npt
import talib


def sma(
    data: npt.NDArray[np.float64], period: int = 50
) -> npt.NDArray[np.float64]:
    """Simple Moving Average via TA-Lib."""
    result: npt.NDArray[np.float64] = talib.SMA(data, timeperiod=period)
    return result


def wma(
    data: npt.NDArray[np.float64], period: int
) -> npt.NDArray[np.float64]:
    """Weighted Moving Average via TA-Lib."""
    result: npt.NDArray[np.float64] = talib.WMA(data, timeperiod=period)
    return result


def ema(
    data: npt.NDArray[np.float64], period: int
) -> npt.NDArray[np.float64]:
    """Exponential Moving Average via TA-Lib."""
    result: npt.NDArray[np.float64] = talib.EMA(data, timeperiod=period)
    return result


def hma(
    data: npt.NDArray[np.float64], period: int = 15
) -> npt.NDArray[np.float64]:
    """Hull Moving Average: WMA(2*WMA(n/2) - WMA(n), sqrt(n))."""
    half_period = max(int(period / 2), 1)
    sqrt_period = max(int(np.sqrt(period)), 1)

    wma_half = wma(data, half_period)
    wma_full = wma(data, period)

    diff = 2.0 * wma_half - wma_full
    result: npt.NDArray[np.float64] = wma(diff, sqrt_period)
    return result


def rsi(
    data: npt.NDArray[np.float64], period: int = 14
) -> npt.NDArray[np.float64]:
    """Relative Strength Index via TA-Lib."""
    result: npt.NDArray[np.float64] = talib.RSI(data, timeperiod=period)
    return result


def stdev(
    data: npt.NDArray[np.float64], period: int, nbdev: float = 1.0
) -> npt.NDArray[np.float64]:
    """Rolling standard deviation via TA-Lib."""
    result: npt.NDArray[np.float64] = talib.STDDEV(data, timeperiod=period, nbdev=nbdev)
    return result


def true_range(
    high: npt.NDArray[np.float64],
    low: npt.NDArray[np.float64],
    close: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """True Range: max(H-L, |H-Cprev|, |L-Cprev|).

    First element is NaN (no previous close).
    """
    tr = np.full_like(close, np.nan)
    for i in range(1, len(close)):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i - 1])
        lc = abs(low[i] - close[i - 1])
        tr[i] = max(hl, hc, lc)
    return tr


def obv(
    close: npt.NDArray[np.float64],
    volume: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """On-Balance Volume: cumulative sum of signed volume."""
    result = np.zeros_like(close)
    for i in range(1, len(close)):
        if close[i] > close[i - 1]:
            result[i] = result[i - 1] + volume[i]
        elif close[i] < close[i - 1]:
            result[i] = result[i - 1] - volume[i]
        else:
            result[i] = result[i - 1]
    return result


def pct_change(
    data: npt.NDArray[np.float64], periods: int = 1
) -> npt.NDArray[np.float64]:
    """Percent change over *periods* bars. First *periods* values are NaN."""
    result = np.full_like(data, np.nan)
    for i in range(periods, len(data)):
        if data[i - periods] != 0:
            result[i] = (data[i] - data[i - periods]) / data[i - periods]
        else:
            result[i] = 0.0
    return result


def direction(
    arr: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """Compute direction: +1 if rising, -1 if falling. NaN where input is NaN."""
    d = np.full_like(arr, np.nan)
    for i in range(1, len(arr)):
        if np.isnan(arr[i]) or np.isnan(arr[i - 1]):
            d[i] = np.nan
        elif arr[i] > arr[i - 1]:
            d[i] = 1.0
        else:
            d[i] = -1.0
    return d
