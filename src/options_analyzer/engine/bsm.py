"""Black-Scholes-Merton analytical formulas — pure functions.

All functions take scalar inputs and return scalar outputs.
Parameters:
    S: spot price
    K: strike price
    T: time to expiry in years
    r: risk-free rate (annualized)
    sigma: implied volatility (annualized)
    q: continuous dividend yield (default 0.0)
"""

import math

from scipy.stats import norm

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def d1(S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0) -> float:
    """Compute d1 in the BSM formula."""
    return (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))


def d2(S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0) -> float:
    """Compute d2 in the BSM formula."""
    return d1(S, K, T, r, sigma, q) - sigma * math.sqrt(T)


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------


def call_price(
    S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0
) -> float:
    """European call price via BSM."""
    if T <= 0:
        return max(0.0, S - K)
    if sigma <= 0:
        return max(0.0, S * math.exp(-q * T) - K * math.exp(-r * T))
    _d1 = d1(S, K, T, r, sigma, q)
    _d2 = _d1 - sigma * math.sqrt(T)
    return S * math.exp(-q * T) * norm.cdf(_d1) - K * math.exp(-r * T) * norm.cdf(_d2)


def put_price(
    S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0
) -> float:
    """European put price via BSM."""
    if T <= 0:
        return max(0.0, K - S)
    if sigma <= 0:
        return max(0.0, K * math.exp(-r * T) - S * math.exp(-q * T))
    _d1 = d1(S, K, T, r, sigma, q)
    _d2 = _d1 - sigma * math.sqrt(T)
    return K * math.exp(-r * T) * norm.cdf(-_d2) - S * math.exp(-q * T) * norm.cdf(-_d1)


# ---------------------------------------------------------------------------
# First-Order Greeks
# ---------------------------------------------------------------------------


def delta(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    q: float = 0.0,
    *,
    option_type: str = "call",
) -> float:
    """Delta: dPrice/dS."""
    if T <= 0:
        if option_type == "call":
            return 1.0 if S > K else 0.0
        else:
            return -1.0 if S < K else 0.0
    if sigma <= 0:
        if option_type == "call":
            return math.exp(-q * T) if S > K else 0.0
        else:
            return -math.exp(-q * T) if S < K else 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    if option_type == "call":
        return math.exp(-q * T) * norm.cdf(_d1)
    else:
        return -math.exp(-q * T) * norm.cdf(-_d1)


def gamma(
    S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0
) -> float:
    """Gamma: d2Price/dS2. Same for calls and puts."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    return math.exp(-q * T) * norm.pdf(_d1) / (S * sigma * math.sqrt(T))


def theta(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    q: float = 0.0,
    *,
    option_type: str = "call",
) -> float:
    """Theta: dPrice/dT (per year). Negative for long options."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    _d2 = _d1 - sigma * math.sqrt(T)
    common = -(S * math.exp(-q * T) * norm.pdf(_d1) * sigma) / (2 * math.sqrt(T))
    if option_type == "call":
        return (
            common
            + q * S * math.exp(-q * T) * norm.cdf(_d1)
            - r * K * math.exp(-r * T) * norm.cdf(_d2)
        )
    else:
        return (
            common
            - q * S * math.exp(-q * T) * norm.cdf(-_d1)
            + r * K * math.exp(-r * T) * norm.cdf(-_d2)
        )


def vega(S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0) -> float:
    """Vega: dPrice/dSigma. Same for calls and puts."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    return S * math.exp(-q * T) * norm.pdf(_d1) * math.sqrt(T)


def rho(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    q: float = 0.0,
    *,
    option_type: str = "call",
) -> float:
    """Rho: dPrice/dR."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d2 = d2(S, K, T, r, sigma, q)
    if option_type == "call":
        return K * T * math.exp(-r * T) * norm.cdf(_d2)
    else:
        return -K * T * math.exp(-r * T) * norm.cdf(-_d2)


# ---------------------------------------------------------------------------
# Second-Order Greeks
# ---------------------------------------------------------------------------


def vanna(
    S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0
) -> float:
    """Vanna: dDelta/dVol = dVega/dS."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    _d2 = _d1 - sigma * math.sqrt(T)
    return -math.exp(-q * T) * norm.pdf(_d1) * _d2 / sigma


def volga(
    S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0
) -> float:
    """Volga (vomma): dVega/dVol."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    _d2 = _d1 - sigma * math.sqrt(T)
    _vega = vega(S, K, T, r, sigma, q)
    return _vega * _d1 * _d2 / sigma


def charm(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    q: float = 0.0,
    *,
    option_type: str = "call",
) -> float:
    """Charm: dDelta/dTime (delta decay)."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    _d2 = _d1 - sigma * math.sqrt(T)
    sqrt_T = math.sqrt(T)
    common_term = (
        math.exp(-q * T)
        * norm.pdf(_d1)
        * (2 * (r - q) * T - _d2 * sigma * sqrt_T)
        / (2 * T * sigma * sqrt_T)
    )
    if option_type == "call":
        return -q * math.exp(-q * T) * norm.cdf(_d1) + common_term
    else:
        return q * math.exp(-q * T) * norm.cdf(-_d1) + common_term


def veta(S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0) -> float:
    """Veta: dVega/dTime."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    _d2 = _d1 - sigma * math.sqrt(T)
    sqrt_T = math.sqrt(T)
    return (
        -S
        * math.exp(-q * T)
        * norm.pdf(_d1)
        * sqrt_T
        * (q + (r - q) * _d1 / (sigma * sqrt_T) - (1 + _d1 * _d2) / (2 * T))
    )


def speed(
    S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0
) -> float:
    """Speed: dGamma/dS."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    _gamma = gamma(S, K, T, r, sigma, q)
    sqrt_T = math.sqrt(T)
    return -(_gamma / S) * (1 + _d1 / (sigma * sqrt_T))


def color(
    S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0
) -> float:
    """Color: dGamma/dTime."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma, q)
    _d2 = _d1 - sigma * math.sqrt(T)
    sqrt_T = math.sqrt(T)
    return (
        -math.exp(-q * T)
        * norm.pdf(_d1)
        / (2 * S * T * sigma * sqrt_T)
        * (
            2 * q * T
            + 1
            + _d1 * (2 * (r - q) * T - _d2 * sigma * sqrt_T) / (sigma * sqrt_T)
        )
    )
