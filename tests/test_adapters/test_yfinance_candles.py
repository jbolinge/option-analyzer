"""Tests for yfinance candle fetcher."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from options_analyzer.adapters.yfinance_candles import (
    CandleSeries,
    fetch_candles_yfinance,
    map_symbol,
)


class TestSymbolMapping:
    """Tests for internal symbol -> yfinance ticker mapping."""

    def test_spx_maps_to_gspc(self) -> None:
        assert map_symbol("SPX") == "^GSPC"

    def test_dollar_spx_maps_to_gspc(self) -> None:
        assert map_symbol("$SPX") == "^GSPC"

    def test_ndx_maps_to_ndx(self) -> None:
        assert map_symbol("NDX") == "^NDX"

    def test_rut_maps_to_rut(self) -> None:
        assert map_symbol("RUT") == "^RUT"

    def test_equity_passes_through(self) -> None:
        assert map_symbol("AAPL") == "AAPL"

    def test_unknown_symbol_passes_through(self) -> None:
        assert map_symbol("TSLA") == "TSLA"


def _make_ohlcv_dataframe(n: int = 3, symbol: str = "^GSPC") -> pd.DataFrame:
    """Create a mock yfinance-style DataFrame with MultiIndex columns."""
    dates = pd.date_range("2024-06-15", periods=n, freq="D")
    data = {
        ("Open", symbol): [5500.0 + i for i in range(n)],
        ("High", symbol): [5520.0 + i for i in range(n)],
        ("Low", symbol): [5480.0 + i for i in range(n)],
        ("Close", symbol): [5510.0 + i for i in range(n)],
        ("Volume", symbol): [1_000_000 + i * 100 for i in range(n)],
    }
    df = pd.DataFrame(data, index=dates)
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=["Price", "Ticker"])
    return df


class TestDataFrameConversion:
    """Tests for DataFrame-to-CandleSeries conversion."""

    @pytest.mark.asyncio
    async def test_converts_dataframe_to_candle_series(self) -> None:
        df = _make_ohlcv_dataframe(3)
        with patch("options_analyzer.adapters.yfinance_candles.yf") as mock_yf:
            mock_yf.download.return_value = df
            result = await fetch_candles_yfinance("SPX", days_back=30)

        assert isinstance(result, CandleSeries)
        assert len(result.bars) == 3
        assert result.bars[0].symbol == "SPX"
        assert result.bars[0].open == 5500.0
        assert result.bars[0].close == 5510.0

    @pytest.mark.asyncio
    async def test_bar_timestamps_have_utc(self) -> None:
        df = _make_ohlcv_dataframe(1)
        with patch("options_analyzer.adapters.yfinance_candles.yf") as mock_yf:
            mock_yf.download.return_value = df
            result = await fetch_candles_yfinance("SPX", days_back=30)

        assert result.bars[0].timestamp.tzinfo is not None

    @pytest.mark.asyncio
    async def test_equity_symbol_preserved(self) -> None:
        df = _make_ohlcv_dataframe(2, symbol="AAPL")
        with patch("options_analyzer.adapters.yfinance_candles.yf") as mock_yf:
            mock_yf.download.return_value = df
            result = await fetch_candles_yfinance("AAPL", days_back=30)

        assert all(bar.symbol == "AAPL" for bar in result.bars)

    @pytest.mark.asyncio
    async def test_volume_int_conversion(self) -> None:
        df = _make_ohlcv_dataframe(1)
        with patch("options_analyzer.adapters.yfinance_candles.yf") as mock_yf:
            mock_yf.download.return_value = df
            result = await fetch_candles_yfinance("SPX", days_back=30)

        assert isinstance(result.bars[0].volume, int)


class TestErrorHandling:
    """Tests for error cases."""

    @pytest.mark.asyncio
    async def test_empty_dataframe_raises_value_error(self) -> None:
        with patch("options_analyzer.adapters.yfinance_candles.yf") as mock_yf:
            mock_yf.download.return_value = pd.DataFrame()
            with pytest.raises(ValueError, match="yfinance returned no data"):
                await fetch_candles_yfinance("SPX", days_back=30)

    @pytest.mark.asyncio
    async def test_none_dataframe_raises_value_error(self) -> None:
        with patch("options_analyzer.adapters.yfinance_candles.yf") as mock_yf:
            mock_yf.download.return_value = None
            with pytest.raises(ValueError, match="yfinance returned no data"):
                await fetch_candles_yfinance("SPX", days_back=30)
