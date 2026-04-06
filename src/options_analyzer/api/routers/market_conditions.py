"""Market conditions API endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from options_analyzer.api.dependencies import get_providers
from options_analyzer.api.services.market_conditions import (
    VALID_PANELS,
    compute_dashboard,
    compute_panel,
)
from options_analyzer.factory import ProviderContext

router = APIRouter(prefix="/market-conditions")


@router.get("/dashboard")
async def dashboard(
    providers: ProviderContext = Depends(get_providers),
) -> dict[str, Any]:
    """Return full 5-panel market conditions dashboard as Plotly figure JSON."""
    return await compute_dashboard(providers.market_data)


@router.get("/panels/{panel_name}")
async def panel(
    panel_name: str,
    providers: ProviderContext = Depends(get_providers),
) -> dict[str, Any]:
    """Return a single panel figure as Plotly JSON.

    Valid panel names: ema-cloud, dstfs-bias, mc-squares, mc-totals, ivts, borg
    """
    if panel_name not in VALID_PANELS:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown panel: {panel_name!r}. Valid: {VALID_PANELS}",
        )
    return await compute_panel(panel_name, providers.market_data)
