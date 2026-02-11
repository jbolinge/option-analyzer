"""Tests for the provider factory."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from options_analyzer.config.schema import AppConfig, ProviderConfig
from options_analyzer.factory import ProviderContext, create_providers
from options_analyzer.ports.account import AccountProvider
from options_analyzer.ports.market_data import MarketDataProvider

_SESSION = "options_analyzer.adapters.tastytrade.session.TastyTradeSession"
_MARKET_DATA = (
    "options_analyzer.adapters.tastytrade.market_data"
    ".TastyTradeMarketDataProvider"
)
_ACCOUNT = (
    "options_analyzer.adapters.tastytrade.account.TastyTradeAccountProvider"
)


def _make_config(provider_name: str = "tastytrade", is_paper: bool = True) -> AppConfig:
    return AppConfig(
        provider=ProviderConfig(
            name=provider_name,
            client_secret=SecretStr("test-secret"),
            refresh_token=SecretStr("test-token"),
            is_paper=is_paper,
        ),
    )


class TestCreateProviders:
    @pytest.mark.asyncio
    async def test_creates_tastytrade_providers(self) -> None:
        config = _make_config()

        with (
            patch(_SESSION) as mock_session_cls,
            patch(_MARKET_DATA) as mock_md_cls,
            patch(_ACCOUNT) as mock_acct_cls,
        ):
            mock_session = MagicMock()
            mock_session.connect = AsyncMock()
            mock_session_cls.return_value = mock_session

            ctx = await create_providers(config)

            mock_session_cls.assert_called_once_with(config.provider)
            mock_session.connect.assert_called_once()
            mock_md_cls.assert_called_once_with(mock_session)
            mock_acct_cls.assert_called_once_with(mock_session)
            assert isinstance(ctx, ProviderContext)

    @pytest.mark.asyncio
    async def test_provider_name_paper(self) -> None:
        config = _make_config(is_paper=True)

        with (
            patch(_SESSION) as mock_cls,
            patch(_MARKET_DATA),
            patch(_ACCOUNT),
        ):
            mock_cls.return_value = MagicMock(connect=AsyncMock())
            ctx = await create_providers(config)
            assert ctx.provider_name == "TastyTrade (paper)"

    @pytest.mark.asyncio
    async def test_provider_name_live(self) -> None:
        config = _make_config(is_paper=False)

        with (
            patch(_SESSION) as mock_cls,
            patch(_MARKET_DATA),
            patch(_ACCOUNT),
        ):
            mock_cls.return_value = MagicMock(connect=AsyncMock())
            ctx = await create_providers(config)
            assert ctx.provider_name == "TastyTrade (live)"

    @pytest.mark.asyncio
    async def test_unknown_provider_raises(self) -> None:
        config = _make_config(provider_name="unknown_broker")
        with pytest.raises(ValueError, match="Unknown provider"):
            await create_providers(config)

    @pytest.mark.asyncio
    async def test_case_insensitive_provider_name(self) -> None:
        config = _make_config(provider_name="TastyTrade")

        with (
            patch(_SESSION) as mock_cls,
            patch(_MARKET_DATA),
            patch(_ACCOUNT),
        ):
            mock_cls.return_value = MagicMock(connect=AsyncMock())
            ctx = await create_providers(config)
            assert ctx is not None


class TestProviderContext:
    @pytest.mark.asyncio
    async def test_disconnect_delegates_to_market_data(self) -> None:
        mock_md = AsyncMock(spec=MarketDataProvider)
        mock_acct = AsyncMock(spec=AccountProvider)
        ctx = ProviderContext(
            market_data=mock_md, account=mock_acct, provider_name="Test"
        )
        await ctx.disconnect()
        mock_md.disconnect.assert_called_once()

    def test_exposes_port_typed_providers(self) -> None:
        mock_md = MagicMock(spec=MarketDataProvider)
        mock_acct = MagicMock(spec=AccountProvider)
        ctx = ProviderContext(
            market_data=mock_md, account=mock_acct, provider_name="Test"
        )
        assert ctx.market_data is mock_md
        assert ctx.account is mock_acct
        assert ctx.provider_name == "Test"
