"""Tests for ATR Bollinger Bands volatility warning indicator."""

import numpy as np
import pytest

from options_analyzer.engine.atr_bollinger import (
    ATRBollingerResult,
    compute_atr_bollinger,
)
from tests.factories import make_ohlcv_arrays


class TestComputeATRBollinger:
    def setup_method(self) -> None:
        self.data = make_ohlcv_arrays(n=200, seed=42)
        self.result = compute_atr_bollinger(
            self.data["high"], self.data["low"], self.data["close"]
        )

    def test_returns_atr_bollinger_result(self) -> None:
        assert isinstance(self.result, ATRBollingerResult)

    def test_array_lengths_match_input(self) -> None:
        n = len(self.data["close"])
        assert len(self.result.atr_ema) == n
        assert len(self.result.bb_basis) == n
        assert len(self.result.bb_upper_1) == n
        assert len(self.result.bb_upper_2) == n
        assert len(self.result.bb_lower) == n
        assert len(self.result.severity) == n

    def test_upper2_above_upper1_above_basis(self) -> None:
        valid = (
            ~np.isnan(self.result.bb_upper_2)
            & ~np.isnan(self.result.bb_upper_1)
            & ~np.isnan(self.result.bb_basis)
        )
        np.testing.assert_array_less(
            self.result.bb_upper_1[valid], self.result.bb_upper_2[valid]
        )
        np.testing.assert_array_less(
            self.result.bb_basis[valid], self.result.bb_upper_1[valid]
        )

    def test_severity_values(self) -> None:
        valid = self.result.severity[~np.isnan(self.result.severity)]
        for v in valid:
            assert v in {0.0, 1.0, 2.0}

    def test_atr_ema_non_negative(self) -> None:
        valid = self.result.atr_ema[~np.isnan(self.result.atr_ema)]
        assert np.all(valid >= 0)

    def test_low_volatility_constant_prices(self) -> None:
        # Constant prices → TR=0 → atr_ema=0, bands=0
        # With >= comparison: 0 >= 0 is True → severity 2 (matches PineScript)
        n = 200
        close = np.full(n, 100.0)
        high = np.full(n, 100.0)
        low = np.full(n, 100.0)
        result = compute_atr_bollinger(high, low, close)
        valid = result.severity[~np.isnan(result.severity)]
        # Degenerate case: all zero → atr_ema == all bands → severity 2
        assert np.all(valid == 2.0)

    def test_custom_periods(self) -> None:
        result = compute_atr_bollinger(
            self.data["high"],
            self.data["low"],
            self.data["close"],
            atr_period=10,
            bb_period=10,
            bb_mult=1.5,
        )
        assert isinstance(result, ATRBollingerResult)

    def test_frozen_dataclass(self) -> None:
        with pytest.raises(AttributeError):
            self.result.severity = np.array([1.0])  # type: ignore[misc]

    def test_severity_2_above_upper2(self) -> None:
        """Severity 2 only when atr_ema >= bb_upper_2."""
        valid = ~np.isnan(self.result.severity) & ~np.isnan(self.result.bb_upper_2)
        sev2 = self.result.severity[valid] == 2.0
        if np.any(sev2):
            assert np.all(
                self.result.atr_ema[valid][sev2]
                >= self.result.bb_upper_2[valid][sev2]
            )

    def test_severity_boundary_at_upper2(self) -> None:
        """ATR exactly at upper_2 BB should give severity 2 (>=, not >)."""
        n = 200
        close = np.full(n, 100.0)
        high = np.full(n, 101.0)
        low = np.full(n, 99.0)
        result = compute_atr_bollinger(high, low, close)
        valid = ~np.isnan(result.severity) & ~np.isnan(result.bb_upper_2)
        # Find any point where atr_ema == bb_upper_2 exactly
        at_boundary = np.isclose(
            result.atr_ema[valid], result.bb_upper_2[valid], atol=1e-12
        )
        if np.any(at_boundary):
            assert np.all(result.severity[valid][at_boundary] == 2.0)

    def test_severity_boundary_at_upper1(self) -> None:
        """ATR exactly at upper_1 BB should give severity >= 1 (>=, not >)."""
        valid = ~np.isnan(self.result.severity) & ~np.isnan(self.result.bb_upper_1)
        at_boundary = np.isclose(
            self.result.atr_ema[valid], self.result.bb_upper_1[valid], atol=1e-12
        )
        if np.any(at_boundary):
            assert np.all(self.result.severity[valid][at_boundary] >= 1.0)
