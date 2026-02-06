"""Hypothesis property-based tests for BSM invariants."""

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from options_analyzer.engine import bsm

# Strategies for valid BSM inputs
spot = st.floats(min_value=10.0, max_value=500.0, allow_nan=False, allow_infinity=False)
strike = st.floats(
    min_value=10.0, max_value=500.0, allow_nan=False, allow_infinity=False
)
time_to_expiry = st.floats(
    min_value=0.01, max_value=5.0, allow_nan=False, allow_infinity=False
)
risk_free = st.floats(
    min_value=0.0, max_value=0.20, allow_nan=False, allow_infinity=False
)
vol = st.floats(min_value=0.05, max_value=2.0, allow_nan=False, allow_infinity=False)
div_yield = st.floats(
    min_value=0.0, max_value=0.10, allow_nan=False, allow_infinity=False
)


class TestPutCallParity:
    """Put-call parity must hold for all valid inputs."""

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_put_call_parity(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        call = bsm.call_price(S, K, T, r, sigma, q)
        put = bsm.put_price(S, K, T, r, sigma, q)
        parity = S * math.exp(-q * T) - K * math.exp(-r * T)
        assert (call - put) == pytest.approx(parity, rel=1e-6, abs=1e-10)


class TestDeltaBounds:
    """Delta must stay within theoretical bounds."""

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_call_delta_between_0_and_1(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        d = bsm.delta(S, K, T, r, sigma, q, option_type="call")
        assert -1e-10 <= d <= 1.0 + 1e-10

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_put_delta_between_neg1_and_0(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        d = bsm.delta(S, K, T, r, sigma, q, option_type="put")
        assert -1.0 - 1e-10 <= d <= 1e-10

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_delta_parity(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        """call_delta - put_delta = e^(-qT)."""
        call_d = bsm.delta(S, K, T, r, sigma, q, option_type="call")
        put_d = bsm.delta(S, K, T, r, sigma, q, option_type="put")
        assert (call_d - put_d) == pytest.approx(math.exp(-q * T), rel=1e-6)


class TestNonNegativeGreeks:
    """Greeks that must be non-negative."""

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_gamma_non_negative(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        g = bsm.gamma(S, K, T, r, sigma, q)
        assert g >= -1e-10

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_vega_non_negative(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        v = bsm.vega(S, K, T, r, sigma, q)
        assert v >= -1e-10

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_call_price_non_negative(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        assert bsm.call_price(S, K, T, r, sigma, q) >= -1e-10

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_put_price_non_negative(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        assert bsm.put_price(S, K, T, r, sigma, q) >= -1e-10


class TestMonotonicity:
    """Price monotonicity properties."""

    @given(
        S1=st.floats(
            min_value=10.0, max_value=250.0, allow_nan=False, allow_infinity=False
        ),
        S_bump=st.floats(
            min_value=0.01, max_value=50.0, allow_nan=False, allow_infinity=False
        ),
        K=strike,
        T=time_to_expiry,
        r=risk_free,
        sigma=vol,
        q=div_yield,
    )
    @settings(max_examples=500)
    def test_call_increases_with_spot(
        self,
        S1: float,
        S_bump: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float,
    ) -> None:
        S2 = S1 + S_bump
        c1 = bsm.call_price(S1, K, T, r, sigma, q)
        c2 = bsm.call_price(S2, K, T, r, sigma, q)
        assert c2 >= c1 - 1e-10

    @given(
        S1=st.floats(
            min_value=10.0, max_value=250.0, allow_nan=False, allow_infinity=False
        ),
        S_bump=st.floats(
            min_value=0.01, max_value=50.0, allow_nan=False, allow_infinity=False
        ),
        K=strike,
        T=time_to_expiry,
        r=risk_free,
        sigma=vol,
        q=div_yield,
    )
    @settings(max_examples=500)
    def test_put_decreases_with_spot(
        self,
        S1: float,
        S_bump: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float,
    ) -> None:
        S2 = S1 + S_bump
        p1 = bsm.put_price(S1, K, T, r, sigma, q)
        p2 = bsm.put_price(S2, K, T, r, sigma, q)
        assert p1 >= p2 - 1e-10

    @given(
        S=spot,
        K=strike,
        T=time_to_expiry,
        r=risk_free,
        sigma1=st.floats(
            min_value=0.05, max_value=1.0, allow_nan=False, allow_infinity=False
        ),
        sigma_bump=st.floats(
            min_value=0.01, max_value=0.5, allow_nan=False, allow_infinity=False
        ),
        q=div_yield,
    )
    @settings(max_examples=500)
    def test_prices_increase_with_vol(
        self,
        S: float,
        K: float,
        T: float,
        r: float,
        sigma1: float,
        sigma_bump: float,
        q: float,
    ) -> None:
        sigma2 = sigma1 + sigma_bump
        c1 = bsm.call_price(S, K, T, r, sigma1, q)
        c2 = bsm.call_price(S, K, T, r, sigma2, q)
        assert c2 >= c1 - 1e-10
        p1 = bsm.put_price(S, K, T, r, sigma1, q)
        p2 = bsm.put_price(S, K, T, r, sigma2, q)
        assert p2 >= p1 - 1e-10


class TestGreeksSymmetry:
    """Greeks that are the same for calls and puts."""

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_vanna_is_finite(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        """Vanna (same for call/put) should always be finite."""
        v = bsm.vanna(S, K, T, r, sigma, q)
        assert math.isfinite(v)

    @given(S=spot, K=strike, T=time_to_expiry, r=risk_free, sigma=vol, q=div_yield)
    @settings(max_examples=500)
    def test_all_greeks_finite(
        self, S: float, K: float, T: float, r: float, sigma: float, q: float
    ) -> None:
        """All Greeks should produce finite values for valid inputs."""
        assert math.isfinite(bsm.delta(S, K, T, r, sigma, q, option_type="call"))
        assert math.isfinite(bsm.gamma(S, K, T, r, sigma, q))
        assert math.isfinite(bsm.theta(S, K, T, r, sigma, q, option_type="call"))
        assert math.isfinite(bsm.vega(S, K, T, r, sigma, q))
        assert math.isfinite(bsm.rho(S, K, T, r, sigma, q, option_type="call"))
        assert math.isfinite(bsm.vanna(S, K, T, r, sigma, q))
        assert math.isfinite(bsm.volga(S, K, T, r, sigma, q))
        assert math.isfinite(bsm.charm(S, K, T, r, sigma, q, option_type="call"))
        assert math.isfinite(bsm.veta(S, K, T, r, sigma, q))
        assert math.isfinite(bsm.speed(S, K, T, r, sigma, q))
        assert math.isfinite(bsm.color(S, K, T, r, sigma, q))
