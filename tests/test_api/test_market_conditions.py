"""Tests for the market conditions API endpoints."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import numpy as np
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from options_analyzer.api.app import create_app
from options_analyzer.api.dependencies import get_providers
from options_analyzer.domain.candles import CandleBar, CandleSeries
from options_analyzer.engine.borg_transwarp import BORG_TICKERS
from options_analyzer.factory import ProviderContext


def _make_test_candle_series(
    symbol: str, n: int = 300, seed: int = 42
) -> CandleSeries:
    """Create a CandleSeries with realistic-enough data for indicator computation."""
    rng = np.random.default_rng(seed + hash(symbol) % 1000)
    base = rng.uniform(50, 500)
    bars: list[CandleBar] = []
    price = base
    for i in range(n):
        change = rng.normal(0, 2.0)
        close = price + change
        high = max(price, close) + abs(rng.normal(0, 1.0))
        low = min(price, close) - abs(rng.normal(0, 1.0))
        bars.append(
            CandleBar(
                symbol=symbol,
                timestamp=datetime(2024, 1, 1, 16, 0, tzinfo=UTC)
                + timedelta(days=i),
                open=price,
                high=high,
                low=low,
                close=close,
                volume=int(rng.integers(500_000, 2_000_000)),
            )
        )
        price = close
    return CandleSeries(bars=bars)


def _build_mock_providers() -> ProviderContext:
    """Create a ProviderContext with mocked market data returning synthetic candles."""
    # All symbols the dashboard needs
    all_symbols = list(dict.fromkeys(BORG_TICKERS + ["SPX", "VIX", "VIX3M"]))

    # Pre-build candle series for each symbol
    candle_map = {sym: _make_test_candle_series(sym, n=300) for sym in all_symbols}

    mock_market_data = AsyncMock()
    mock_market_data.get_candles_batch = AsyncMock(return_value=candle_map)
    mock_market_data.disconnect = AsyncMock()

    mock_account = AsyncMock()

    return ProviderContext(
        market_data=mock_market_data,
        account=mock_account,
        provider_name="MockProvider (test)",
    )


@pytest.fixture
def mock_providers() -> ProviderContext:
    return _build_mock_providers()


@pytest.fixture
def app(mock_providers):
    test_app = create_app()
    test_app.dependency_overrides[get_providers] = lambda: mock_providers
    return test_app


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_dashboard_returns_plotly_figure(client):
    """GET /api/market-conditions/dashboard returns valid Plotly figure JSON."""
    response = await client.get("/api/market-conditions/dashboard")
    assert response.status_code == 200

    data = response.json()
    assert "figure" in data
    assert "computed_at" in data
    assert data["symbol"] == "SPX"

    # Plotly figure structure
    figure = data["figure"]
    assert "data" in figure
    assert "layout" in figure
    assert isinstance(figure["data"], list)
    assert len(figure["data"]) > 0


@pytest.mark.asyncio
async def test_dashboard_figure_has_traces(client):
    """Dashboard figure contains multiple traces for the 5-panel grid."""
    response = await client.get("/api/market-conditions/dashboard")
    figure = response.json()["figure"]
    # Full grid has candlestick + EMA traces + bias bars + MC markers + IVTS + Borg
    assert len(figure["data"]) >= 5


@pytest.mark.asyncio
async def test_panel_ema_cloud(client):
    """GET /api/market-conditions/panels/ema-cloud returns valid figure."""
    response = await client.get("/api/market-conditions/panels/ema-cloud")
    assert response.status_code == 200

    data = response.json()
    assert data["panel"] == "ema-cloud"
    assert "data" in data["figure"]


@pytest.mark.asyncio
async def test_panel_ivts(client):
    """GET /api/market-conditions/panels/ivts returns valid figure."""
    response = await client.get("/api/market-conditions/panels/ivts")
    assert response.status_code == 200
    assert response.json()["panel"] == "ivts"


@pytest.mark.asyncio
async def test_panel_invalid_returns_404(client):
    """GET /api/market-conditions/panels/invalid returns 404."""
    response = await client.get("/api/market-conditions/panels/nonexistent")
    assert response.status_code == 404
    assert "nonexistent" in response.json()["detail"]


@pytest.mark.asyncio
async def test_health_still_works(client):
    """Health endpoint is unaffected by market conditions wiring."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
