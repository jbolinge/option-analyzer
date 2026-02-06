"""Greeks domain models — first-order, second-order, full, and position-level."""

from pydantic import BaseModel, ConfigDict


class FirstOrderGreeks(BaseModel):
    """First-order Greeks sourced from data provider."""

    model_config = ConfigDict(frozen=True)

    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    iv: float


class SecondOrderGreeks(BaseModel):
    """Second-order Greeks computed via BSM engine."""

    model_config = ConfigDict(frozen=True)

    vanna: float
    volga: float
    charm: float
    veta: float
    speed: float
    color: float


class FullGreeks(BaseModel):
    """Combined first and second order Greeks for a single contract."""

    model_config = ConfigDict(frozen=True)

    first_order: FirstOrderGreeks
    second_order: SecondOrderGreeks


class PositionGreeks(BaseModel):
    """Greeks at the position level — per-leg breakdown and aggregated totals."""

    model_config = ConfigDict(frozen=True)

    per_leg: dict[str, FullGreeks]
    aggregated: FullGreeks
