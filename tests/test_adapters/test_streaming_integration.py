"""Integration test verifying DXLink streaming auth works after SDK upgrade.

The tastytrade SDK v12.0.1 had a bug where DXLinkStreamer auth would fail with:
    AuthException: Session not found: api

SDK v12.0.2 includes the httpx-ws CancelScope fix that resolves this.
This test confirms DXLink can connect and receive at least one quote event.

Run with: uv run pytest -m integration tests/test_adapters/test_streaming_integration.py
"""

import asyncio
import os

import pytest
from tastytrade import DXLinkStreamer, Session
from tastytrade.dxfeed import Quote

pytestmark = pytest.mark.integration


def _get_session() -> Session:
    """Create a tastytrade Session from env vars, or skip."""
    client_secret = os.environ.get("TASTYTRADE_CLIENT_SECRET")
    refresh_token = os.environ.get("TASTYTRADE_REFRESH_TOKEN")
    if not client_secret or not refresh_token:
        pytest.skip("TASTYTRADE_CLIENT_SECRET and TASTYTRADE_REFRESH_TOKEN not set")
    return Session(client_secret, refresh_token, is_test=True)


class TestDXLinkAuth:
    """Verify DXLink WebSocket connects and receives quotes after SDK upgrade."""

    @pytest.mark.asyncio
    async def test_dxlink_receives_quote(self) -> None:
        session = _get_session()
        try:
            async with asyncio.timeout(15):
                async with DXLinkStreamer(session) as streamer:
                    await streamer.subscribe(Quote, ["SPY"])
                    quote = await streamer.get_event(Quote)
                    assert quote.event_symbol == "SPY"
                    assert quote.bid_price > 0
                    assert quote.ask_price > 0
        except TimeoutError:
            pytest.fail("DXLink streamer timed out — auth may still be broken")
        finally:
            await session._client.aclose()
