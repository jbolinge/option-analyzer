"""Provider factory — creates port implementations from config."""

from __future__ import annotations

from dataclasses import dataclass

from options_analyzer.config.schema import AppConfig
from options_analyzer.ports.account import AccountProvider
from options_analyzer.ports.market_data import MarketDataProvider


@dataclass
class ProviderContext:
    """Container for all provider instances needed by the presentation layer."""

    market_data: MarketDataProvider
    account: AccountProvider
    provider_name: str

    async def disconnect(self) -> None:
        """Disconnect all providers."""
        await self.market_data.disconnect()


async def create_providers(config: AppConfig) -> ProviderContext:
    """Create and connect provider implementations based on config.

    Currently supports:
        - "tastytrade": TastyTrade paper/live via OAuth

    Raises ValueError for unknown provider names.
    """
    name = config.provider.name.lower()

    if name == "tastytrade":
        from options_analyzer.adapters.tastytrade.account import (
            TastyTradeAccountProvider,
        )
        from options_analyzer.adapters.tastytrade.market_data import (
            TastyTradeMarketDataProvider,
        )
        from options_analyzer.adapters.tastytrade.session import TastyTradeSession

        session = TastyTradeSession(config.provider)
        await session.connect()
        return ProviderContext(
            market_data=TastyTradeMarketDataProvider(session),
            account=TastyTradeAccountProvider(session),
            provider_name=(
                f"TastyTrade ({'paper' if config.provider.is_paper else 'live'})"
            ),
        )

    raise ValueError(f"Unknown provider: {name!r}. Supported: 'tastytrade'")
