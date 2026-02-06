"""Tests for GreeksCalculator class."""

import pytest

from options_analyzer.domain.enums import OptionType
from options_analyzer.domain.greeks import (
    FirstOrderGreeks,
    FullGreeks,
    SecondOrderGreeks,
)
from options_analyzer.engine import bsm
from options_analyzer.engine.greeks_calculator import GreeksCalculator


class TestConstructor:
    def test_stores_defaults(self) -> None:
        calc = GreeksCalculator(risk_free_rate=0.05, dividend_yield=0.02)
        assert calc.risk_free_rate == 0.05
        assert calc.dividend_yield == 0.02

    def test_default_values(self) -> None:
        calc = GreeksCalculator()
        assert calc.risk_free_rate == 0.05
        assert calc.dividend_yield == 0.0


class TestFirstOrder:
    def test_returns_first_order_greeks(self) -> None:
        calc = GreeksCalculator()
        result = calc.first_order(100.0, 100.0, 1.0, 0.20, OptionType.CALL)
        assert isinstance(result, FirstOrderGreeks)

    def test_correct_values(self) -> None:
        calc = GreeksCalculator(risk_free_rate=0.05, dividend_yield=0.0)
        S, K, T, sigma = 100.0, 100.0, 1.0, 0.20
        result = calc.first_order(S, K, T, sigma, OptionType.CALL)
        assert result.delta == pytest.approx(
            bsm.delta(S, K, T, 0.05, sigma, option_type="call"), rel=1e-6
        )
        assert result.gamma == pytest.approx(bsm.gamma(S, K, T, 0.05, sigma), rel=1e-6)
        assert result.theta == pytest.approx(
            bsm.theta(S, K, T, 0.05, sigma, option_type="call"), rel=1e-6
        )
        assert result.vega == pytest.approx(bsm.vega(S, K, T, 0.05, sigma), rel=1e-6)
        assert result.rho == pytest.approx(
            bsm.rho(S, K, T, 0.05, sigma, option_type="call"), rel=1e-6
        )
        assert result.iv == sigma

    def test_put_type(self) -> None:
        calc = GreeksCalculator(risk_free_rate=0.05)
        result = calc.first_order(100.0, 100.0, 1.0, 0.20, OptionType.PUT)
        assert result.delta < 0  # put delta is negative

    def test_override_r_q(self) -> None:
        calc = GreeksCalculator(risk_free_rate=0.05, dividend_yield=0.0)
        result = calc.first_order(
            100.0, 100.0, 1.0, 0.20, OptionType.CALL, r=0.10, q=0.03
        )
        expected_delta = bsm.delta(
            100.0, 100.0, 1.0, 0.10, 0.20, 0.03, option_type="call"
        )
        assert result.delta == pytest.approx(expected_delta, rel=1e-6)


class TestSecondOrder:
    def test_returns_second_order_greeks(self) -> None:
        calc = GreeksCalculator()
        result = calc.second_order(100.0, 100.0, 1.0, 0.20, OptionType.CALL)
        assert isinstance(result, SecondOrderGreeks)

    def test_correct_values(self) -> None:
        calc = GreeksCalculator(risk_free_rate=0.05)
        S, K, T, sigma = 100.0, 100.0, 1.0, 0.20
        result = calc.second_order(S, K, T, sigma, OptionType.CALL)
        assert result.vanna == pytest.approx(bsm.vanna(S, K, T, 0.05, sigma), rel=1e-6)
        assert result.volga == pytest.approx(bsm.volga(S, K, T, 0.05, sigma), rel=1e-6)
        assert result.charm == pytest.approx(
            bsm.charm(S, K, T, 0.05, sigma, option_type="call"), rel=1e-6
        )
        assert result.veta == pytest.approx(bsm.veta(S, K, T, 0.05, sigma), rel=1e-6)
        assert result.speed == pytest.approx(bsm.speed(S, K, T, 0.05, sigma), rel=1e-6)
        assert result.color == pytest.approx(bsm.color(S, K, T, 0.05, sigma), rel=1e-6)


class TestFull:
    def test_returns_full_greeks(self) -> None:
        calc = GreeksCalculator()
        result = calc.full(100.0, 100.0, 1.0, 0.20, OptionType.CALL)
        assert isinstance(result, FullGreeks)
        assert isinstance(result.first_order, FirstOrderGreeks)
        assert isinstance(result.second_order, SecondOrderGreeks)

    def test_combines_first_and_second(self) -> None:
        calc = GreeksCalculator(risk_free_rate=0.05)
        S, K, T, sigma = 100.0, 100.0, 1.0, 0.20
        full = calc.full(S, K, T, sigma, OptionType.CALL)
        first = calc.first_order(S, K, T, sigma, OptionType.CALL)
        second = calc.second_order(S, K, T, sigma, OptionType.CALL)
        assert full.first_order.delta == pytest.approx(first.delta, rel=1e-10)
        assert full.second_order.vanna == pytest.approx(second.vanna, rel=1e-10)


class TestEdgeCases:
    def test_at_expiry(self) -> None:
        calc = GreeksCalculator()
        result = calc.full(110.0, 100.0, 0.0, 0.20, OptionType.CALL)
        assert isinstance(result, FullGreeks)
        assert result.first_order.delta == pytest.approx(1.0, abs=1e-6)

    def test_zero_vol(self) -> None:
        calc = GreeksCalculator()
        result = calc.full(110.0, 100.0, 1.0, 0.0, OptionType.CALL)
        assert isinstance(result, FullGreeks)
