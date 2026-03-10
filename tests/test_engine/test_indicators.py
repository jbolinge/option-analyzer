"""Tests for DSTFS trend-following indicator engine."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from options_analyzer.engine.indicators import (
    DSTFSResult,
    compute_dstfs,
    hma,
    sma,
    wma,
)
from tests.factories import make_candle_series


class TestSMA:
    """Tests for SMA wrapper."""

    def test_output_length_matches_input(self) -> None:
        close = np.arange(100, dtype=np.float64)
        result = sma(close, period=10)
        assert len(result) == len(close)

    def test_nan_warmup(self) -> None:
        close = np.arange(20, dtype=np.float64)
        result = sma(close, period=10)
        assert np.all(np.isnan(result[:9]))
        assert not np.isnan(result[9])

    def test_constant_array_identity(self) -> None:
        close = np.full(50, 100.0)
        result = sma(close, period=10)
        valid = result[~np.isnan(result)]
        np.testing.assert_allclose(valid, 100.0)

    def test_known_value(self) -> None:
        close = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = sma(close, period=5)
        assert result[4] == pytest.approx(3.0)


class TestWMA:
    """Tests for WMA wrapper."""

    def test_output_length_matches_input(self) -> None:
        close = np.arange(50, dtype=np.float64)
        result = wma(close, period=10)
        assert len(result) == len(close)

    def test_constant_array_identity(self) -> None:
        close = np.full(50, 100.0)
        result = wma(close, period=10)
        valid = result[~np.isnan(result)]
        np.testing.assert_allclose(valid, 100.0)


class TestHMA:
    """Tests for HMA (Hull Moving Average)."""

    def test_output_length_matches_input(self) -> None:
        close = np.arange(100, dtype=np.float64)
        result = hma(close, period=15)
        assert len(result) == len(close)

    def test_faster_response_than_sma_on_step(self) -> None:
        close = np.concatenate([np.full(50, 100.0), np.full(50, 200.0)])
        hma_result = hma(close, period=15)
        sma_result = sma(close, period=15)
        # After step, HMA should reach 200 faster (at earlier index)
        hma_reach = np.where(~np.isnan(hma_result) & (hma_result > 190))[0]
        sma_reach = np.where(~np.isnan(sma_result) & (sma_result > 190))[0]
        assert len(hma_reach) > 0
        assert len(sma_reach) > 0
        assert hma_reach[0] < sma_reach[0]

    def test_constant_array_identity(self) -> None:
        close = np.full(50, 100.0)
        result = hma(close, period=15)
        valid = result[~np.isnan(result)]
        np.testing.assert_allclose(valid, 100.0)


class TestComputeDSTFS:
    """Tests for compute_dstfs composite indicator."""

    def setup_method(self) -> None:
        self.series = make_candle_series(n=200, seed=42)
        self.result = compute_dstfs(self.series.closes)

    def test_returns_dstfs_result(self) -> None:
        assert isinstance(self.result, DSTFSResult)

    def test_result_arrays_same_length(self) -> None:
        n = len(self.series.closes)
        assert len(self.result.sma) == n
        assert len(self.result.hma) == n
        assert len(self.result.total_bias) == n
        assert len(self.result.close) == n

    def test_bias_range(self) -> None:
        valid = self.result.total_bias[~np.isnan(self.result.total_bias)]
        assert np.all(valid >= -4)
        assert np.all(valid <= 4)

    def test_bias_values_in_valid_set(self) -> None:
        valid = self.result.total_bias[~np.isnan(self.result.total_bias)]
        for v in valid:
            assert v in {-4, -2, 0, 2, 4}

    def test_strong_uptrend_gives_positive_four(self) -> None:
        close = np.linspace(100, 300, 200)
        result = compute_dstfs(close)
        # At the end of a strong uptrend, total bias should be +4
        assert result.total_bias[-1] == 4

    def test_strong_downtrend_gives_negative_four(self) -> None:
        close = np.linspace(300, 100, 200)
        result = compute_dstfs(close)
        assert result.total_bias[-1] == -4

    def test_individual_biases_are_plus_minus_one(self) -> None:
        valid_mask = ~np.isnan(self.result.bias1)
        for bias in [
            self.result.bias1,
            self.result.bias2,
            self.result.bias3,
            self.result.bias4,
        ]:
            valid = bias[valid_mask]
            for v in valid:
                assert v in {-1, 1}

    def test_close_array_passthrough(self) -> None:
        np.testing.assert_array_equal(self.result.close, self.series.closes)


class TestDSTFSPropertyBased:
    """Property-based tests for DSTFS bias computation."""

    @settings(max_examples=20, deadline=None)
    @given(
        arrays(
            dtype=np.float64,
            shape=st.integers(min_value=60, max_value=200),
            elements=st.floats(
                min_value=50.0, max_value=10000.0, allow_nan=False, allow_infinity=False
            ),
        )
    )
    def test_bias_always_in_valid_set(self, close: np.ndarray) -> None:  # type: ignore[type-arg]
        result = compute_dstfs(close)
        valid = result.total_bias[~np.isnan(result.total_bias)]
        for v in valid:
            assert v in {-4, -2, 0, 2, 4}
