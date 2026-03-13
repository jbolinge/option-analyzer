"""Tests for MC Warnings aggregation indicator."""

import numpy as np
import pytest

from options_analyzer.engine.atr_bollinger import compute_atr_bollinger
from options_analyzer.engine.force_index import compute_force_index_dual
from options_analyzer.engine.indicators import compute_dstfs
from options_analyzer.engine.ivts import compute_ivts
from options_analyzer.engine.mc_warnings import MCWarningsResult, compute_mc_warnings
from options_analyzer.engine.obv_bollinger import compute_obv_bollinger
from tests.factories import make_ohlcv_arrays


def _make_stress_scenario(
    include_dstfs: bool = False,
) -> MCWarningsResult:
    """All indicators in warning state."""
    n = 200
    # ATR: spike volatility
    high = np.full(n, 110.0)
    low = np.full(n, 90.0)
    close = np.full(n, 100.0)
    # Make a sudden vol spike
    high[-10:] = 200.0
    low[-10:] = 50.0
    atr = compute_atr_bollinger(high, low, close)

    # OBV: sudden selling
    rng = np.random.default_rng(42)
    obv_close = 100.0 + np.cumsum(rng.normal(0, 0.1, n))
    obv_vol = np.full(n, 100_000.0)
    obv_close[-10:] = np.linspace(obv_close[-11], obv_close[-11] - 30, 10)
    obv_vol[-10:] = 10_000_000.0
    obv_result = compute_obv_bollinger(obv_close, obv_vol)

    # IVTS: inverted
    vix = np.full(n, 30.0)
    vix3m = np.full(n, 20.0)
    ivts = compute_ivts(vix, vix3m)

    # Force Index: both selling
    fi_close1 = np.linspace(200, 100, n)
    fi_close2 = np.linspace(200, 100, n)
    fi_vol = np.full(n, 1_000_000.0)
    fi = compute_force_index_dual(fi_close1, fi_vol, fi_close2, fi_vol)

    dstfs = None
    if include_dstfs:
        # Bearish DSTFS — declining close
        dstfs_close = np.linspace(200, 100, n).astype(np.float64)
        dstfs = compute_dstfs(dstfs_close)

    return compute_mc_warnings(atr, obv_result, ivts, fi, dstfs)


def _make_calm_scenario() -> MCWarningsResult:
    """No indicators in warning state."""
    n = 200
    # ATR: low vol
    high = np.full(n, 101.0)
    low = np.full(n, 99.0)
    close = np.full(n, 100.0)
    atr = compute_atr_bollinger(high, low, close)

    # OBV: steady buying
    obv_close = np.linspace(100, 150, n)
    obv_vol = np.full(n, 100_000.0)
    obv_result = compute_obv_bollinger(obv_close, obv_vol)

    # IVTS: normal contango
    vix = np.full(n, 15.0)
    vix3m = np.full(n, 20.0)
    ivts = compute_ivts(vix, vix3m)

    # Force Index: both buying
    fi_close1 = np.linspace(100, 200, n)
    fi_close2 = np.linspace(100, 200, n)
    fi_vol = np.full(n, 1_000_000.0)
    fi = compute_force_index_dual(fi_close1, fi_vol, fi_close2, fi_vol)

    return compute_mc_warnings(atr, obv_result, ivts, fi)


class TestComputeMCWarnings:
    def test_returns_mc_warnings_result(self) -> None:
        result = _make_calm_scenario()
        assert isinstance(result, MCWarningsResult)

    def test_array_lengths_match(self) -> None:
        result = _make_calm_scenario()
        n = len(result.total)
        assert len(result.atr_severity) == n
        assert len(result.obv_severity) == n
        assert len(result.ivts_severity) == n
        assert len(result.fi_severity) == n
        assert len(result.dstfs_warning) == n

    def test_total_range_0_to_5(self) -> None:
        result = _make_stress_scenario(include_dstfs=True)
        assert np.all(result.total >= 0)
        assert np.all(result.total <= 5)

    def test_calm_total_zero(self) -> None:
        result = _make_calm_scenario()
        # Most of the calm scenario should have zero warnings
        assert result.total[-1] == 0.0

    def test_stress_total_positive(self) -> None:
        result = _make_stress_scenario()
        # End of stress scenario should have some warnings
        assert result.total[-1] >= 2.0

    def test_total_is_sum_of_binary_severities(self) -> None:
        result = _make_stress_scenario()
        idx = -1
        expected = 0.0
        for arr in [
            result.atr_severity,
            result.obv_severity,
            result.ivts_severity,
            result.fi_severity,
            result.dstfs_warning,
        ]:
            val = arr[idx]
            if not np.isnan(val) and val > 0:
                expected += 1.0
        assert result.total[idx] == pytest.approx(expected)

    def test_without_dstfs_default_zero(self) -> None:
        result = _make_calm_scenario()
        assert np.all(result.dstfs_warning == 0.0)

    def test_with_dstfs_bearish(self) -> None:
        result = _make_stress_scenario(include_dstfs=True)
        # Bearish DSTFS should produce some warnings
        valid = result.dstfs_warning[~np.isnan(result.dstfs_warning)]
        assert np.any(valid == 1.0)

    def test_frozen_dataclass(self) -> None:
        result = _make_calm_scenario()
        with pytest.raises(AttributeError):
            result.total = np.array([1.0])  # type: ignore[misc]

    def test_with_real_data(self) -> None:
        """Integration-style test with factory data."""
        data1 = make_ohlcv_arrays(n=200, seed=42)
        data2 = make_ohlcv_arrays(n=200, seed=99)

        atr = compute_atr_bollinger(data1["high"], data1["low"], data1["close"])
        obv_result = compute_obv_bollinger(data1["close"], data1["volume"])

        # Use close as proxy for VIX/VIX3M (just testing pipeline)
        ivts = compute_ivts(data1["close"], data2["close"])

        fi = compute_force_index_dual(
            data1["close"], data1["volume"],
            data2["close"], data2["volume"],
        )

        result = compute_mc_warnings(atr, obv_result, ivts, fi)
        assert isinstance(result, MCWarningsResult)
        assert np.all(result.total >= 0)
        assert np.all(result.total <= 5)
