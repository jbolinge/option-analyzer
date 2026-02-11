"""Tests for TastyTrade market data provider."""

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from options_analyzer.adapters.tastytrade.market_data import (
    TastyTradeMarketDataProvider,
)
from options_analyzer.adapters.tastytrade.session import TastyTradeSession
from options_analyzer.domain.enums import OptionType
from options_analyzer.domain.greeks import FirstOrderGreeks
from options_analyzer.domain.models import OptionContract
from options_analyzer.domain.streaming import GreeksUpdate, QuoteUpdate
from options_analyzer.ports.market_data import MarketDataProvider


def _make_sdk_option(
    symbol: str = "SPY  260220C00450000",
    underlying: str = "SPY",
    option_type_value: str = "C",
    strike: Decimal = Decimal("450"),
    expiration: date = date(2026, 2, 20),
    streamer_symbol: str = ".SPY260220C450",
) -> MagicMock:
    mock = MagicMock()
    mock.symbol = symbol
    mock.underlying_symbol = underlying
    mock.option_type.value = option_type_value
    mock.strike_price = strike
    mock.expiration_date = expiration
    mock.exercise_style = "American"
    mock.shares_per_contract = 100
    mock.streamer_symbol = streamer_symbol
    return mock


@pytest.fixture
def mock_session() -> MagicMock:
    mock = MagicMock(spec=TastyTradeSession)
    mock.session = MagicMock()
    return mock


class TestTastyTradeMarketDataProviderIsPort:
    def test_implements_market_data_provider(self) -> None:
        assert issubclass(TastyTradeMarketDataProvider, MarketDataProvider)


class TestGetOptionChain:
    @pytest.mark.asyncio
    async def test_returns_mapped_option_chain(self, mock_session: MagicMock) -> None:
        exp_date = date(2026, 2, 20)
        sdk_options = [
            _make_sdk_option(
                symbol="SPY  260220C00450000",
                strike=Decimal("450"),
                streamer_symbol=".SPY260220C450",
            ),
            _make_sdk_option(
                symbol="SPY  260220P00450000",
                option_type_value="P",
                strike=Decimal("450"),
                streamer_symbol=".SPY260220P450",
            ),
        ]
        sdk_chain = {exp_date: sdk_options}

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
            new_callable=AsyncMock,
            return_value=sdk_chain,
        ) as mock_get_chain:
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_option_chain("SPY")

            mock_get_chain.assert_called_once_with(mock_session.session, "SPY")
            assert exp_date in result
            contracts = result[exp_date]
            assert len(contracts) == 2
            assert isinstance(contracts[0], OptionContract)
            assert contracts[0].option_type == OptionType.CALL
            assert contracts[1].option_type == OptionType.PUT

    @pytest.mark.asyncio
    async def test_populates_streamer_symbol_registry(
        self, mock_session: MagicMock
    ) -> None:
        exp_date = date(2026, 2, 20)
        sdk_options = [
            _make_sdk_option(
                symbol="SPY  260220C00450000",
                strike=Decimal("450"),
                streamer_symbol=".SPY260220C450",
            ),
            _make_sdk_option(
                symbol="SPY  260220P00450000",
                option_type_value="P",
                strike=Decimal("450"),
                streamer_symbol=".SPY260220P450",
            ),
        ]
        sdk_chain = {exp_date: sdk_options}

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
            new_callable=AsyncMock,
            return_value=sdk_chain,
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_option_chain("SPY")

            contracts = result[exp_date]
            streamer_symbols = provider.get_streamer_symbols(contracts)
            assert ".SPY260220C450" in streamer_symbols
            assert ".SPY260220P450" in streamer_symbols
            assert len(streamer_symbols) == 2

    @pytest.mark.asyncio
    async def test_returns_empty_chain(self, mock_session: MagicMock) -> None:
        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
            new_callable=AsyncMock,
            return_value={},
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_option_chain("INVALID")
            assert result == {}


class TestGetUnderlyingPrice:
    @pytest.mark.asyncio
    async def test_returns_mid_when_available(self, mock_session: MagicMock) -> None:
        mock_data = MagicMock()
        mock_data.mid = Decimal("450.15")
        mock_data.bid = Decimal("450.10")
        mock_data.ask = Decimal("450.20")
        mock_data.mark = Decimal("450.12")

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_market_data",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_underlying_price("SPY")
            assert result == Decimal("450.15")

    @pytest.mark.asyncio
    async def test_falls_back_to_bid_ask_avg(self, mock_session: MagicMock) -> None:
        mock_data = MagicMock()
        mock_data.mid = None
        mock_data.bid = Decimal("450.10")
        mock_data.ask = Decimal("450.20")
        mock_data.mark = Decimal("450.12")

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_market_data",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_underlying_price("SPY")
            assert result == Decimal("450.15")

    @pytest.mark.asyncio
    async def test_falls_back_to_mark(self, mock_session: MagicMock) -> None:
        mock_data = MagicMock()
        mock_data.mid = None
        mock_data.bid = None
        mock_data.ask = None
        mock_data.mark = Decimal("450.12")

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_market_data",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            result = await provider.get_underlying_price("SPY")
            assert result == Decimal("450.12")


class TestConnectDisconnect:
    @pytest.mark.asyncio
    async def test_connect_delegates_to_session(self, mock_session: MagicMock) -> None:
        mock_session.connect = AsyncMock()
        provider = TastyTradeMarketDataProvider(mock_session)
        await provider.connect()
        mock_session.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_delegates_to_session(
        self, mock_session: MagicMock
    ) -> None:
        mock_session.disconnect = AsyncMock()
        provider = TastyTradeMarketDataProvider(mock_session)
        await provider.disconnect()
        mock_session.disconnect.assert_called_once()


def _make_contract(
    symbol: str = "SPY  260220C00450000",
    underlying: str = "SPY",
    option_type: OptionType = OptionType.CALL,
    strike: Decimal = Decimal("450"),
    expiration: date = date(2026, 2, 20),
) -> OptionContract:
    return OptionContract(
        symbol=symbol,
        underlying=underlying,
        option_type=option_type,
        strike=strike,
        expiration=expiration,
    )


def _sdk_chain_for(contracts_and_streamers: list[tuple[str, str, str]]) -> dict:
    """Build a fake SDK chain dict from (symbol, underlying, streamer_symbol) tuples."""
    exp = date(2026, 2, 20)
    options = []
    for sym, underlying, streamer in contracts_and_streamers:
        options.append(
            _make_sdk_option(symbol=sym, underlying=underlying, streamer_symbol=streamer)
        )
    return {exp: options}


class TestEnsureStreamerSymbols:
    @pytest.mark.asyncio
    async def test_auto_resolves_missing_streamer_symbols(
        self, mock_session: MagicMock
    ) -> None:
        contract = _make_contract()
        sdk_chain = _sdk_chain_for([
            ("SPY  260220C00450000", "SPY", ".SPY260220C450"),
        ])

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
            new_callable=AsyncMock,
            return_value=sdk_chain,
        ) as mock_get_chain:
            provider = TastyTradeMarketDataProvider(mock_session)
            assert provider._streamer_symbols == {}

            await provider._ensure_streamer_symbols([contract])

            mock_get_chain.assert_called_once_with(mock_session.session, "SPY")
            assert contract.symbol in provider._streamer_symbols
            assert provider._streamer_symbols[contract.symbol] == ".SPY260220C450"

    @pytest.mark.asyncio
    async def test_skips_already_cached_underlyings(
        self, mock_session: MagicMock
    ) -> None:
        contract = _make_contract()

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
            new_callable=AsyncMock,
        ) as mock_get_chain:
            provider = TastyTradeMarketDataProvider(mock_session)
            provider._streamer_symbols["SPY  260220C00450000"] = ".SPY260220C450"

            await provider._ensure_streamer_symbols([contract])

            mock_get_chain.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolves_multiple_underlyings(
        self, mock_session: MagicMock
    ) -> None:
        spy_contract = _make_contract(
            symbol="SPY  260220C00450000", underlying="SPY"
        )
        aapl_contract = _make_contract(
            symbol="AAPL 260220C00200000", underlying="AAPL",
            strike=Decimal("200"),
        )

        spy_chain = _sdk_chain_for([
            ("SPY  260220C00450000", "SPY", ".SPY260220C450"),
        ])
        aapl_chain = _sdk_chain_for([
            ("AAPL 260220C00200000", "AAPL", ".AAPL260220C200"),
        ])

        call_count = 0

        async def fake_get_chain(session, underlying):
            nonlocal call_count
            call_count += 1
            if underlying == "SPY":
                return spy_chain
            return aapl_chain

        with patch(
            "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
            side_effect=fake_get_chain,
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            await provider._ensure_streamer_symbols([spy_contract, aapl_contract])

            assert call_count == 2
            assert provider._streamer_symbols["SPY  260220C00450000"] == ".SPY260220C450"
            assert provider._streamer_symbols["AAPL 260220C00200000"] == ".AAPL260220C200"


class TestStreamGreeksAutoResolves:
    @pytest.mark.asyncio
    async def test_stream_greeks_resolves_symbols_before_subscribing(
        self, mock_session: MagicMock
    ) -> None:
        contract = _make_contract()
        sdk_chain = _sdk_chain_for([
            ("SPY  260220C00450000", "SPY", ".SPY260220C450"),
        ])

        mock_greeks_event = MagicMock()
        mock_greeks_event.event_symbol = ".SPY260220C450"
        mock_greeks_event.delta = 0.5
        mock_greeks_event.gamma = 0.02
        mock_greeks_event.theta = -0.05
        mock_greeks_event.vega = 0.15
        mock_greeks_event.rho = 0.03
        mock_greeks_event.volatility = 0.2
        mock_greeks_event.price = 5.0

        # Async iterator that yields one event then stops
        async def mock_listen(event_type):
            yield mock_greeks_event

        mock_streamer = AsyncMock()
        mock_streamer.subscribe = AsyncMock()
        mock_streamer.listen = mock_listen
        mock_streamer.__aenter__ = AsyncMock(return_value=mock_streamer)
        mock_streamer.__aexit__ = AsyncMock(return_value=False)

        with (
            patch(
                "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
                new_callable=AsyncMock,
                return_value=sdk_chain,
            ) as mock_get_chain,
            patch(
                "options_analyzer.adapters.tastytrade.market_data.DXLinkStreamer",
                return_value=mock_streamer,
            ),
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            # Cache is empty — stream_greeks must auto-resolve
            assert provider._streamer_symbols == {}

            results = []
            async for sym, greeks in provider.stream_greeks([contract]):
                results.append((sym, greeks))
                break  # one event is enough

            # Verify get_option_chain was called to populate cache
            mock_get_chain.assert_called_once_with(mock_session.session, "SPY")
            # Verify we got the event with canonical symbol
            assert len(results) == 1
            assert results[0][0] == "SPY  260220C00450000"
            assert isinstance(results[0][1], FirstOrderGreeks)


class TestStreamGreeksAndQuotesAutoResolves:
    @pytest.mark.asyncio
    async def test_stream_greeks_and_quotes_resolves_symbols_before_subscribing(
        self, mock_session: MagicMock
    ) -> None:
        contract = _make_contract()
        sdk_chain = _sdk_chain_for([
            ("SPY  260220C00450000", "SPY", ".SPY260220C450"),
        ])

        mock_greeks = FirstOrderGreeks(
            delta=Decimal("0.5"),
            gamma=Decimal("0.02"),
            theta=Decimal("-0.05"),
            vega=Decimal("0.15"),
            rho=Decimal("0.03"),
            iv=Decimal("0.2"),
        )
        greeks_update = GreeksUpdate(
            event_symbol=".SPY260220C450", greeks=mock_greeks
        )

        async def mock_subscribe_greeks_and_quotes(greeks_syms, quote_syms):
            yield greeks_update

        mock_wrapper = MagicMock()
        mock_wrapper.subscribe_greeks_and_quotes = mock_subscribe_greeks_and_quotes

        with (
            patch(
                "options_analyzer.adapters.tastytrade.market_data.get_option_chain",
                new_callable=AsyncMock,
                return_value=sdk_chain,
            ) as mock_get_chain,
            patch(
                "options_analyzer.adapters.tastytrade.streaming.DXLinkStreamerWrapper",
                return_value=mock_wrapper,
            ),
        ):
            provider = TastyTradeMarketDataProvider(mock_session)
            assert provider._streamer_symbols == {}

            results = []
            async for update in provider.stream_greeks_and_quotes(
                [contract], ["SPY"]
            ):
                results.append(update)
                break

            mock_get_chain.assert_called_once_with(mock_session.session, "SPY")
            assert len(results) == 1
            assert isinstance(results[0], GreeksUpdate)
            # Canonical symbol should be used, not streamer symbol
            assert results[0].event_symbol == "SPY  260220C00450000"
