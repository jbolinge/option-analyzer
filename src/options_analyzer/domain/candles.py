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


def _normalize_daily_ts(ts: datetime) -> datetime:
    """Normalize a timestamp to 16:00 UTC (US equity market close).

    Daily candle bars represent whole days — the time component is meaningless
    for alignment.  Normalizing to market close ensures that bars from different
    sources (e.g. ``2026-03-14 00:00`` and ``2026-03-14 16:00``) map to the
    same key and align correctly with intraday data.
    """
    return ts.replace(hour=16, minute=0, second=0, microsecond=0)


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
    """Union of all timestamps, forward-filling gaps with previous close.

    Timestamps are normalized to midnight UTC before computing the union so
    that bars for the same calendar day (but different time components) are
    treated as a single day.
    """
    # Compute sorted union of *normalized* timestamps
    all_norm: set[datetime] = set()
    for s in series:
        all_norm.update(_normalize_daily_ts(t) for t in s.timestamps)
    sorted_ts = sorted(all_norm)

    aligned = []
    for s in series:
        # Build lookup keyed by normalized timestamp
        norm_to_bar = {_normalize_daily_ts(b.timestamp): b for b in s.bars}
        new_bars: list[CandleBar] = []
        prev_close: float | None = None
        symbol = s.bars[0].symbol if s.bars else ""

        for ts in sorted_ts:
            bar = norm_to_bar.get(ts)
            if bar is not None:
                # Keep original bar data but normalise its timestamp
                if bar.timestamp != ts:
                    bar = bar.model_copy(update={"timestamp": ts})
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
