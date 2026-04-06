"""Tests for SPA static file serving."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from options_analyzer.api.app import _FRONTEND_DIST, create_app


@pytest_asyncio.fixture
async def client_with_dist(tmp_path):
    """Client with a fake frontend/dist directory."""
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    (dist_dir / "assets").mkdir()

    # Create a minimal index.html
    index_html = dist_dir / "index.html"
    index_html.write_text("<html><body>SPA</body></html>")

    # Create a fake asset
    (dist_dir / "assets" / "main.js").write_text("console.log('ok')")

    # Create a favicon
    (dist_dir / "favicon.svg").write_text("<svg></svg>")

    with patch("options_analyzer.api.app._FRONTEND_DIST", dist_dir):
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest_asyncio.fixture
async def client_without_dist():
    """Client when frontend/dist does not exist."""
    with patch("options_analyzer.api.app._FRONTEND_DIST", Path("/nonexistent")):
        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


@pytest.mark.asyncio
async def test_api_routes_take_priority(client_with_dist):
    """API routes respond even when SPA is mounted."""
    response = await client_with_dist.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_spa_serves_index_html(client_with_dist):
    """Root path returns index.html."""
    response = await client_with_dist.get("/")
    assert response.status_code == 200
    assert "SPA" in response.text


@pytest.mark.asyncio
async def test_spa_serves_static_assets(client_with_dist):
    """Static assets are served from /assets/."""
    response = await client_with_dist.get("/assets/main.js")
    assert response.status_code == 200
    assert "console.log" in response.text


@pytest.mark.asyncio
async def test_spa_serves_root_files(client_with_dist):
    """Root-level static files like favicon.svg are served."""
    response = await client_with_dist.get("/favicon.svg")
    assert response.status_code == 200
    assert "<svg>" in response.text


@pytest.mark.asyncio
async def test_spa_fallback_for_unknown_paths(client_with_dist):
    """Unknown paths fall back to index.html (client-side routing)."""
    response = await client_with_dist.get("/some/unknown/route")
    assert response.status_code == 200
    assert "SPA" in response.text


@pytest.mark.asyncio
async def test_api_works_without_dist(client_without_dist):
    """API works fine when frontend/dist does not exist."""
    response = await client_without_dist.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
