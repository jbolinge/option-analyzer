"""Integration tests for TastyTrade adapter.

These tests require real TastyTrade OAuth credentials and are skipped by default.
Run with: uv run pytest -m integration
"""

import asyncio
import os

import pytest
import pytest_asyncio
from pydantic import SecretStr

from options_analyzer.adapters.tastytrade.account import TastyTradeAccountProvider
from options_analyzer.adapters.tastytrade.market_data import (
    TastyTradeMarketDataProvider,
)
from options_analyzer.adapters.tastytrade.session import TastyTradeSession
from options_analyzer.adapters.tastytrade.streaming import DXLinkStreamerWrapper
from options_analyzer.config.schema import ProviderConfig
from options_analyzer.domain.models import OptionContract

pytestmark = pytest.mark.integration


def _get_config() -> ProviderConfig:
    """Build config from environment variables, or skip."""
    client_secret = os.environ.get("TASTYTRADE_CLIENT_SECRET")
    refresh_token = os.environ.get("TASTYTRADE_REFRESH_TOKEN")
    if not client_secret or not refresh_token:
        pytest.skip("TASTYTRADE_CLIENT_SECRET and TASTYTRADE_REFRESH_TOKEN not set")
    return ProviderConfig(
        name="tastytrade",
        client_secret=SecretStr(client_secret),
        refresh_token=SecretStr(refresh_token),
        is_paper=True,
    )


@pytest_asyncio.fixture
async def tt_session() -> TastyTradeSession:
    config = _get_config()
    session = TastyTradeSession(config)
    await session.connect()
    yield session  # type: ignore[misc]
    await session.disconnect()


class TestSessionIntegration:
    @pytest.mark.asyncio
    async def test_connect_and_validate(self) -> None:
        config = _get_config()
        async with TastyTradeSession(config) as session:
            assert session.session is not None
            is_valid = await session.session.validate()
            assert is_valid


class TestAccountIntegration:
    @pytest.mark.asyncio
    async def test_get_accounts_returns_nonempty(
        self, tt_session: TastyTradeSession
    ) -> None:
        provider = TastyTradeAccountProvider(tt_session)
        accounts = await provider.get_accounts()
        assert len(accounts) > 0
        assert all(isinstance(a, str) for a in accounts)

    @pytest.mark.asyncio
    async def test_get_positions(self, tt_session: TastyTradeSession) -> None:
        provider = TastyTradeAccountProvider(tt_session)
        accounts = await provider.get_accounts()
        positions = await provider.get_positions(accounts[0])
        assert isinstance(positions, list)


class TestMarketDataIntegration:
    @pytest.mark.asyncio
    async def test_get_option_chain_spy(
        self, tt_session: TastyTradeSession
    ) -> None:
        provider = TastyTradeMarketDataProvider(tt_session)
        chain = await provider.get_option_chain("SPY")
        assert len(chain) > 0
        first_expiration = next(iter(chain.values()))
        assert len(first_expiration) > 0
        assert isinstance(first_expiration[0], OptionContract)
        assert first_expiration[0].underlying == "SPY"

    @pytest.mark.asyncio
    async def test_get_underlying_price_spy(
        self, tt_session: TastyTradeSession
    ) -> None:
        provider = TastyTradeMarketDataProvider(tt_session)
        price = await provider.get_underlying_price("SPY")
        assert price > 0
        # SPY should be in a reasonable range
        assert 100 < price < 10000


class TestStreamingIntegration:
    @pytest.mark.asyncio
    async def test_stream_greeks_receives_update(
        self, tt_session: TastyTradeSession
    ) -> None:
        # Get a valid streamer symbol first
        provider = TastyTradeMarketDataProvider(tt_session)
        chain = await provider.get_option_chain("SPY")
        first_exp = next(iter(chain.values()))
        symbols = [
            c.streamer_symbol for c in first_exp[:2] if c.streamer_symbol
        ]
        assert len(symbols) > 0

        wrapper = DXLinkStreamerWrapper(tt_session)
        received = []
        async for symbol, greeks in wrapper.subscribe_greeks(symbols):
            received.append((symbol, greeks))
            if len(received) >= 1:
                break

        assert len(received) >= 1
        assert received[0][1].delta != 0.0 or received[0][1].gamma != 0.0

    @pytest.mark.asyncio
    async def test_stream_quotes_receives_update(
        self, tt_session: TastyTradeSession
    ) -> None:
        wrapper = DXLinkStreamerWrapper(tt_session)
        received = []
        try:
            async with asyncio.timeout(10):
                async for symbol, bid, ask in wrapper.subscribe_quotes(["SPY"]):
                    received.append((symbol, bid, ask))
                    if len(received) >= 1:
                        break
        except TimeoutError:
            pytest.skip("No quote received within 10 seconds")

        assert len(received) >= 1
        assert received[0][1] > 0  # bid > 0
