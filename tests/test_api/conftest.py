"""Fixtures for API tests."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from options_analyzer.api.app import create_app


@pytest.fixture
def app():
    """Create a test FastAPI application."""
    return create_app()


@pytest_asyncio.fixture
async def client(app):
    """Async HTTP client wired to the test app (no running server)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
