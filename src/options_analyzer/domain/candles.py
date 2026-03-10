"""Candle bar and series domain models for historical price data."""

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
