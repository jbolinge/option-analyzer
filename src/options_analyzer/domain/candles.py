"""Candle bar and series domain models for historical price data."""

from __future__ import annotations

from datetime import datetime

import numpy as np
import numpy.typing as npt
from pydantic import BaseModel, ConfigDict


class CandleBar(BaseModel):
    """A single OHLCV candle bar."""

    model_config = ConfigDict(frozen=True)

    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class CandleSeries(BaseModel):
    """Ordered sequence of candle bars with numpy property accessors."""

    model_config = ConfigDict(frozen=True)

    bars: list[CandleBar]

    def __len__(self) -> int:
        return len(self.bars)

    @property
    def closes(self) -> npt.NDArray[np.float64]:
        return np.array([b.close for b in self.bars], dtype=np.float64)

    @property
    def opens(self) -> npt.NDArray[np.float64]:
        return np.array([b.open for b in self.bars], dtype=np.float64)

    @property
    def highs(self) -> npt.NDArray[np.float64]:
        return np.array([b.high for b in self.bars], dtype=np.float64)

    @property
    def lows(self) -> npt.NDArray[np.float64]:
        return np.array([b.low for b in self.bars], dtype=np.float64)

    @property
    def volumes(self) -> npt.NDArray[np.float64]:
        return np.array([b.volume for b in self.bars], dtype=np.float64)

    @property
    def timestamps(self) -> list[datetime]:
        return [b.timestamp for b in self.bars]


def align_series(*series: CandleSeries) -> tuple[CandleSeries, ...]:
    """Align multiple CandleSeries to their common timestamps (intersection).

    Returns new series containing only bars at timestamps present in ALL inputs,
    preserving chronological order. Returns inputs unchanged if already aligned.
    """
    if len(series) <= 1:
        return series

    # Build timestamp sets and compute intersection
    timestamp_sets = [set(s.timestamps) for s in series]
    common = timestamp_sets[0]
    for ts_set in timestamp_sets[1:]:
        common = common & ts_set

    # Fast path: all series already have identical timestamps
    if all(len(common) == len(s) for s in series):
        # Verify actual timestamp equality (not just count)
        first_ts = series[0].timestamps
        if all(s.timestamps == first_ts for s in series[1:]):
            return series

    # Filter each series to common timestamps, preserving chronological order
    sorted_common = sorted(common)
    common_set = set(sorted_common)
    aligned = []
    for s in series:
        filtered_bars = [b for b in s.bars if b.timestamp in common_set]
        filtered_bars.sort(key=lambda b: b.timestamp)
        aligned.append(CandleSeries(bars=filtered_bars))

    return tuple(aligned)
