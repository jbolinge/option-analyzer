"""Tests for IVTS (Implied Volatility Term Structure) warning indicator."""

import numpy as np
import pytest

from options_analyzer.engine.ivts import IVTSResult, compute_ivts


def _make_vix_arrays(
    n: int = 100,
    vix_base: float = 20.0,
    vix3m_base: float = 22.0,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray]:
    """Create synthetic VIX and VIX3M arrays."""
    rng = np.random.default_rng(seed)
    vix = vix_base + np.cumsum(rng.normal(0, 0.5, n))
    vix3m = vix3m_base + np.cumsum(rng.normal(0, 0.3, n))
    # Keep positive
    vix = np.clip(vix, 10.0, 80.0)
    vix3m = np.clip(vix3m, 10.0, 80.0)
    return vix, vix3m


class TestComputeIVTS:
    def setup_method(self) -> None:
        self.vix, self.vix3m = _make_vix_arrays(n=200)
        self.result = compute_ivts(self.vix, self.vix3m)

    def test_returns_ivts_result(self) -> None:
        assert isinstance(self.result, IVTSResult)

    def test_array_lengths_match_input(self) -> None:
        n = len(self.vix)
        assert len(self.result.ratio) == n
        assert len(self.result.smoothed) == n
        assert len(self.result.severity) == n

    def test_ratio_positive(self) -> None:
        valid = self.result.ratio[~np.isnan(self.result.ratio)]
        assert np.all(valid > 0)

    def test_severity_values(self) -> None:
        valid = self.result.severity[~np.isnan(self.result.severity)]
        for v in valid:
            assert v in {0.0, 1.0, 2.0}

    def test_normal_contango_no_warning(self) -> None:
        # VIX < VIX3M → ratio < 0.9 → severity 0
        n = 200
        vix = np.full(n, 15.0)
        vix3m = np.full(n, 20.0)
        result = compute_ivts(vix, vix3m)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 0.0)

    def test_inverted_term_structure_severity_2(self) -> None:
        # VIX > VIX3M → ratio > 1 → severity 2
        n = 200
        vix = np.full(n, 30.0)
        vix3m = np.full(n, 20.0)
        result = compute_ivts(vix, vix3m)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 2.0)

    def test_mid_range_severity_1(self) -> None:
        # ratio ~0.95 → between 0.9 and 1.0 → severity 1
        n = 200
        vix = np.full(n, 19.0)
        vix3m = np.full(n, 20.0)  # ratio = 0.95
        result = compute_ivts(vix, vix3m)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 1.0)

    def test_ratio_known_value(self) -> None:
        vix = np.full(20, 25.0)
        vix3m = np.full(20, 20.0)
        result = compute_ivts(vix, vix3m)
        np.testing.assert_allclose(
            result.ratio, 1.25, atol=1e-10
        )

    def test_zero_vix3m_produces_nan(self) -> None:
        vix = np.array([20.0, 25.0])
        vix3m = np.array([0.0, 20.0])
        result = compute_ivts(vix, vix3m)
        assert np.isnan(result.ratio[0])
        assert result.ratio[1] == pytest.approx(1.25)

    def test_custom_threshold(self) -> None:
        n = 200
        vix = np.full(n, 18.0)
        vix3m = np.full(n, 20.0)
        # ratio = 0.9, threshold=0.85 → severity 2 (>= threshold)
        result = compute_ivts(vix, vix3m, threshold=0.85)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 2.0)

    def test_severity_uses_raw_ratio_not_smoothed(self) -> None:
        """Severity should be based on raw ratio, not smoothed SMA."""
        # Create data where raw ratio crosses threshold but SMA doesn't
        n = 20
        # Start with low ratio, then spike — raw crosses 1.0 before SMA does
        vix = np.concatenate([np.full(15, 15.0), np.full(5, 25.0)])
        vix3m = np.full(n, 20.0)
        result = compute_ivts(vix, vix3m, smooth_period=5)
        # At index 15 (first spike), raw ratio = 1.25, but SMA still < 1.0
        # Severity should be 2 based on raw ratio
        assert result.ratio[15] == pytest.approx(1.25)
        assert result.severity[15] == 2.0

    def test_severity_boundary_at_threshold(self) -> None:
        """Ratio exactly at threshold should give severity 2 (>=)."""
        n = 200
        vix = np.full(n, 20.0)
        vix3m = np.full(n, 20.0)  # ratio = 1.0 exactly
        result = compute_ivts(vix, vix3m, threshold=1.0)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 2.0)

    def test_severity_boundary_at_0_9(self) -> None:
        """Ratio exactly at 0.9 should give severity 1 (>=)."""
        n = 200
        vix = np.full(n, 18.0)
        vix3m = np.full(n, 20.0)  # ratio = 0.9 exactly
        result = compute_ivts(vix, vix3m)
        valid = result.severity[~np.isnan(result.severity)]
        assert np.all(valid == 1.0)

    def test_frozen_dataclass(self) -> None:
        with pytest.raises(AttributeError):
            self.result.ratio = np.array([1.0])  # type: ignore[misc]
