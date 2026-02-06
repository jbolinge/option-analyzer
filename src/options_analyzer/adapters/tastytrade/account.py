"""TastyTrade account provider — implements AccountProvider port."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tastytrade import Account
from tastytrade.instruments import get_option_chain

from options_analyzer.adapters.tastytrade.mapping import map_position_to_leg
from options_analyzer.domain.models import Leg
from options_analyzer.ports.account import AccountProvider

if TYPE_CHECKING:
    from options_analyzer.adapters.tastytrade.session import TastyTradeSession


class TastyTradeAccountProvider(AccountProvider):
    """Accesses accounts and positions via TastyTrade."""

    def __init__(self, session: TastyTradeSession) -> None:
        self._session = session

    async def get_accounts(self) -> list[str]:
        accounts = await Account.get(self._session.session)
        if not isinstance(accounts, list):
            return [accounts.account_number]
        return [a.account_number for a in accounts]

    async def get_positions(
        self, account_id: str, underlying: str | None = None
    ) -> list[Leg]:
        account = await Account.get(self._session.session, account_id)
        if isinstance(account, list):
            account = account[0]

        kwargs: dict[str, object] = {"session": self._session.session}
        if underlying:
            kwargs["underlying_symbols"] = [underlying]

        positions = await account.get_positions(**kwargs)  # type: ignore[arg-type]
        if not positions:
            return []

        # Build lookup of option symbols to SDK option objects
        underlyings = {p.underlying_symbol for p in positions}
        option_lookup: dict[str, object] = {}
        for sym in underlyings:
            chain = await get_option_chain(self._session.session, sym)
            for options in chain.values():
                for opt in options:
                    option_lookup[opt.symbol] = opt

        legs: list[Leg] = []
        for pos in positions:
            sdk_option = option_lookup.get(pos.symbol)
            if sdk_option:
                legs.append(map_position_to_leg(pos, sdk_option))
        return legs
