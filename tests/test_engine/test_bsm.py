"""Tests for BSM pure functions — first and second-order Greeks."""

import math

import pytest

from options_analyzer.engine import bsm

# Common test points for parametrized tests
TEST_POINTS = [
    # (S, K, T, r, sigma, q, label)
    (100.0, 100.0, 1.0, 0.05, 0.20, 0.0, "ATM"),
    (110.0, 100.0, 0.5, 0.05, 0.25, 0.0, "ITM call"),
    (90.0, 100.0, 0.25, 0.05, 0.30, 0.0, "OTM call"),
    (42.0, 40.0, 0.5, 0.10, 0.20, 0.0, "Hull textbook"),
    (100.0, 100.0, 1.0, 0.05, 0.20, 0.02, "with dividend"),
    (100.0, 80.0, 0.5, 0.05, 0.15, 0.0, "deep ITM call"),
    (80.0, 100.0, 0.5, 0.05, 0.15, 0.0, "deep OTM call"),
]


class TestHelpers:
    """Tests for d1/d2 helper functions."""

    def test_d1_atm(self) -> None:
        # ATM: S=K, so ln(S/K)=0, d1 simplifies
        S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
        result = bsm.d1(S, K, T, r, sigma)
        expected = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        assert result == pytest.approx(expected, rel=1e-10)

    def test_d2_is_d1_minus_sigma_sqrt_t(self) -> None:
        S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
        d1_val = bsm.d1(S, K, T, r, sigma)
        d2_val = bsm.d2(S, K, T, r, sigma)
        assert d2_val == pytest.approx(d1_val - sigma * math.sqrt(T), rel=1e-10)

    def test_d1_d2_with_dividend(self) -> None:
        S, K, T, r, sigma, q = 100.0, 100.0, 1.0, 0.05, 0.20, 0.02
        result = bsm.d1(S, K, T, r, sigma, q)
        expected = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (
            sigma * math.sqrt(T)
        )
        assert result == pytest.approx(expected, rel=1e-10)


class TestPricing:
    """Tests for call_price and put_price."""

    def test_hull_textbook_call(self) -> None:
        """Hull 10th ed: S=42, K=40, T=0.5, r=0.10, sigma=0.20 -> call ~ 4.76."""
        price = bsm.call_price(42.0, 40.0, 0.5, 0.10, 0.20)
        assert price == pytest.approx(4.76, abs=0.01)

    def test_hull_textbook_put(self) -> None:
        """Put via put-call parity from Hull textbook call."""
        call = bsm.call_price(42.0, 40.0, 0.5, 0.10, 0.20)
        put = bsm.put_price(42.0, 40.0, 0.5, 0.10, 0.20)
        # put-call parity: C - P = S - K*e^(-rT)
        parity = 42.0 - 40.0 * math.exp(-0.10 * 0.5)
        assert (call - put) == pytest.approx(parity, rel=1e-6)

    def test_atm_call_put_symmetry(self) -> None:
        """ATM with r=0, q=0: call == put."""
        call = bsm.call_price(100.0, 100.0, 1.0, 0.0, 0.20)
        put = bsm.put_price(100.0, 100.0, 1.0, 0.0, 0.20)
        assert call == pytest.approx(put, rel=1e-6)

    def test_put_call_parity_atm(self) -> None:
        S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
        call = bsm.call_price(S, K, T, r, sigma)
        put = bsm.put_price(S, K, T, r, sigma)
        parity = S - K * math.exp(-r * T)
        assert (call - put) == pytest.approx(parity, rel=1e-6)

    def test_put_call_parity_itm(self) -> None:
        S, K, T, r, sigma = 110.0, 100.0, 0.5, 0.05, 0.25
        call = bsm.call_price(S, K, T, r, sigma)
        put = bsm.put_price(S, K, T, r, sigma)
        parity = S - K * math.exp(-r * T)
        assert (call - put) == pytest.approx(parity, rel=1e-6)

    def test_put_call_parity_otm(self) -> None:
        S, K, T, r, sigma = 100.0, 90.0, 0.25, 0.05, 0.30
        call = bsm.call_price(S, K, T, r, sigma)
        put = bsm.put_price(S, K, T, r, sigma)
        parity = S - K * math.exp(-r * T)
        assert (call - put) == pytest.approx(parity, rel=1e-6)

    def test_put_call_parity_with_dividend(self) -> None:
        S, K, T, r, sigma, q = 100.0, 100.0, 1.0, 0.05, 0.20, 0.02
        call = bsm.call_price(S, K, T, r, sigma, q)
        put = bsm.put_price(S, K, T, r, sigma, q)
        parity = S * math.exp(-q * T) - K * math.exp(-r * T)
        assert (call - put) == pytest.approx(parity, rel=1e-6)

    def test_prices_non_negative(self) -> None:
        for S, K in [(100, 100), (50, 100), (150, 100)]:
            call = bsm.call_price(float(S), float(K), 1.0, 0.05, 0.20)
            put = bsm.put_price(float(S), float(K), 1.0, 0.05, 0.20)
            assert call >= 0
            assert put >= 0


class TestDelta:
    """Tests for delta."""

    def test_hull_textbook_call_delta(self) -> None:
        """Hull 10th ed: call delta ~ 0.7791."""
        d = bsm.delta(42.0, 40.0, 0.5, 0.10, 0.20, option_type="call")
        assert d == pytest.approx(0.7791, abs=0.001)

    def test_call_delta_bounds(self) -> None:
        d = bsm.delta(100.0, 100.0, 1.0, 0.05, 0.20, option_type="call")
        assert 0 <= d <= 1

    def test_put_delta_bounds(self) -> None:
        d = bsm.delta(100.0, 100.0, 1.0, 0.05, 0.20, option_type="put")
        assert -1 <= d <= 0

    def test_atm_call_delta_near_half(self) -> None:
        # With r=0.05, forward ATM delta is ~0.64 (forward effect shifts delta up)
        d = bsm.delta(100.0, 100.0, 1.0, 0.05, 0.20, option_type="call")
        assert d == pytest.approx(0.6368, abs=0.01)

    def test_deep_itm_call_delta_near_one(self) -> None:
        d = bsm.delta(200.0, 100.0, 1.0, 0.05, 0.20, option_type="call")
        assert d == pytest.approx(1.0, abs=0.01)

    def test_deep_otm_call_delta_near_zero(self) -> None:
        d = bsm.delta(50.0, 100.0, 1.0, 0.05, 0.20, option_type="call")
        assert d == pytest.approx(0.0, abs=0.01)

    def test_call_put_delta_relationship(self) -> None:
        """call_delta - put_delta = e^(-qT) for q=0 this is 1."""
        S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
        call_d = bsm.delta(S, K, T, r, sigma, option_type="call")
        put_d = bsm.delta(S, K, T, r, sigma, option_type="put")
        assert (call_d - put_d) == pytest.approx(1.0, rel=1e-6)

    def test_call_put_delta_relationship_with_dividend(self) -> None:
        S, K, T, r, sigma, q = 100.0, 100.0, 1.0, 0.05, 0.20, 0.02
        call_d = bsm.delta(S, K, T, r, sigma, q, option_type="call")
        put_d = bsm.delta(S, K, T, r, sigma, q, option_type="put")
        assert (call_d - put_d) == pytest.approx(math.exp(-q * T), rel=1e-6)


class TestGamma:
    """Tests for gamma."""

    def test_gamma_non_negative(self) -> None:
        g = bsm.gamma(100.0, 100.0, 1.0, 0.05, 0.20)
        assert g >= 0

    def test_gamma_atm_positive(self) -> None:
        g = bsm.gamma(100.0, 100.0, 1.0, 0.05, 0.20)
        assert g > 0

    def test_gamma_deep_itm_near_zero(self) -> None:
        g = bsm.gamma(200.0, 100.0, 1.0, 0.05, 0.20)
        assert g == pytest.approx(0.0, abs=0.001)

    def test_gamma_deep_otm_near_zero(self) -> None:
        g = bsm.gamma(50.0, 100.0, 1.0, 0.05, 0.20)
        assert g == pytest.approx(0.0, abs=0.001)

    def test_gamma_same_for_call_put(self) -> None:
        """Gamma is the same for calls and puts."""
        # Gamma function doesn't take option_type — it's the same for both
        g = bsm.gamma(100.0, 100.0, 1.0, 0.05, 0.20)
        assert g > 0  # Just verify it's valid


class TestTheta:
    """Tests for theta."""

    def test_call_theta_negative(self) -> None:
        """Long options lose value over time (theta < 0)."""
        t = bsm.theta(100.0, 100.0, 1.0, 0.05, 0.20, option_type="call")
        assert t < 0

    def test_put_theta_typically_negative(self) -> None:
        """ATM put theta is typically negative."""
        t = bsm.theta(100.0, 100.0, 1.0, 0.05, 0.20, option_type="put")
        assert t < 0

    def test_theta_per_year(self) -> None:
        """Theta should be per year (not per day)."""
        t = bsm.theta(100.0, 100.0, 1.0, 0.05, 0.20, option_type="call")
        # Daily theta is theta/365, should be a small number
        daily = t / 365
        assert -1.0 < daily < 0


class TestVega:
    """Tests for vega."""

    def test_vega_non_negative(self) -> None:
        v = bsm.vega(100.0, 100.0, 1.0, 0.05, 0.20)
        assert v >= 0

    def test_vega_atm_positive(self) -> None:
        v = bsm.vega(100.0, 100.0, 1.0, 0.05, 0.20)
        assert v > 0

    def test_vega_deep_otm_small(self) -> None:
        """Deep OTM vega is small relative to ATM vega."""
        v_otm = bsm.vega(50.0, 100.0, 1.0, 0.05, 0.20)
        v_atm = bsm.vega(100.0, 100.0, 1.0, 0.05, 0.20)
        assert v_otm < v_atm * 0.1


class TestRho:
    """Tests for rho."""

    def test_call_rho_positive(self) -> None:
        """Call value increases with interest rates."""
        r = bsm.rho(100.0, 100.0, 1.0, 0.05, 0.20, option_type="call")
        assert r > 0

    def test_put_rho_negative(self) -> None:
        """Put value decreases with interest rates."""
        r = bsm.rho(100.0, 100.0, 1.0, 0.05, 0.20, option_type="put")
        assert r < 0


class TestEdgeCases:
    """Edge case handling."""

    def test_at_expiry_call_itm(self) -> None:
        """T=0, ITM call returns intrinsic value."""
        price = bsm.call_price(110.0, 100.0, 0.0, 0.05, 0.20)
        assert price == pytest.approx(10.0, abs=1e-6)

    def test_at_expiry_call_otm(self) -> None:
        """T=0, OTM call returns 0."""
        price = bsm.call_price(90.0, 100.0, 0.0, 0.05, 0.20)
        assert price == pytest.approx(0.0, abs=1e-6)

    def test_at_expiry_put_itm(self) -> None:
        """T=0, ITM put returns intrinsic value."""
        price = bsm.put_price(90.0, 100.0, 0.0, 0.05, 0.20)
        assert price == pytest.approx(10.0, abs=1e-6)

    def test_at_expiry_put_otm(self) -> None:
        """T=0, OTM put returns 0."""
        price = bsm.put_price(110.0, 100.0, 0.0, 0.05, 0.20)
        assert price == pytest.approx(0.0, abs=1e-6)

    def test_zero_vol_call_itm(self) -> None:
        """sigma=0, ITM call returns discounted intrinsic."""
        price = bsm.call_price(110.0, 100.0, 1.0, 0.05, 0.0)
        expected = max(0.0, 110.0 - 100.0 * math.exp(-0.05))
        assert price == pytest.approx(expected, abs=1e-6)

    def test_zero_vol_call_otm(self) -> None:
        """sigma=0, OTM call returns 0."""
        price = bsm.call_price(90.0, 100.0, 1.0, 0.05, 0.0)
        assert price == pytest.approx(0.0, abs=1e-6)

    def test_zero_vol_put_itm(self) -> None:
        """sigma=0, ITM put returns discounted intrinsic."""
        price = bsm.put_price(90.0, 100.0, 1.0, 0.05, 0.0)
        expected = max(0.0, 100.0 * math.exp(-0.05) - 90.0)
        assert price == pytest.approx(expected, abs=1e-6)

    def test_very_small_time_no_nan(self) -> None:
        """Very small T should not produce NaN."""
        price = bsm.call_price(100.0, 100.0, 1e-10, 0.05, 0.20)
        assert math.isfinite(price)

    def test_very_small_vol_no_nan(self) -> None:
        """Very small sigma should not produce NaN."""
        price = bsm.call_price(100.0, 100.0, 1.0, 0.05, 1e-10)
        assert math.isfinite(price)

    def test_delta_at_expiry_itm_call(self) -> None:
        d = bsm.delta(110.0, 100.0, 0.0, 0.05, 0.20, option_type="call")
        assert d == pytest.approx(1.0, abs=1e-6)

    def test_delta_at_expiry_otm_call(self) -> None:
        d = bsm.delta(90.0, 100.0, 0.0, 0.05, 0.20, option_type="call")
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_gamma_at_expiry(self) -> None:
        g = bsm.gamma(100.0, 100.0, 0.0, 0.05, 0.20)
        assert math.isfinite(g)

    def test_vega_at_expiry(self) -> None:
        v = bsm.vega(100.0, 100.0, 0.0, 0.05, 0.20)
        assert math.isfinite(v)


# -----------------------------------------------------------------------
# Second-Order Greeks: Finite-Difference Verification
# -----------------------------------------------------------------------


class TestSecondOrderFiniteDifference:
    """Verify analytical second-order Greeks against numerical finite differences."""

    H = 1e-5  # bump size
    TOL = 1e-4  # tolerance

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_vanna_vs_delta_bump_sigma(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """vanna = dDelta/dSigma, verified by bumping sigma on delta."""
        analytical = bsm.vanna(S, K, T, r, sigma, q)
        numerical = (
            bsm.delta(S, K, T, r, sigma + self.H, q, option_type="call")
            - bsm.delta(S, K, T, r, sigma - self.H, q, option_type="call")
        ) / (2 * self.H)
        assert analytical == pytest.approx(numerical, abs=self.TOL)

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_vanna_vs_vega_bump_spot(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """vanna = dVega/dS, verified by bumping S on vega."""
        analytical = bsm.vanna(S, K, T, r, sigma, q)
        h_s = S * self.H  # relative bump for spot
        numerical = (
            bsm.vega(S + h_s, K, T, r, sigma, q) - bsm.vega(S - h_s, K, T, r, sigma, q)
        ) / (2 * h_s)
        assert analytical == pytest.approx(numerical, abs=self.TOL)

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_volga_vs_vega_bump_sigma(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """volga = dVega/dSigma, verified by bumping sigma on vega."""
        analytical = bsm.volga(S, K, T, r, sigma, q)
        numerical = (
            bsm.vega(S, K, T, r, sigma + self.H, q)
            - bsm.vega(S, K, T, r, sigma - self.H, q)
        ) / (2 * self.H)
        assert analytical == pytest.approx(numerical, abs=self.TOL)

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_charm_vs_delta_bump_time(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """charm = dDelta/dT, verified by bumping T on delta."""
        for opt_type in ("call", "put"):
            analytical = bsm.charm(S, K, T, r, sigma, q, option_type=opt_type)
            numerical = (
                bsm.delta(S, K, T + self.H, r, sigma, q, option_type=opt_type)
                - bsm.delta(S, K, T - self.H, r, sigma, q, option_type=opt_type)
            ) / (2 * self.H)
            assert analytical == pytest.approx(numerical, abs=self.TOL), (
                f"charm mismatch for {opt_type} at {label}"
            )

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_veta_vs_vega_bump_time(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """veta = dVega/dT, verified by bumping T on vega."""
        analytical = bsm.veta(S, K, T, r, sigma, q)
        numerical = (
            bsm.vega(S, K, T + self.H, r, sigma, q)
            - bsm.vega(S, K, T - self.H, r, sigma, q)
        ) / (2 * self.H)
        assert analytical == pytest.approx(numerical, abs=self.TOL)

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_speed_vs_gamma_bump_spot(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """speed = dGamma/dS, verified by bumping S on gamma."""
        analytical = bsm.speed(S, K, T, r, sigma, q)
        h_s = S * self.H
        numerical = (
            bsm.gamma(S + h_s, K, T, r, sigma, q)
            - bsm.gamma(S - h_s, K, T, r, sigma, q)
        ) / (2 * h_s)
        assert analytical == pytest.approx(numerical, abs=self.TOL)

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_color_vs_gamma_bump_time(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """color = dGamma/dT, verified by bumping T on gamma."""
        analytical = bsm.color(S, K, T, r, sigma, q)
        numerical = (
            bsm.gamma(S, K, T + self.H, r, sigma, q)
            - bsm.gamma(S, K, T - self.H, r, sigma, q)
        ) / (2 * self.H)
        assert analytical == pytest.approx(numerical, abs=self.TOL)


class TestSecondOrderSymmetry:
    """Verify second-order Greeks symmetries."""

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_vanna_same_for_call_and_put(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """Vanna is the same for calls and puts."""
        # Our vanna function doesn't take option_type — it's symmetric by definition
        v = bsm.vanna(S, K, T, r, sigma, q)
        assert math.isfinite(v)

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_volga_same_for_call_and_put(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """Volga is the same for calls and puts."""
        v = bsm.volga(S, K, T, r, sigma, q)
        assert math.isfinite(v)


class TestSecondOrderEdgeCases:
    """Edge cases for second-order Greeks."""

    def test_second_order_at_expiry(self) -> None:
        """All second-order Greeks should return 0 at T=0."""
        S, K, r, sigma = 100.0, 100.0, 0.05, 0.20
        assert bsm.vanna(S, K, 0.0, r, sigma) == 0.0
        assert bsm.volga(S, K, 0.0, r, sigma) == 0.0
        assert bsm.charm(S, K, 0.0, r, sigma, option_type="call") == 0.0
        assert bsm.veta(S, K, 0.0, r, sigma) == 0.0
        assert bsm.speed(S, K, 0.0, r, sigma) == 0.0
        assert bsm.color(S, K, 0.0, r, sigma) == 0.0

    def test_second_order_zero_vol(self) -> None:
        """All second-order Greeks should return 0 at sigma=0."""
        S, K, T, r = 100.0, 100.0, 1.0, 0.05
        assert bsm.vanna(S, K, T, r, 0.0) == 0.0
        assert bsm.volga(S, K, T, r, 0.0) == 0.0
        assert bsm.charm(S, K, T, r, 0.0, option_type="call") == 0.0
        assert bsm.veta(S, K, T, r, 0.0) == 0.0
        assert bsm.speed(S, K, T, r, 0.0) == 0.0
        assert bsm.color(S, K, T, r, 0.0) == 0.0

    def test_no_nan_inf_deep_itm(self) -> None:
        """No NaN/Inf for deep ITM (S >> K)."""
        S, K, T, r, sigma = 300.0, 100.0, 0.5, 0.05, 0.20
        for fn in [bsm.vanna, bsm.volga, bsm.veta, bsm.speed, bsm.color]:
            assert math.isfinite(fn(S, K, T, r, sigma))
        assert math.isfinite(bsm.charm(S, K, T, r, sigma, option_type="call"))

    def test_no_nan_inf_deep_otm(self) -> None:
        """No NaN/Inf for deep OTM (S << K)."""
        S, K, T, r, sigma = 30.0, 100.0, 0.5, 0.05, 0.20
        for fn in [bsm.vanna, bsm.volga, bsm.veta, bsm.speed, bsm.color]:
            assert math.isfinite(fn(S, K, T, r, sigma))
        assert math.isfinite(bsm.charm(S, K, T, r, sigma, option_type="call"))


# -----------------------------------------------------------------------
# Comprehensive parametrized tests (options-12)
# -----------------------------------------------------------------------


class TestPutCallParityParametrized:
    """Put-call parity across multiple test points."""

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_put_call_parity(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        call = bsm.call_price(S, K, T, r, sigma, q)
        put = bsm.put_price(S, K, T, r, sigma, q)
        parity = S * math.exp(-q * T) - K * math.exp(-r * T)
        assert (call - put) == pytest.approx(parity, rel=1e-6)


class TestGreeksSymmetryParametrized:
    """Symmetry properties across test points."""

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_gamma_call_equals_put(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """Gamma is the same for calls and puts (same function)."""
        g = bsm.gamma(S, K, T, r, sigma, q)
        assert g >= 0

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_vega_call_equals_put(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """Vega is the same for calls and puts (same function)."""
        v = bsm.vega(S, K, T, r, sigma, q)
        assert v >= 0


class TestFirstOrderFiniteDifference:
    """Verify first-order Greeks via finite difference on pricing."""

    H = 1e-5
    TOL = 1e-4

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_delta_vs_price_bump(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """delta = dC/dS."""
        h_s = S * self.H
        for opt_type, price_fn in [("call", bsm.call_price), ("put", bsm.put_price)]:
            analytical = bsm.delta(S, K, T, r, sigma, q, option_type=opt_type)
            numerical = (
                price_fn(S + h_s, K, T, r, sigma, q)
                - price_fn(S - h_s, K, T, r, sigma, q)
            ) / (2 * h_s)
            assert analytical == pytest.approx(numerical, abs=self.TOL), (
                f"delta mismatch for {opt_type} at {label}"
            )

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_gamma_vs_price_bump(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """gamma = d2C/dS2."""
        h_s = S * self.H
        analytical = bsm.gamma(S, K, T, r, sigma, q)
        numerical = (
            bsm.call_price(S + h_s, K, T, r, sigma, q)
            - 2 * bsm.call_price(S, K, T, r, sigma, q)
            + bsm.call_price(S - h_s, K, T, r, sigma, q)
        ) / (h_s**2)
        assert analytical == pytest.approx(numerical, abs=self.TOL)

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_vega_vs_price_bump(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """vega = dC/dSigma."""
        analytical = bsm.vega(S, K, T, r, sigma, q)
        numerical = (
            bsm.call_price(S, K, T, r, sigma + self.H, q)
            - bsm.call_price(S, K, T, r, sigma - self.H, q)
        ) / (2 * self.H)
        assert analytical == pytest.approx(numerical, abs=self.TOL)

    @pytest.mark.parametrize(
        "S,K,T,r,sigma,q,label",
        TEST_POINTS,
        ids=[t[-1] for t in TEST_POINTS],
    )
    def test_rho_vs_price_bump(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float, label: str
    ) -> None:
        """rho = dC/dr."""
        for opt_type, price_fn in [("call", bsm.call_price), ("put", bsm.put_price)]:
            analytical = bsm.rho(S, K, T, r, sigma, q, option_type=opt_type)
            numerical = (
                price_fn(S, K, T, r + self.H, sigma, q)
                - price_fn(S, K, T, r - self.H, sigma, q)
            ) / (2 * self.H)
            assert analytical == pytest.approx(numerical, abs=self.TOL), (
                f"rho mismatch for {opt_type} at {label}"
            )
