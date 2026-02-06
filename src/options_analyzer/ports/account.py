"""AccountProvider port — abstract interface for account and position access."""

from abc import ABC, abstractmethod

from options_analyzer.domain.models import Leg


class AccountProvider(ABC):
    """Abstract interface for accessing brokerage accounts and positions."""

    @abstractmethod
    async def get_accounts(self) -> list[str]: ...

    @abstractmethod
    async def get_positions(
        self, account_id: str, underlying: str | None = None
    ) -> list[Leg]: ...
