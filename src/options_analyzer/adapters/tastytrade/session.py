"""TastyTrade session lifecycle management."""

from __future__ import annotations

from types import TracebackType

from tastytrade import Session as ProductionSession

from options_analyzer.config.schema import ProviderConfig


class TastyTradeSession:
    """Manages authentication and session lifecycle for the TastyTrade API.

    Uses ProviderConfig.is_paper to toggle between paper (is_test=True)
    and live (is_test=False) environments.
    """

    def __init__(self, config: ProviderConfig) -> None:
        self._config = config
        self._session: ProductionSession | None = None

    @property
    def session(self) -> ProductionSession:
        """Access the underlying tastytrade Session. Raises if not connected."""
        if self._session is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._session

    async def connect(self) -> None:
        """Authenticate and create a session."""
        self._session = ProductionSession(
            self._config.username.get_secret_value(),
            self._config.password.get_secret_value(),
            is_test=self._config.is_paper,
        )

    async def disconnect(self) -> None:
        """Close the session cleanly."""
        if self._session is not None:
            await self._session._client.aclose()
            self._session = None

    async def __aenter__(self) -> TastyTradeSession:
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.disconnect()
