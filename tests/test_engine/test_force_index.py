"""Tests for Elder's Force Index indicator."""

import numpy as np
import pytest

from options_analyzer.engine.force_index import (
    ForceIndexDualResult,
    ForceIndexResult,
    compute_force_index,
    compute_force_index_dual,
)
from tests.factories import make_ohlcv_arrays


class TestComputeForceIndex:
    def setup_method(self) -> None:
        self.data = make_ohlcv_arrays(n=200, seed=42)
        self.result = compute_force_index(
            self.data["close"], self.data["volume"]
        )

    def test_returns_force_index_result(self) -> None:
        assert isinstance(self.result, ForceIndexResult)

    def test_array_lengths_match_input(self) -> None:
        n = len(self.data["close"])
        assert len(self.result.raw) == n
        assert len(self.result.smoothed) == n
        assert len(self.result.warning) == n

    def test_raw_first_is_nan(self) -> None:
        assert np.isnan(self.result.raw[0])

    def test_warning_binary(self) -> None:
        valid = self.result.warning[~np.isnan(self.result.warning)]
        for v in valid:
            assert v in {0.0, 1.0}

    def test_raw_known_value(self) -> None:
        close = np.array([100.0, 102.0, 101.0])
        volume = np.array([1000.0, 2000.0, 1500.0])
        result = compute_force_index(close, volume, period=2)
        # bar 1: (102-100)*2000 = 4000
        assert result.raw[1] == pytest.approx(4000.0)
        # bar 2: (101-102)*1500 = -1500
        assert result.raw[2] == pytest.approx(-1500.0)

    def test_strong_selling_gives_warning(self) -> None:
        n = 200
        close = np.linspace(200, 100, n)
        volume = np.full(n, 1_000_000.0)
        result = compute_force_index(close, volume)
        # Strong selling → negative force → warning
        valid = result.warning[~np.isnan(result.warning)]
        assert np.all(valid == 1.0)

    def test_strong_buying_no_warning(self) -> None:
        n = 200
        close = np.linspace(100, 200, n)
        volume = np.full(n, 1_000_000.0)
        result = compute_force_index(close, volume)
        valid = result.warning[~np.isnan(result.warning)]
        assert np.all(valid == 0.0)

    def test_frozen_dataclass(self) -> None:
        with pytest.raises(AttributeError):
            self.result.raw = np.array([1.0])  # type: ignore[misc]


class TestComputeForceIndexDual:
    def setup_method(self) -> None:
        self.data1 = make_ohlcv_arrays(n=200, seed=42)
        self.data2 = make_ohlcv_arrays(n=200, seed=99)
        self.result = compute_force_index_dual(
            self.data1["close"],
            self.data1["volume"],
            self.data2["close"],
            self.data2["volume"],
        )

    def test_returns_dual_result(self) -> None:
        assert isinstance(self.result, ForceIndexDualResult)
        assert isinstance(self.result.primary, ForceIndexResult)
        assert isinstance(self.result.secondary, ForceIndexResult)

    def test_severity_values(self) -> None:
        valid = self.result.severity[~np.isnan(self.result.severity)]
        for v in valid:
            assert v in {0.0, 1.0, 2.0}

    def test_both_selling_severity_2(self) -> None:
        n = 200
        close1 = np.linspace(200, 100, n)
        close2 = np.linspace(200, 100, n)
        vol = np.full(n, 1_000_000.0)
        result = compute_force_index_dual(close1, vol, close2, vol)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 2.0)

    def test_one_buying_one_selling_severity_1(self) -> None:
        n = 200
        close1 = np.linspace(100, 200, n)  # buying
        close2 = np.linspace(200, 100, n)  # selling
        vol = np.full(n, 1_000_000.0)
        result = compute_force_index_dual(close1, vol, close2, vol)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 1.0)

    def test_both_buying_severity_0(self) -> None:
        n = 200
        close1 = np.linspace(100, 200, n)
        close2 = np.linspace(100, 200, n)
        vol = np.full(n, 1_000_000.0)
        result = compute_force_index_dual(close1, vol, close2, vol)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 0.0)
