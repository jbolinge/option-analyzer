"""GreeksCalculator — thin wrapper around BSM pure functions returning domain models."""

from options_analyzer.domain.enums import OptionType
from options_analyzer.domain.greeks import (
    FirstOrderGreeks,
    FullGreeks,
    SecondOrderGreeks,
)
from options_analyzer.engine import bsm


class GreeksCalculator:
    """Wraps BSM pure functions with config defaults.

    Returns domain Greeks models.
    """

    def __init__(
        self, risk_free_rate: float = 0.05, dividend_yield: float = 0.0
    ) -> None:
        self.risk_free_rate = risk_free_rate
        self.dividend_yield = dividend_yield

    def first_order(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
        option_type: OptionType,
        r: float | None = None,
        q: float | None = None,
    ) -> FirstOrderGreeks:
        """Compute first-order Greeks. Uses config defaults for r/q if not provided."""
        r_ = r if r is not None else self.risk_free_rate
        q_ = q if q is not None else self.dividend_yield
        opt = option_type.value
        return FirstOrderGreeks(
            delta=bsm.delta(S, K, T, r_, sigma, q_, option_type=opt),
            gamma=bsm.gamma(S, K, T, r_, sigma, q_),
            theta=bsm.theta(S, K, T, r_, sigma, q_, option_type=opt),
            vega=bsm.vega(S, K, T, r_, sigma, q_),
            rho=bsm.rho(S, K, T, r_, sigma, q_, option_type=opt),
            iv=sigma,
        )

    def second_order(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
        option_type: OptionType,
        r: float | None = None,
        q: float | None = None,
    ) -> SecondOrderGreeks:
        """Compute second-order Greeks."""
        r_ = r if r is not None else self.risk_free_rate
        q_ = q if q is not None else self.dividend_yield
        opt = option_type.value
        return SecondOrderGreeks(
            vanna=bsm.vanna(S, K, T, r_, sigma, q_),
            volga=bsm.volga(S, K, T, r_, sigma, q_),
            charm=bsm.charm(S, K, T, r_, sigma, q_, option_type=opt),
            veta=bsm.veta(S, K, T, r_, sigma, q_),
            speed=bsm.speed(S, K, T, r_, sigma, q_),
            color=bsm.color(S, K, T, r_, sigma, q_),
        )

    def full(
        self,
        S: float,
        K: float,
        T: float,
        sigma: float,
        option_type: OptionType,
        r: float | None = None,
        q: float | None = None,
    ) -> FullGreeks:
        """Compute all Greeks (first + second order)."""
        return FullGreeks(
            first_order=self.first_order(S, K, T, sigma, option_type, r, q),
            second_order=self.second_order(S, K, T, sigma, option_type, r, q),
        )
