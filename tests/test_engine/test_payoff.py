"""Tests for PayoffCalculator."""

from decimal import Decimal

import numpy as np
import pytest

from options_analyzer.domain.enums import OptionType, PositionSide
from options_analyzer.engine.payoff import PayoffCalculator
from tests.factories import (
    make_butterfly,
    make_contract,
    make_iron_condor,
    make_leg,
    make_position,
    make_vertical_spread,
)


@pytest.fixture
def calc() -> PayoffCalculator:
    return PayoffCalculator(risk_free_rate=0.05, dividend_yield=0.0)


@pytest.fixture
def prices() -> np.ndarray:
    return np.linspace(80.0, 120.0, 41)


class TestExpirationPayoff:
    """Expiration payoff (hockey-stick) tests."""

    def test_long_call_shape(self, calc: PayoffCalculator, prices: np.ndarray) -> None:
        """Long call: loss below strike, linear gain above."""
        contract = make_contract(strike=Decimal("100"), option_type=OptionType.CALL)
        leg = make_leg(
            contract=contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        )
        position = make_position(legs=[leg])
        payoff = calc.expiration_payoff(position, prices)
        assert payoff.shape == prices.shape
        # At S=80: max(0, 80-100)*100 - 5*100 = -500
        idx_80 = 0
        assert payoff[idx_80] == pytest.approx(-500.0, abs=1.0)
        # At S=100: max(0, 100-100)*100 - 5*100 = -500
        idx_100 = 20
        assert payoff[idx_100] == pytest.approx(-500.0, abs=1.0)
        # At S=120: max(0, 120-100)*100 - 5*100 = 1500
        idx_120 = 40
        assert payoff[idx_120] == pytest.approx(1500.0, abs=1.0)

    def test_long_put_shape(self, calc: PayoffCalculator, prices: np.ndarray) -> None:
        """Long put: linear gain below strike, loss above."""
        contract = make_contract(strike=Decimal("100"), option_type=OptionType.PUT)
        leg = make_leg(
            contract=contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        )
        position = make_position(legs=[leg])
        payoff = calc.expiration_payoff(position, prices)
        # At S=80: max(0, 100-80)*100 - 5*100 = 1500
        assert payoff[0] == pytest.approx(1500.0, abs=1.0)
        # At S=120: max(0, 100-120)*100 - 5*100 = -500
        assert payoff[40] == pytest.approx(-500.0, abs=1.0)

    def test_vertical_spread_capped(self, calc: PayoffCalculator) -> None:
        """Vertical spread has capped max gain and capped max loss."""
        position = make_vertical_spread("AAPL", [Decimal("100"), Decimal("110")])
        prices = np.linspace(80.0, 130.0, 51)
        payoff = calc.expiration_payoff(position, prices)
        # Max gain is (110-100)*100 - net_debit; max loss is net_debit
        # Payoff should be flat below lower strike and flat above upper strike
        assert payoff[0] == payoff[5]  # both below 100: flat
        assert payoff[-1] == payoff[-5]  # both above 110: flat

    def test_butterfly_tent_shape(self, calc: PayoffCalculator) -> None:
        """Butterfly has a tent shape with max profit at middle strike."""
        position = make_butterfly(
            "AAPL", [Decimal("90"), Decimal("100"), Decimal("110")]
        )
        prices = np.linspace(80.0, 120.0, 41)
        payoff = calc.expiration_payoff(position, prices)
        # Max profit at middle strike (100)
        idx_100 = 20
        idx_90 = 10
        idx_110 = 30
        assert payoff[idx_100] > payoff[idx_90]
        assert payoff[idx_100] > payoff[idx_110]
        # Equal loss on wings
        assert payoff[0] == pytest.approx(payoff[-1], abs=10.0)

    def test_iron_condor_flat_middle(self, calc: PayoffCalculator) -> None:
        """Iron condor has flat profit in middle, losses on wings."""
        position = make_iron_condor(
            "AAPL", [Decimal("85"), Decimal("90"), Decimal("110"), Decimal("115")]
        )
        prices = np.linspace(70.0, 130.0, 61)
        payoff = calc.expiration_payoff(position, prices)
        # Flat in middle (between 90 and 110)
        idx_95 = 25
        idx_100 = 30
        idx_105 = 35
        assert payoff[idx_95] == pytest.approx(payoff[idx_100], abs=1.0)
        assert payoff[idx_100] == pytest.approx(payoff[idx_105], abs=1.0)
        # Losses on wings
        assert payoff[0] < payoff[idx_100]
        assert payoff[-1] < payoff[idx_100]


class TestTheoreticalPnl:
    def test_approaches_expiration_as_dte_decreases(
        self, calc: PayoffCalculator
    ) -> None:
        """Theoretical P&L converges to expiration payoff as DTE → 0."""
        contract = make_contract(strike=Decimal("100"), option_type=OptionType.CALL)
        leg = make_leg(
            contract=contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        )
        position = make_position(legs=[leg])
        prices = np.linspace(80.0, 120.0, 41)
        ivs = {contract.symbol: 0.20}
        expiry = calc.expiration_payoff(position, prices)
        theoretical = calc.theoretical_pnl(position, prices, ivs, dte=0.001)
        # Should be very close to expiration payoff for very small DTE
        np.testing.assert_allclose(theoretical, expiry, atol=5.0)

    def test_theoretical_higher_than_expiry_for_long_option(
        self, calc: PayoffCalculator
    ) -> None:
        """With time value, theoretical P&L >= expiration P&L for long options."""
        contract = make_contract(strike=Decimal("100"), option_type=OptionType.CALL)
        leg = make_leg(
            contract=contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        )
        position = make_position(legs=[leg])
        prices = np.linspace(80.0, 120.0, 41)
        ivs = {contract.symbol: 0.20}
        expiry = calc.expiration_payoff(position, prices)
        theoretical = calc.theoretical_pnl(position, prices, ivs, dte=30.0)
        # Theoretical should be >= expiration for long single option
        assert np.all(theoretical >= expiry - 1.0)

    def test_correct_shape(self, calc: PayoffCalculator) -> None:
        contract = make_contract(strike=Decimal("100"), option_type=OptionType.CALL)
        leg = make_leg(
            contract=contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        )
        position = make_position(legs=[leg])
        prices = np.linspace(80.0, 120.0, 41)
        ivs = {contract.symbol: 0.20}
        result = calc.theoretical_pnl(position, prices, ivs, dte=30.0)
        assert result.shape == (41,)


class TestPnlSurface:
    def test_correct_shape(self, calc: PayoffCalculator) -> None:
        contract = make_contract(strike=Decimal("100"), option_type=OptionType.CALL)
        leg = make_leg(
            contract=contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        )
        position = make_position(legs=[leg])
        prices = np.linspace(80.0, 120.0, 21)
        dte_range = np.array([60.0, 30.0, 15.0, 7.0, 1.0])
        ivs = {contract.symbol: 0.20}
        surface = calc.pnl_surface(position, prices, ivs, dte_range)
        assert surface.shape == (5, 21)

    def test_last_row_near_expiration(self, calc: PayoffCalculator) -> None:
        """Last DTE row (closest to expiry) should approximate expiration payoff."""
        contract = make_contract(strike=Decimal("100"), option_type=OptionType.CALL)
        leg = make_leg(
            contract=contract,
            side=PositionSide.LONG,
            quantity=1,
            open_price=Decimal("5"),
        )
        position = make_position(legs=[leg])
        prices = np.linspace(80.0, 120.0, 21)
        dte_range = np.array([30.0, 0.001])
        ivs = {contract.symbol: 0.20}
        surface = calc.pnl_surface(position, prices, ivs, dte_range)
        expiry = calc.expiration_payoff(position, prices)
        np.testing.assert_allclose(surface[-1], expiry, atol=5.0)
