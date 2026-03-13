"""yfinance-based candle fetcher — fallback when DXLink streaming fails."""

from __future__ import annotations

import asyncio
import logging
import threading
from datetime import UTC, datetime, timedelta

import yfinance as yf  # type: ignore[import-untyped]

from options_analyzer.domain.candles import CandleBar, CandleSeries

logger = logging.getLogger(__name__)

# yfinance is not thread-safe — concurrent yf.download() calls corrupt shared
# internal state, causing wrong data or DataFrame structure errors.
_YF_LOCK = threading.Lock()

# Map internal symbols to yfinance tickers
_SYMBOL_MAP: dict[str, str] = {
    "SPX": "^GSPC",
    "$SPX": "^GSPC",
    "NDX": "^NDX",
    "$NDX": "^NDX",
    "RUT": "^RUT",
    "$RUT": "^RUT",
    "DJX": "^DJI",
    "$DJX": "^DJI",
    "VIX": "^VIX",
    "$VIX": "^VIX",
    "VIX3M": "^VIX3M",
    "$VIX3M": "^VIX3M",
}

# Map our interval strings to yfinance intervals
_INTERVAL_MAP: dict[str, str] = {
    "1d": "1d",
    "1w": "1wk",
    "1m": "1mo",
    "1h": "1h",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
}


def map_symbol(symbol: str) -> str:
    """Map an internal symbol to a yfinance ticker."""
    return _SYMBOL_MAP.get(symbol, symbol)


def _download_sync(
    ticker: str, interval: str, start: datetime, end: datetime
) -> list[CandleBar]:
    """Synchronous yfinance download — run in executor."""
    yf_interval = _INTERVAL_MAP.get(interval, interval)
    with _YF_LOCK:
        df = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            interval=yf_interval,
            progress=False,
            auto_adjust=True,
        )
    if df is None or df.empty:
        return []

    # Strip ticker level from MultiIndex columns if present
    if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
        df.columns = df.columns.droplevel("Ticker")

    bars: list[CandleBar] = []
    # Reverse-map back to our internal symbol
    reverse = {v: k for k, v in _SYMBOL_MAP.items() if not k.startswith("$")}
    bar_symbol = reverse.get(ticker, ticker)

    for ts, row in df.iterrows():
        bars.append(
            CandleBar(
                symbol=bar_symbol,
                timestamp=ts.to_pydatetime().replace(tzinfo=UTC),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]) if row["Volume"] else 0,
            )
        )
    return bars


async def fetch_candles_yfinance(
    symbol: str,
    interval: str = "1d",
    days_back: int = 365,
) -> CandleSeries:
    """Fetch historical candle data via yfinance.

    Runs the synchronous yfinance download in a thread executor.
    Raises ValueError if no data is returned.
    """
    ticker = map_symbol(symbol)
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=days_back)

    logger.info(
        "Fetching candles from yfinance: %s (%s), %s, %d days",
        symbol, ticker, interval, days_back,
    )

    loop = asyncio.get_running_loop()
    bars = await loop.run_in_executor(
        None, _download_sync, ticker, interval, start, end,
    )

    if not bars:
        raise ValueError(
            f"yfinance returned no data for {ticker} (symbol={symbol}, "
            f"interval={interval}, days_back={days_back})"
        )

    logger.info("yfinance returned %d bars for %s", len(bars), symbol)
    return CandleSeries(bars=bars)
