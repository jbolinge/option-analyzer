"""PayoffCalculator — expiration payoff, theoretical P&L, and P&L surfaces."""

import numpy as np

from options_analyzer.domain.enums import OptionType
from options_analyzer.domain.models import Position
from options_analyzer.engine import bsm


class PayoffCalculator:
    """Computes payoff diagrams and P&L surfaces for positions."""

    def __init__(
        self, risk_free_rate: float = 0.05, dividend_yield: float = 0.0
    ) -> None:
        self.risk_free_rate = risk_free_rate
        self.dividend_yield = dividend_yield

    def expiration_payoff(
        self, position: Position, price_range: np.ndarray
    ) -> np.ndarray:
        """P&L at expiration for each price in range."""
        total = np.zeros_like(price_range)
        for leg in position.legs:
            strike = float(leg.contract.strike)
            multiplier = leg.contract.multiplier
            signed_qty = leg.signed_quantity
            open_cost = float(leg.open_price) * signed_qty * multiplier

            if leg.contract.option_type == OptionType.CALL:
                intrinsic = np.maximum(0.0, price_range - strike)
            else:
                intrinsic = np.maximum(0.0, strike - price_range)

            total += intrinsic * signed_qty * multiplier - open_cost
        return total

    def theoretical_pnl(
        self,
        position: Position,
        price_range: np.ndarray,
        ivs: dict[str, float],
        dte: float,
    ) -> np.ndarray:
        """Theoretical P&L at given DTE using BSM pricing."""
        T = dte / 365.0
        total = np.zeros_like(price_range)
        for leg in position.legs:
            strike = float(leg.contract.strike)
            multiplier = leg.contract.multiplier
            signed_qty = leg.signed_quantity
            sigma = ivs[leg.contract.symbol]
            open_cost = float(leg.open_price) * signed_qty * multiplier

            if leg.contract.option_type == OptionType.CALL:
                price_fn = bsm.call_price
            else:
                price_fn = bsm.put_price

            theo_prices = np.array(
                [
                    price_fn(
                        float(S),
                        strike,
                        T,
                        self.risk_free_rate,
                        sigma,
                        self.dividend_yield,
                    )
                    for S in price_range
                ]
            )
            total += theo_prices * signed_qty * multiplier - open_cost
        return total

    def pnl_surface(
        self,
        position: Position,
        price_range: np.ndarray,
        ivs: dict[str, float],
        dte_range: np.ndarray,
    ) -> np.ndarray:
        """2D surface: price x time -> P&L.

        Shape: (len(dte_range), len(price_range)).
        """
        surface = np.zeros((len(dte_range), len(price_range)))
        for i, dte in enumerate(dte_range):
            surface[i] = self.theoretical_pnl(position, price_range, ivs, float(dte))
        return surface
