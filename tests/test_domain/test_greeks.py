"""Tests for Greeks domain models."""

import pytest
from pydantic import ValidationError

from options_analyzer.domain.greeks import (
    FirstOrderGreeks,
    FullGreeks,
    PositionGreeks,
    SecondOrderGreeks,
)


class TestFirstOrderGreeks:
    def test_creation(self) -> None:
        greeks = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        assert greeks.delta == 0.55
        assert greeks.gamma == 0.05
        assert greeks.theta == -0.03
        assert greeks.vega == 0.20
        assert greeks.rho == 0.01
        assert greeks.iv == 0.25

    def test_frozen(self) -> None:
        greeks = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        with pytest.raises(ValidationError):
            greeks.delta = 0.6  # type: ignore[misc]

    def test_serialization_roundtrip(self) -> None:
        greeks = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        data = greeks.model_dump()
        restored = FirstOrderGreeks.model_validate(data)
        assert restored == greeks


class TestSecondOrderGreeks:
    def test_creation(self) -> None:
        greeks = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        assert greeks.vanna == 0.01
        assert greeks.volga == 0.02
        assert greeks.charm == -0.001
        assert greeks.veta == -0.005
        assert greeks.speed == 0.0001
        assert greeks.color == -0.0001

    def test_frozen(self) -> None:
        greeks = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        with pytest.raises(ValidationError):
            greeks.vanna = 0.5  # type: ignore[misc]

    def test_serialization_roundtrip(self) -> None:
        greeks = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        data = greeks.model_dump()
        restored = SecondOrderGreeks.model_validate(data)
        assert restored == greeks


class TestFullGreeks:
    def test_composition(self) -> None:
        first = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        second = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        full = FullGreeks(first_order=first, second_order=second)
        assert full.first_order == first
        assert full.second_order == second

    def test_frozen(self) -> None:
        first = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        second = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        full = FullGreeks(first_order=first, second_order=second)
        with pytest.raises(ValidationError):
            full.first_order = first  # type: ignore[misc]

    def test_serialization_roundtrip(self) -> None:
        first = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        second = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        full = FullGreeks(first_order=first, second_order=second)
        data = full.model_dump()
        restored = FullGreeks.model_validate(data)
        assert restored == full


class TestPositionGreeks:
    def test_per_leg_and_aggregated(self) -> None:
        first = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        second = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        full = FullGreeks(first_order=first, second_order=second)

        pos_greeks = PositionGreeks(
            per_leg={"AAPL  240119C00150000": full},
            aggregated=full,
        )
        assert "AAPL  240119C00150000" in pos_greeks.per_leg
        assert pos_greeks.per_leg["AAPL  240119C00150000"] == full
        assert pos_greeks.aggregated == full

    def test_frozen(self) -> None:
        first = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        second = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        full = FullGreeks(first_order=first, second_order=second)
        pos_greeks = PositionGreeks(per_leg={}, aggregated=full)
        with pytest.raises(ValidationError):
            pos_greeks.aggregated = full  # type: ignore[misc]

    def test_serialization_roundtrip(self) -> None:
        first = FirstOrderGreeks(
            delta=0.55, gamma=0.05, theta=-0.03, vega=0.20, rho=0.01, iv=0.25
        )
        second = SecondOrderGreeks(
            vanna=0.01,
            volga=0.02,
            charm=-0.001,
            veta=-0.005,
            speed=0.0001,
            color=-0.0001,
        )
        full = FullGreeks(first_order=first, second_order=second)
        pos_greeks = PositionGreeks(
            per_leg={"SYM1": full},
            aggregated=full,
        )
        data = pos_greeks.model_dump()
        restored = PositionGreeks.model_validate(data)
        assert restored == pos_greeks
