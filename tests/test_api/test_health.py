"""Tests for the health endpoint."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    """GET /api/health returns 200 with status ok."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_includes_version(client):
    """GET /api/health includes an api_version field."""
    response = await client.get("/api/health")
    data = response.json()
    assert "api_version" in data
