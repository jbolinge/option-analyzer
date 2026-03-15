"""Candle bar and series domain models for historical price data."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

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


def align_series(
    *series: CandleSeries,
    method: Literal["intersect", "ffill"] = "ffill",
) -> tuple[CandleSeries, ...]:
    """Align multiple CandleSeries to shared timestamps.

    Args:
        series: Two or more CandleSeries to align.
        method: ``"ffill"`` (default) uses the union of all timestamps and
            forward-fills missing bars with the previous close (volume=0).
            ``"intersect"`` keeps only timestamps present in ALL series.

    Returns inputs unchanged if all series already share identical timestamps.
    """
    if len(series) <= 1:
        return series

    # Fast path: all series already have identical timestamps
    first_ts = series[0].timestamps
    if all(s.timestamps == first_ts for s in series[1:]):
        return series

    if method == "intersect":
        return _align_intersect(*series)
    return _align_ffill(*series)


def _align_intersect(*series: CandleSeries) -> tuple[CandleSeries, ...]:
    """Keep only timestamps present in ALL series."""
    timestamp_sets = [set(s.timestamps) for s in series]
    common = timestamp_sets[0]
    for ts_set in timestamp_sets[1:]:
        common = common & ts_set

    common_set = set(common)
    aligned = []
    for s in series:
        filtered_bars = [b for b in s.bars if b.timestamp in common_set]
        filtered_bars.sort(key=lambda b: b.timestamp)
        aligned.append(CandleSeries(bars=filtered_bars))

    return tuple(aligned)


def _align_ffill(*series: CandleSeries) -> tuple[CandleSeries, ...]:
    """Union of all timestamps, forward-filling gaps with previous close."""
    # Compute sorted union of all timestamps
    all_ts: set[datetime] = set()
    for s in series:
        all_ts.update(s.timestamps)
    sorted_ts = sorted(all_ts)

    aligned = []
    for s in series:
        ts_to_bar = {b.timestamp: b for b in s.bars}
        new_bars: list[CandleBar] = []
        prev_close: float | None = None
        symbol = s.bars[0].symbol if s.bars else ""

        for ts in sorted_ts:
            bar = ts_to_bar.get(ts)
            if bar is not None:
                new_bars.append(bar)
                prev_close = bar.close
            elif prev_close is not None:
                # Forward-fill: synthetic bar from previous close
                new_bars.append(
                    CandleBar(
                        symbol=symbol,
                        timestamp=ts,
                        open=prev_close,
                        high=prev_close,
                        low=prev_close,
                        close=prev_close,
                        volume=0,
                    )
                )
            # else: no previous data yet for this series — skip

        aligned.append(CandleSeries(bars=new_bars))

    return tuple(aligned)
