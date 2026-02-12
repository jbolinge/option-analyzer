"""Tests for PositionAnalyzer."""

from datetime import date, timedelta
from decimal import Decimal

import numpy as np
import pytest

from options_analyzer.domain.enums import OptionType, PositionSide
from options_analyzer.domain.greeks import PositionGreeks
from options_analyzer.domain.models import Position
from options_analyzer.engine.greeks_calculator import GreeksCalculator
from options_analyzer.engine.position_analyzer import PositionAnalyzer
from tests.factories import make_contract, make_leg, make_position, make_vertical_spread


@pytest.fixture
def analyzer() -> PositionAnalyzer:
    return PositionAnalyzer(GreeksCalculator(risk_free_rate=0.05, dividend_yield=0.0))


def _make_single_call_position() -> tuple[Position, dict[str, float]]:
    contract = make_contract(
        strike=Decimal("100"),
        option_type=OptionType.CALL,
        expiration=date.today() + timedelta(days=30),
    )
    leg = make_leg(
        contract=contract, side=PositionSide.LONG, quantity=1, open_price=Decimal("5")
    )
    position = make_position(legs=[leg])
    ivs = {contract.symbol: 0.20}
    return position, ivs


def _make_straddle() -> tuple[Position, dict[str, float]]:
    expiration = date.today() + timedelta(days=30)
    call_contract = make_contract(
        symbol="AAPL_C100",
        strike=Decimal("100"),
        option_type=OptionType.CALL,
        expiration=expiration,
    )
    put_contract = make_contract(
        symbol="AAPL_P100",
        strike=Decimal("100"),
        option_type=OptionType.PUT,
        expiration=expiration,
    )
    legs = [
        make_leg(
            contract=call_contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        ),
        make_leg(
            contract=put_contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        ),
    ]
    position = make_position(legs=legs)
    ivs = {call_contract.symbol: 0.20, put_contract.symbol: 0.20}
    return position, ivs


class TestPositionGreeks:
    def test_single_long_call(self, analyzer: PositionAnalyzer) -> None:
        """Single long call: position Greeks = leg Greeks * quantity * multiplier."""
        position, ivs = _make_single_call_position()
        result = analyzer.position_greeks(position, 100.0, ivs)
        assert isinstance(result, PositionGreeks)
        assert len(result.per_leg) == 1
        # Aggregated should scale by signed_quantity * multiplier = 1 * 100
        leg_greeks = list(result.per_leg.values())[0]
        assert result.aggregated.first_order.delta == pytest.approx(
            leg_greeks.first_order.delta, rel=1e-6
        )

    def test_straddle_near_zero_delta_atm(self, analyzer: PositionAnalyzer) -> None:
        """ATM straddle: delta near zero (call delta + put delta ~ 0)."""
        position, ivs = _make_straddle()
        result = analyzer.position_greeks(position, 100.0, ivs)
        # ATM call delta ~0.5, put delta ~-0.5, scaled by 100 each
        # Net delta should be near zero (not exactly due to forward effect)
        assert abs(result.aggregated.first_order.delta) < 20.0  # small relative to 100

    def test_straddle_double_gamma(self, analyzer: PositionAnalyzer) -> None:
        """ATM straddle: gamma is doubled (call gamma + put gamma = 2 * gamma)."""
        position, ivs = _make_straddle()
        result = analyzer.position_greeks(position, 100.0, ivs)
        # Both call and put have same gamma, so aggregated = 2 * single * multiplier
        single_gamma = list(result.per_leg.values())[0].first_order.gamma
        # Aggregated is sum of both legs (each scaled by qty * multiplier = 100)
        assert result.aggregated.first_order.gamma == pytest.approx(
            single_gamma * 2, rel=0.01
        )

    def test_vertical_spread_partial_cancel(self, analyzer: PositionAnalyzer) -> None:
        """Vertical spread: delta partially cancels."""
        position = make_vertical_spread("AAPL", [Decimal("100"), Decimal("110")])
        ivs = {leg.contract.symbol: 0.20 for leg in position.legs}
        result = analyzer.position_greeks(position, 105.0, ivs)
        # Long 100 call has higher delta than short 110 call
        # Net delta should be positive but less than single leg
        assert result.aggregated.first_order.delta > 0
        # Check per-leg has 2 entries
        assert len(result.per_leg) == 2


class TestGreeksVsPrice:
    def test_correct_shape(self, analyzer: PositionAnalyzer) -> None:
        position, ivs = _make_single_call_position()
        price_range = np.linspace(80.0, 120.0, 21)
        result = analyzer.greeks_vs_price(position, price_range, ivs)
        assert isinstance(result, dict)
        for key in (
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
            "vanna",
            "volga",
            "charm",
            "veta",
            "speed",
            "color",
        ):
            assert key in result
            assert result[key].shape == (21,)

    def test_delta_increases_with_price_for_call(
        self, analyzer: PositionAnalyzer
    ) -> None:
        position, ivs = _make_single_call_position()
        price_range = np.linspace(80.0, 120.0, 21)
        result = analyzer.greeks_vs_price(position, price_range, ivs)
        # Delta for a long call should generally increase with S
        assert result["delta"][-1] > result["delta"][0]


class TestGreeksVsTime:
    def test_correct_shape(self, analyzer: PositionAnalyzer) -> None:
        position, ivs = _make_single_call_position()
        dte_range = np.array([60.0, 45.0, 30.0, 15.0, 7.0, 1.0])
        result = analyzer.greeks_vs_time(position, 100.0, ivs, dte_range)
        assert isinstance(result, dict)
        for key in (
            "delta",
            "gamma",
            "theta",
            "vega",
            "rho",
            "vanna",
            "volga",
            "charm",
            "veta",
            "speed",
            "color",
        ):
            assert key in result
            assert result[key].shape == (6,)


class TestDeltaVsPriceAtDtes:
    def test_returns_dict_with_correct_keys(self, analyzer: PositionAnalyzer) -> None:
        """Keys match '{dte} DTE' format."""
        position, ivs = _make_single_call_position()
        price_range = np.linspace(80.0, 120.0, 11)
        result = analyzer.delta_vs_price_at_dtes(position, price_range, ivs, [60, 30, 7])
        assert set(result.keys()) == {"60 DTE", "30 DTE", "7 DTE"}

    def test_correct_array_shape(self, analyzer: PositionAnalyzer) -> None:
        """Each array matches len(price_range)."""
        position, ivs = _make_single_call_position()
        price_range = np.linspace(80.0, 120.0, 21)
        result = analyzer.delta_vs_price_at_dtes(position, price_range, ivs, [60, 30])
        for arr in result.values():
            assert arr.shape == (21,)

    def test_delta_increases_with_price_for_long_call(
        self, analyzer: PositionAnalyzer
    ) -> None:
        """Delta monotonically increases for a simple long call."""
        position, ivs = _make_single_call_position()
        price_range = np.linspace(80.0, 120.0, 21)
        result = analyzer.delta_vs_price_at_dtes(position, price_range, ivs, [30])
        deltas = result["30 DTE"]
        assert all(deltas[i + 1] >= deltas[i] for i in range(len(deltas) - 1))

    def test_delta_steeper_at_lower_dte(self, analyzer: PositionAnalyzer) -> None:
        """Lower DTE produces a sharper step function (charm effect)."""
        position, ivs = _make_single_call_position()
        price_range = np.linspace(80.0, 120.0, 51)
        result = analyzer.delta_vs_price_at_dtes(position, price_range, ivs, [60, 7])
        # Max delta difference across range is greater at lower DTE (sharper)
        span_60 = result["60 DTE"][-1] - result["60 DTE"][0]
        span_7 = result["7 DTE"][-1] - result["7 DTE"][0]
        assert span_7 >= span_60

    def test_multileg_scaling(self, analyzer: PositionAnalyzer) -> None:
        """Vertical spread delta partially cancels and is bounded."""
        position = make_vertical_spread("AAPL", [Decimal("100"), Decimal("110")])
        ivs = {leg.contract.symbol: 0.20 for leg in position.legs}
        price_range = np.linspace(80.0, 130.0, 21)
        result = analyzer.delta_vs_price_at_dtes(position, price_range, ivs, [30])
        deltas = result["30 DTE"]
        # Net delta should be positive (long lower strike) but bounded
        assert all(d >= -10 for d in deltas)  # not hugely negative
        # Max net delta less than a single naked call (100 * 1 = 100)
        assert max(deltas) < 100

    def test_zero_dte_approaches_intrinsic_delta(
        self, analyzer: PositionAnalyzer
    ) -> None:
        """At ~0 DTE, delta approaches step function (0 OTM, ~100 ITM)."""
        position, ivs = _make_single_call_position()
        # Strike is 100
        price_range = np.array([80.0, 120.0])
        result = analyzer.delta_vs_price_at_dtes(position, price_range, ivs, [0.01])
        deltas = result["0.01 DTE"]
        # Deep OTM: delta near 0
        assert abs(deltas[0]) < 5.0
        # Deep ITM: delta near 100 (scaled by multiplier)
        assert deltas[1] > 90.0


class TestGreeksSurface:
    def test_correct_shape(self, analyzer: PositionAnalyzer) -> None:
        position, ivs = _make_single_call_position()
        price_range = np.linspace(80.0, 120.0, 11)
        dte_range = np.array([30.0, 15.0, 7.0])
        result = analyzer.greeks_surface(position, price_range, ivs, dte_range)
        assert isinstance(result, dict)
        for key in ("delta", "gamma", "theta", "vega"):
            assert key in result
            assert result[key].shape == (3, 11)
