"""Tests for OBV Bollinger Bands volume warning indicator."""

import numpy as np
import pytest

from options_analyzer.engine.obv_bollinger import (
    OBVBollingerResult,
    compute_obv_bollinger,
)
from tests.factories import make_ohlcv_arrays


class TestComputeOBVBollinger:
    def setup_method(self) -> None:
        self.data = make_ohlcv_arrays(n=200, seed=42)
        self.result = compute_obv_bollinger(
            self.data["close"], self.data["volume"]
        )

    def test_returns_obv_bollinger_result(self) -> None:
        assert isinstance(self.result, OBVBollingerResult)

    def test_array_lengths_match_input(self) -> None:
        n = len(self.data["close"])
        assert len(self.result.obv) == n
        assert len(self.result.bb_basis) == n
        assert len(self.result.bb_upper) == n
        assert len(self.result.bb_lower_1) == n
        assert len(self.result.bb_lower_2) == n
        assert len(self.result.severity) == n

    def test_lower1_above_lower2(self) -> None:
        valid = (
            ~np.isnan(self.result.bb_lower_1)
            & ~np.isnan(self.result.bb_lower_2)
        )
        if np.any(valid):
            np.testing.assert_array_less(
                self.result.bb_lower_2[valid], self.result.bb_lower_1[valid]
            )

    def test_severity_values(self) -> None:
        valid = self.result.severity[~np.isnan(self.result.severity)]
        for v in valid:
            assert v in {0.0, 1.0, 2.0}

    def test_sudden_selling_triggers_warning(self) -> None:
        # Calm period then sudden heavy selling → OBV breaks below lower band
        n = 200
        rng = np.random.default_rng(42)
        # Flat period with small random changes
        close = 100.0 + np.cumsum(rng.normal(0, 0.1, n))
        volume = np.full(n, 100_000.0)
        # Sudden heavy selling in last 10 bars
        close[-10:] = np.linspace(close[-11], close[-11] - 30, 10)
        volume[-10:] = 10_000_000.0
        result = compute_obv_bollinger(close, volume)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.any(valid >= 1.0)

    def test_custom_periods(self) -> None:
        result = compute_obv_bollinger(
            self.data["close"],
            self.data["volume"],
            bb_period=10,
            bb_mult=1.5,
        )
        assert isinstance(result, OBVBollingerResult)

    def test_frozen_dataclass(self) -> None:
        with pytest.raises(AttributeError):
            self.result.obv = np.array([1.0])  # type: ignore[misc]
