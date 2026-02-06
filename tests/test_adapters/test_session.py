"""Tests for TastyTrade session management."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from options_analyzer.adapters.tastytrade.session import TastyTradeSession
from options_analyzer.config.schema import ProviderConfig


@pytest.fixture
def paper_config() -> ProviderConfig:
    return ProviderConfig(
        name="tastytrade",
        username=SecretStr("test_provider_secret"),
        password=SecretStr("test_refresh_token"),
        is_paper=True,
    )


@pytest.fixture
def live_config() -> ProviderConfig:
    return ProviderConfig(
        name="tastytrade",
        username=SecretStr("test_provider_secret"),
        password=SecretStr("test_refresh_token"),
        is_paper=False,
    )


class TestTastyTradeSessionInit:
    def test_stores_config(self, paper_config: ProviderConfig) -> None:
        session = TastyTradeSession(paper_config)
        assert session._config is paper_config

    def test_session_is_none_before_connect(self, paper_config: ProviderConfig) -> None:
        session = TastyTradeSession(paper_config)
        assert session._session is None


class TestTastyTradeSessionProperty:
    def test_raises_if_not_connected(self, paper_config: ProviderConfig) -> None:
        ts = TastyTradeSession(paper_config)
        with pytest.raises(RuntimeError, match="Not connected"):
            _ = ts.session

    def test_returns_session_when_connected(self, paper_config: ProviderConfig) -> None:
        ts = TastyTradeSession(paper_config)
        mock_session = MagicMock()
        ts._session = mock_session
        assert ts.session is mock_session


class TestTastyTradeSessionConnect:
    @pytest.mark.asyncio
    async def test_paper_mode_creates_session_with_is_test_true(
        self, paper_config: ProviderConfig
    ) -> None:
        mock_session = MagicMock()
        with patch(
            "options_analyzer.adapters.tastytrade.session.ProductionSession",
        ) as mock_cls:
            mock_cls.return_value = mock_session
            ts = TastyTradeSession(paper_config)
            await ts.connect()
            mock_cls.assert_called_once_with(
                "test_provider_secret", "test_refresh_token", is_test=True
            )

    @pytest.mark.asyncio
    async def test_live_mode_creates_session_with_is_test_false(
        self, live_config: ProviderConfig
    ) -> None:
        mock_session = MagicMock()
        with patch(
            "options_analyzer.adapters.tastytrade.session.ProductionSession",
        ) as mock_cls:
            mock_cls.return_value = mock_session
            ts = TastyTradeSession(live_config)
            await ts.connect()
            mock_cls.assert_called_once_with(
                "test_provider_secret", "test_refresh_token", is_test=False
            )

    @pytest.mark.asyncio
    async def test_connect_stores_session(self, paper_config: ProviderConfig) -> None:
        mock_session = MagicMock()
        with patch(
            "options_analyzer.adapters.tastytrade.session.ProductionSession",
        ) as mock_cls:
            mock_cls.return_value = mock_session
            ts = TastyTradeSession(paper_config)
            await ts.connect()
            assert ts._session is mock_session


class TestTastyTradeSessionDisconnect:
    @pytest.mark.asyncio
    async def test_disconnect_closes_session(
        self, paper_config: ProviderConfig
    ) -> None:
        mock_session = MagicMock()
        mock_session._client.aclose = AsyncMock()
        with patch(
            "options_analyzer.adapters.tastytrade.session.ProductionSession",
        ) as mock_cls:
            mock_cls.return_value = mock_session
            ts = TastyTradeSession(paper_config)
            await ts.connect()
            await ts.disconnect()
            mock_session._client.aclose.assert_called_once()
            assert ts._session is None

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected_is_noop(
        self, paper_config: ProviderConfig
    ) -> None:
        ts = TastyTradeSession(paper_config)
        await ts.disconnect()  # Should not raise


class TestTastyTradeSessionContextManager:
    @pytest.mark.asyncio
    async def test_context_manager_connects_and_disconnects(
        self, paper_config: ProviderConfig
    ) -> None:
        mock_session = MagicMock()
        mock_session._client.aclose = AsyncMock()
        with patch(
            "options_analyzer.adapters.tastytrade.session.ProductionSession",
        ) as mock_cls:
            mock_cls.return_value = mock_session
            async with TastyTradeSession(paper_config) as ts:
                assert ts._session is mock_session
            mock_session._client.aclose.assert_called_once()
