"""Tests for shared TA utility primitives."""

import numpy as np
import pytest

from options_analyzer.engine.ta_utils import (
    direction,
    ema,
    hma,
    obv,
    pct_change,
    rsi,
    sma,
    stdev,
    true_range,
    wma,
)


class TestSMA:
    def test_output_length(self) -> None:
        close = np.arange(100, dtype=np.float64)
        assert len(sma(close, 10)) == 100

    def test_nan_warmup(self) -> None:
        close = np.arange(20, dtype=np.float64)
        result = sma(close, 10)
        assert np.all(np.isnan(result[:9]))
        assert not np.isnan(result[9])

    def test_constant_identity(self) -> None:
        close = np.full(50, 42.0)
        valid = sma(close, 5)[~np.isnan(sma(close, 5))]
        np.testing.assert_allclose(valid, 42.0)

    def test_known_value(self) -> None:
        close = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        assert sma(close, 5)[4] == pytest.approx(3.0)


class TestWMA:
    def test_output_length(self) -> None:
        assert len(wma(np.arange(50, dtype=np.float64), 10)) == 50

    def test_constant_identity(self) -> None:
        close = np.full(50, 100.0)
        valid = wma(close, 10)[~np.isnan(wma(close, 10))]
        np.testing.assert_allclose(valid, 100.0)


class TestEMA:
    def test_output_length(self) -> None:
        close = np.arange(100, dtype=np.float64)
        assert len(ema(close, 10)) == 100

    def test_nan_warmup(self) -> None:
        close = np.arange(20, dtype=np.float64)
        result = ema(close, 10)
        assert np.all(np.isnan(result[:9]))
        assert not np.isnan(result[9])

    def test_constant_identity(self) -> None:
        close = np.full(50, 77.0)
        valid = ema(close, 10)[~np.isnan(ema(close, 10))]
        np.testing.assert_allclose(valid, 77.0)

    def test_reacts_faster_than_sma(self) -> None:
        close = np.concatenate([np.full(50, 100.0), np.full(50, 200.0)])
        ema_r = ema(close, 20)
        sma_r = sma(close, 20)
        # EMA should be closer to 200 at some point before SMA
        idx = 60
        assert ema_r[idx] > sma_r[idx]


class TestHMA:
    def test_output_length(self) -> None:
        assert len(hma(np.arange(100, dtype=np.float64), 15)) == 100

    def test_constant_identity(self) -> None:
        close = np.full(50, 100.0)
        valid = hma(close, 15)[~np.isnan(hma(close, 15))]
        np.testing.assert_allclose(valid, 100.0)


class TestRSI:
    def test_output_length(self) -> None:
        close = np.arange(100, dtype=np.float64)
        assert len(rsi(close, 14)) == 100

    def test_bounded_0_100(self) -> None:
        rng = np.random.default_rng(42)
        close = 100 + np.cumsum(rng.normal(0, 1, 200))
        result = rsi(close, 14)
        valid = result[~np.isnan(result)]
        assert np.all(valid >= 0)
        assert np.all(valid <= 100)

    def test_strong_uptrend_high(self) -> None:
        close = np.linspace(100, 200, 100)
        result = rsi(close, 14)
        assert result[-1] > 90

    def test_strong_downtrend_low(self) -> None:
        close = np.linspace(200, 100, 100)
        result = rsi(close, 14)
        assert result[-1] < 10


class TestStdev:
    def test_output_length(self) -> None:
        data = np.arange(50, dtype=np.float64)
        assert len(stdev(data, 10)) == 50

    def test_constant_zero(self) -> None:
        data = np.full(50, 42.0)
        result = stdev(data, 10)
        valid = result[~np.isnan(result)]
        np.testing.assert_allclose(valid, 0.0, atol=1e-10)

    def test_known_value(self) -> None:
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = stdev(data, 5)
        expected = np.std([1, 2, 3, 4, 5])
        assert result[4] == pytest.approx(expected, abs=0.01)


class TestTrueRange:
    def test_output_length(self) -> None:
        h = np.array([12.0, 13.0, 14.0])
        l = np.array([10.0, 11.0, 12.0])
        c = np.array([11.0, 12.0, 13.0])
        assert len(true_range(h, l, c)) == 3

    def test_first_is_nan(self) -> None:
        h = np.array([12.0, 13.0])
        l = np.array([10.0, 11.0])
        c = np.array([11.0, 12.0])
        assert np.isnan(true_range(h, l, c)[0])

    def test_simple_case(self) -> None:
        # TR = max(H-L, |H-Cprev|, |L-Cprev|)
        # bar 1: H=15, L=11, Cprev=11 → max(4, 4, 0) = 4
        h = np.array([12.0, 15.0])
        l = np.array([10.0, 11.0])
        c = np.array([11.0, 13.0])
        assert true_range(h, l, c)[1] == pytest.approx(4.0)

    def test_gap_up(self) -> None:
        # Gap up: H=25, L=22, Cprev=10 → max(3, 15, 12) = 15
        h = np.array([12.0, 25.0])
        l = np.array([10.0, 22.0])
        c = np.array([10.0, 24.0])
        assert true_range(h, l, c)[1] == pytest.approx(15.0)


class TestOBV:
    def test_output_length(self) -> None:
        close = np.array([10.0, 11.0, 10.5, 12.0])
        vol = np.array([100.0, 200.0, 150.0, 300.0])
        assert len(obv(close, vol)) == 4

    def test_starts_at_zero(self) -> None:
        close = np.array([10.0, 11.0])
        vol = np.array([100.0, 200.0])
        assert obv(close, vol)[0] == 0.0

    def test_up_adds_volume(self) -> None:
        close = np.array([10.0, 11.0])
        vol = np.array([100.0, 200.0])
        assert obv(close, vol)[1] == 200.0

    def test_down_subtracts_volume(self) -> None:
        close = np.array([11.0, 10.0])
        vol = np.array([100.0, 200.0])
        assert obv(close, vol)[1] == -200.0

    def test_flat_no_change(self) -> None:
        close = np.array([10.0, 10.0])
        vol = np.array([100.0, 200.0])
        assert obv(close, vol)[1] == 0.0

    def test_cumulative(self) -> None:
        close = np.array([10.0, 11.0, 12.0, 11.0])
        vol = np.array([100.0, 200.0, 300.0, 150.0])
        result = obv(close, vol)
        # 0 + 200 + 300 - 150 = 350
        assert result[3] == pytest.approx(350.0)


class TestPctChange:
    def test_output_length(self) -> None:
        data = np.array([100.0, 110.0, 105.0])
        assert len(pct_change(data)) == 3

    def test_first_is_nan(self) -> None:
        data = np.array([100.0, 110.0])
        assert np.isnan(pct_change(data)[0])

    def test_known_value(self) -> None:
        data = np.array([100.0, 110.0])
        assert pct_change(data)[1] == pytest.approx(0.1)

    def test_multi_period(self) -> None:
        data = np.array([100.0, 110.0, 121.0])
        result = pct_change(data, periods=2)
        assert np.isnan(result[0])
        assert np.isnan(result[1])
        assert result[2] == pytest.approx(0.21)


class TestDirection:
    def test_output_length(self) -> None:
        arr = np.array([1.0, 2.0, 3.0])
        assert len(direction(arr)) == 3

    def test_first_is_nan(self) -> None:
        arr = np.array([1.0, 2.0])
        assert np.isnan(direction(arr)[0])

    def test_rising(self) -> None:
        arr = np.array([1.0, 2.0, 3.0])
        d = direction(arr)
        assert d[1] == 1.0
        assert d[2] == 1.0

    def test_falling(self) -> None:
        arr = np.array([3.0, 2.0, 1.0])
        d = direction(arr)
        assert d[1] == -1.0
        assert d[2] == -1.0

    def test_flat_is_falling(self) -> None:
        arr = np.array([1.0, 1.0])
        assert direction(arr)[1] == -1.0

    def test_nan_propagation(self) -> None:
        arr = np.array([1.0, np.nan, 3.0])
        d = direction(arr)
        assert np.isnan(d[1])
        assert np.isnan(d[2])
