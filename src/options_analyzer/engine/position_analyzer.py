"""PositionAnalyzer — aggregate Greeks across legs and generate risk profiles."""

from datetime import date

import numpy as np

from options_analyzer.domain.greeks import (
    FirstOrderGreeks,
    FullGreeks,
    PositionGreeks,
    SecondOrderGreeks,
)
from options_analyzer.domain.models import Position
from options_analyzer.engine.greeks_calculator import GreeksCalculator

ALL_GREEK_NAMES = (
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
)


class PositionAnalyzer:
    """Computes position-level Greeks by aggregating across legs."""

    def __init__(self, greeks_calculator: GreeksCalculator) -> None:
        self.greeks_calculator = greeks_calculator

    def position_greeks(
        self, position: Position, spot: float, ivs: dict[str, float]
    ) -> PositionGreeks:
        """Compute per-leg and aggregated Greeks for entire position."""
        per_leg: dict[str, FullGreeks] = {}
        agg_first = {k: 0.0 for k in ("delta", "gamma", "theta", "vega", "rho", "iv")}
        agg_second = {
            k: 0.0 for k in ("vanna", "volga", "charm", "veta", "speed", "color")
        }

        for leg in position.legs:
            contract = leg.contract
            sigma = ivs[contract.symbol]
            T = max(
                (contract.expiration - date.today()).days / 365.0,
                0.0,
            )
            scale = leg.signed_quantity * contract.multiplier

            full = self.greeks_calculator.full(
                spot, float(contract.strike), T, sigma, contract.option_type
            )

            # Scaled Greeks for this leg
            scaled_first = FirstOrderGreeks(
                delta=full.first_order.delta * scale,
                gamma=full.first_order.gamma * scale,
                theta=full.first_order.theta * scale,
                vega=full.first_order.vega * scale,
                rho=full.first_order.rho * scale,
                iv=sigma,
            )
            scaled_second = SecondOrderGreeks(
                vanna=full.second_order.vanna * scale,
                volga=full.second_order.volga * scale,
                charm=full.second_order.charm * scale,
                veta=full.second_order.veta * scale,
                speed=full.second_order.speed * scale,
                color=full.second_order.color * scale,
            )
            scaled_full = FullGreeks(
                first_order=scaled_first, second_order=scaled_second
            )
            per_leg[contract.symbol] = scaled_full

            for k in ("delta", "gamma", "theta", "vega", "rho"):
                agg_first[k] += getattr(scaled_first, k)
            for k in ("vanna", "volga", "charm", "veta", "speed", "color"):
                agg_second[k] += getattr(scaled_second, k)

        # Average IV across legs (weighted equally)
        if per_leg:
            agg_first["iv"] = sum(
                ivs[leg.contract.symbol] for leg in position.legs
            ) / len(position.legs)

        aggregated = FullGreeks(
            first_order=FirstOrderGreeks(**agg_first),
            second_order=SecondOrderGreeks(**agg_second),
        )
        return PositionGreeks(per_leg=per_leg, aggregated=aggregated)

    def greeks_vs_price(
        self,
        position: Position,
        price_range: np.ndarray,
        ivs: dict[str, float],
    ) -> dict[str, np.ndarray]:
        """Greeks profiles across price range."""
        result: dict[str, list[float]] = {k: [] for k in ALL_GREEK_NAMES}
        for S in price_range:
            pg = self.position_greeks(position, float(S), ivs)
            agg = pg.aggregated
            result["delta"].append(agg.first_order.delta)
            result["gamma"].append(agg.first_order.gamma)
            result["theta"].append(agg.first_order.theta)
            result["vega"].append(agg.first_order.vega)
            result["rho"].append(agg.first_order.rho)
            result["vanna"].append(agg.second_order.vanna)
            result["volga"].append(agg.second_order.volga)
            result["charm"].append(agg.second_order.charm)
            result["veta"].append(agg.second_order.veta)
            result["speed"].append(agg.second_order.speed)
            result["color"].append(agg.second_order.color)
        return {k: np.array(v) for k, v in result.items()}

    def greeks_vs_time(
        self,
        position: Position,
        spot: float,
        ivs: dict[str, float],
        dte_range: np.ndarray,
    ) -> dict[str, np.ndarray]:
        """Greeks decay across time range (using DTE in days)."""
        result: dict[str, list[float]] = {k: [] for k in ALL_GREEK_NAMES}
        for dte in dte_range:
            T = float(dte) / 365.0
            agg_first = {k: 0.0 for k in ("delta", "gamma", "theta", "vega", "rho")}
            agg_second = {
                k: 0.0 for k in ("vanna", "volga", "charm", "veta", "speed", "color")
            }
            for leg in position.legs:
                contract = leg.contract
                sigma = ivs[contract.symbol]
                scale = leg.signed_quantity * contract.multiplier
                full = self.greeks_calculator.full(
                    spot, float(contract.strike), T, sigma, contract.option_type
                )
                for k in ("delta", "gamma", "theta", "vega", "rho"):
                    agg_first[k] += getattr(full.first_order, k) * scale
                for k in ("vanna", "volga", "charm", "veta", "speed", "color"):
                    agg_second[k] += getattr(full.second_order, k) * scale
            for k in agg_first:
                result[k].append(agg_first[k])
            for k in agg_second:
                result[k].append(agg_second[k])
        return {k: np.array(v) for k, v in result.items()}

    def delta_vs_price_at_dtes(
        self,
        position: Position,
        price_range: np.ndarray,
        ivs: dict[str, float],
        dtes: list[float],
    ) -> dict[str, np.ndarray]:
        """Position delta across price range at multiple DTEs.

        Returns dict mapping labels like "60 DTE" to delta arrays.
        Useful for visualizing charm (dDelta/dTime).
        """
        result: dict[str, np.ndarray] = {}
        for dte in dtes:
            T = dte / 365.0
            deltas: list[float] = []
            for S in price_range:
                agg_delta = 0.0
                for leg in position.legs:
                    contract = leg.contract
                    sigma = ivs[contract.symbol]
                    scale = leg.signed_quantity * contract.multiplier
                    full = self.greeks_calculator.full(
                        float(S), float(contract.strike), T, sigma, contract.option_type
                    )
                    agg_delta += full.first_order.delta * scale
                deltas.append(agg_delta)
            label = f"{dte:g} DTE"
            result[label] = np.array(deltas)
        return result

    def greeks_surface(
        self,
        position: Position,
        price_range: np.ndarray,
        ivs: dict[str, float],
        dte_range: np.ndarray,
    ) -> dict[str, np.ndarray]:
        """3D surfaces: Greeks across price x time."""
        surfaces: dict[str, np.ndarray] = {
            k: np.zeros((len(dte_range), len(price_range))) for k in ALL_GREEK_NAMES
        }
        for i, dte in enumerate(dte_range):
            T = float(dte) / 365.0
            for j, S in enumerate(price_range):
                agg_first = {k: 0.0 for k in ("delta", "gamma", "theta", "vega", "rho")}
                agg_second = {
                    k: 0.0
                    for k in ("vanna", "volga", "charm", "veta", "speed", "color")
                }
                for leg in position.legs:
                    contract = leg.contract
                    sigma = ivs[contract.symbol]
                    scale = leg.signed_quantity * contract.multiplier
                    full = self.greeks_calculator.full(
                        float(S), float(contract.strike), T, sigma, contract.option_type
                    )
                    for k in ("delta", "gamma", "theta", "vega", "rho"):
                        agg_first[k] += getattr(full.first_order, k) * scale
                    for k in ("vanna", "volga", "charm", "veta", "speed", "color"):
                        agg_second[k] += getattr(full.second_order, k) * scale
                for k in agg_first:
                    surfaces[k][i, j] = agg_first[k]
                for k in agg_second:
                    surfaces[k][i, j] = agg_second[k]
        return surfaces
