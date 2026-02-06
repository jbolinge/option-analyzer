"""Tests for TastyTrade account provider."""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from options_analyzer.adapters.tastytrade.account import TastyTradeAccountProvider
from options_analyzer.adapters.tastytrade.session import TastyTradeSession
from options_analyzer.domain.enums import PositionSide
from options_analyzer.domain.models import Leg
from options_analyzer.ports.account import AccountProvider


def _make_sdk_account(account_number: str = "5WX01234") -> MagicMock:
    mock = MagicMock()
    mock.account_number = account_number
    return mock


def _make_sdk_option(**overrides: object) -> MagicMock:
    defaults = {
        "symbol": "SPY  260220C00450000",
        "underlying_symbol": "SPY",
        "strike_price": Decimal("450"),
        "expiration_date": date(2026, 2, 20),
        "exercise_style": "American",
        "shares_per_contract": 100,
        "streamer_symbol": ".SPY260220C450",
    }
    defaults.update(overrides)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    mock.option_type.value = overrides.get("option_type_value", "C")
    return mock


def _make_sdk_position(**overrides: object) -> MagicMock:
    defaults = {
        "symbol": "SPY  260220C00450000",
        "underlying_symbol": "SPY",
        "quantity": Decimal("1"),
        "quantity_direction": "Long",
        "average_open_price": Decimal("12.50"),
        "multiplier": 100,
        "instrument_type": MagicMock(),
    }
    defaults.update(overrides)
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


@pytest.fixture
def mock_session() -> MagicMock:
    mock = MagicMock(spec=TastyTradeSession)
    mock.session = MagicMock()
    return mock


class TestTastyTradeAccountProviderIsPort:
    def test_implements_account_provider(self) -> None:
        assert issubclass(TastyTradeAccountProvider, AccountProvider)


class TestGetAccounts:
    @pytest.mark.asyncio
    async def test_returns_account_numbers(self, mock_session: MagicMock) -> None:
        sdk_accounts = [
            _make_sdk_account("5WX01234"),
            _make_sdk_account("5WX05678"),
        ]
        with patch(
            "options_analyzer.adapters.tastytrade.account.Account"
        ) as mock_account_cls:
            mock_account_cls.get = AsyncMock(return_value=sdk_accounts)
            provider = TastyTradeAccountProvider(mock_session)
            result = await provider.get_accounts()
            assert result == ["5WX01234", "5WX05678"]
            mock_account_cls.get.assert_called_once_with(mock_session.session)

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, mock_session: MagicMock) -> None:
        with patch(
            "options_analyzer.adapters.tastytrade.account.Account"
        ) as mock_account_cls:
            mock_account_cls.get = AsyncMock(return_value=[])
            provider = TastyTradeAccountProvider(mock_session)
            result = await provider.get_accounts()
            assert result == []


class TestGetPositions:
    @pytest.mark.asyncio
    async def test_returns_legs_for_account(self, mock_session: MagicMock) -> None:
        sdk_positions = [
            _make_sdk_position(
                symbol="SPY  260220C00450000",
                quantity=Decimal("2"),
                quantity_direction="Long",
            ),
        ]
        sdk_account = _make_sdk_account("5WX01234")
        sdk_account.get_positions = AsyncMock(return_value=sdk_positions)

        sdk_option = _make_sdk_option()

        with (
            patch(
                "options_analyzer.adapters.tastytrade.account.Account"
            ) as mock_account_cls,
            patch(
                "options_analyzer.adapters.tastytrade.account.get_option_chain",
                new_callable=AsyncMock,
            ) as mock_get_chain,
        ):
            mock_account_cls.get = AsyncMock(return_value=sdk_account)
            mock_get_chain.return_value = {date(2026, 2, 20): [sdk_option]}

            provider = TastyTradeAccountProvider(mock_session)
            result = await provider.get_positions("5WX01234", underlying="SPY")

            assert len(result) == 1
            assert isinstance(result[0], Leg)
            assert result[0].side == PositionSide.LONG
            assert result[0].quantity == 2

    @pytest.mark.asyncio
    async def test_returns_empty_for_no_positions(
        self, mock_session: MagicMock
    ) -> None:
        sdk_account = _make_sdk_account("5WX01234")
        sdk_account.get_positions = AsyncMock(return_value=[])

        with patch(
            "options_analyzer.adapters.tastytrade.account.Account"
        ) as mock_account_cls:
            mock_account_cls.get = AsyncMock(return_value=sdk_account)
            provider = TastyTradeAccountProvider(mock_session)
            result = await provider.get_positions("5WX01234")
            assert result == []

    @pytest.mark.asyncio
    async def test_filters_by_underlying(self, mock_session: MagicMock) -> None:
        sdk_account = _make_sdk_account("5WX01234")
        sdk_account.get_positions = AsyncMock(return_value=[])

        with patch(
            "options_analyzer.adapters.tastytrade.account.Account"
        ) as mock_account_cls:
            mock_account_cls.get = AsyncMock(return_value=sdk_account)
            provider = TastyTradeAccountProvider(mock_session)
            await provider.get_positions("5WX01234", underlying="AAPL")
            sdk_account.get_positions.assert_called_once()
            call_kwargs = sdk_account.get_positions.call_args
            assert call_kwargs[1].get("underlying_symbols") == ["AAPL"]
