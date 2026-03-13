"""Tests for EMA Cloud + HMA direction indicator."""

import numpy as np
import pytest

from options_analyzer.engine.ema_cloud import EMACloudResult, compute_ema_cloud
from tests.factories import make_candle_series


class TestComputeEMACloud:
    def setup_method(self) -> None:
        self.series = make_candle_series(n=200, seed=42)
        self.result = compute_ema_cloud(self.series.closes)

    def test_returns_ema_cloud_result(self) -> None:
        assert isinstance(self.result, EMACloudResult)

    def test_array_lengths_match_input(self) -> None:
        n = len(self.series.closes)
        assert len(self.result.ema_fast) == n
        assert len(self.result.ema_slow) == n
        assert len(self.result.cloud_bullish) == n
        assert len(self.result.hma_values) == n
        assert len(self.result.hma_direction) == n

    def test_cloud_bullish_values(self) -> None:
        valid = self.result.cloud_bullish[~np.isnan(self.result.cloud_bullish)]
        for v in valid:
            assert v in {-1.0, 1.0}

    def test_hma_direction_values(self) -> None:
        valid = self.result.hma_direction[~np.isnan(self.result.hma_direction)]
        for v in valid:
            assert v in {-1.0, 1.0}

    def test_strong_uptrend_bullish_cloud(self) -> None:
        close = np.linspace(100, 300, 200)
        result = compute_ema_cloud(close)
        # In uptrend, cloud should be bullish at the end
        assert result.cloud_bullish[-1] == 1.0

    def test_strong_downtrend_bearish_cloud(self) -> None:
        close = np.linspace(300, 100, 200)
        result = compute_ema_cloud(close)
        assert result.cloud_bullish[-1] == -1.0

    def test_strong_uptrend_hma_rising(self) -> None:
        close = np.linspace(100, 300, 200)
        result = compute_ema_cloud(close)
        assert result.hma_direction[-1] == 1.0

    def test_custom_periods(self) -> None:
        result = compute_ema_cloud(
            self.series.closes, fast_period=5, slow_period=20, hma_period=10
        )
        assert isinstance(result, EMACloudResult)
        assert len(result.ema_fast) == len(self.series.closes)

    def test_fast_ema_has_less_warmup_than_slow(self) -> None:
        close = np.arange(100, dtype=np.float64)
        result = compute_ema_cloud(close, fast_period=8, slow_period=34)
        fast_valid_start = np.argmax(~np.isnan(result.ema_fast))
        slow_valid_start = np.argmax(~np.isnan(result.ema_slow))
        assert fast_valid_start < slow_valid_start

    def test_frozen_dataclass(self) -> None:
        with pytest.raises(AttributeError):
            self.result.ema_fast = np.array([1.0])  # type: ignore[misc]
