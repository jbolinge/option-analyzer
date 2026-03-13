"""Tests for Borg Transwarp V2 multi-factor allocation model."""

import numpy as np
import pytest

from options_analyzer.engine.borg_transwarp import (
    BORG_TICKERS,
    BlockResult,
    BorgTickerData,
    BorgTranswarpResult,
    compute_borg_transwarp,
    compute_borg_transwarp_series,
    prepare_borg_ticker_data,
    _block1_tlt20_psq20,
    _block7_kmlm_spy,
    _block10_kmlm_hyd,
    _block14_fdn200_xlu200,
    _check_overbought_oversold,
)


def _make_multi_ticker_closes(
    n: int = 300, seed: int = 42
) -> dict[str, np.ndarray]:
    """Create synthetic close arrays for all 20 Borg tickers."""
    rng = np.random.default_rng(seed)
    closes: dict[str, np.ndarray] = {}
    for ticker in BORG_TICKERS:
        base = rng.uniform(50, 500)
        walk = np.cumsum(rng.normal(0, 1, n))
        closes[ticker] = np.clip(base + walk, 10.0, 1000.0)
    return closes


def _make_ticker_data(**overrides: float) -> BorgTickerData:
    """Create a BorgTickerData with neutral defaults."""
    defaults = {
        "spy_close": 450.0,
        "spy_rsi10": 55.0,
        "spy_rsi21": 55.0,
        "spy_sma100": 440.0,
        "spy_sma200": 430.0,
        "ioo_rsi10": 55.0,
        "qqq_close": 380.0,
        "qqq_rsi10": 55.0,
        "qqq_sma20": 375.0,
        "qqq_sma25": 370.0,
        "qqq_pct10": 0.02,
        "qqq_pct20": 0.03,
        "qqq_pct60": 0.05,
        "qqq_return_sma10": 0.001,
        "vtv_rsi10": 55.0,
        "xlf_rsi10": 55.0,
        "xlp_rsi10": 55.0,
        "tlt_rsi20": 55.0,
        "tlt_rsi21": 55.0,
        "tlt_rsi126": 45.0,
        "shv_pct60": 0.002,
        "shv_pct63": 0.002,
        "shv_pct126": 0.004,
        "agg_rsi10": 55.0,
        "agg_rsi20": 55.0,
        "agg_rsi21": 55.0,
        "agg_pct60": 0.01,
        "ief_rsi7": 55.0,
        "ief_rsi10": 55.0,
        "psq_rsi20": 45.0,
        "psq_rsi21": 45.0,
        "sh_rsi60": 45.0,
        "bnd_pct60": 0.01,
        "vwo_close": 42.0,
        "vwo_sma63": 41.0,
        "vwo_sma126": 40.0,
        "vwo_pct60": 0.03,
        "vwo_pct63": 0.03,
        "vwo_pct126": 0.05,
        "fdn_rsi200": 55.0,
        "xlu_rsi126": 45.0,
        "xlu_rsi200": 45.0,
        "xlk_rsi10": 55.0,
        "xlk_rsi126": 55.0,
        "kmlm_close": 30.0,
        "kmlm_rsi10": 45.0,
        "kmlm_sma20": 31.0,
        "smh_rsi10": 55.0,
        "hyd_rsi10": 55.0,
    }
    defaults.update(overrides)
    return BorgTickerData(**defaults)


class TestBlockResult:
    def test_default_weight(self) -> None:
        br = BlockResult(qqq=1.0)
        assert br.weight == 1.0

    def test_custom_weight(self) -> None:
        br = BlockResult(shv=1.0, weight=0.5)
        assert br.weight == 0.5


class TestIndividualBlocks:
    def test_block1_bullish(self) -> None:
        d = _make_ticker_data(tlt_rsi20=60.0, psq_rsi20=40.0)
        assert _block1_tlt20_psq20(d).qqq == 1.0

    def test_block1_bearish(self) -> None:
        d = _make_ticker_data(tlt_rsi20=40.0, psq_rsi20=60.0)
        assert _block1_tlt20_psq20(d).shv == 1.0

    def test_block7_spy_beats_kmlm(self) -> None:
        d = _make_ticker_data(spy_rsi10=60.0, kmlm_rsi10=40.0)
        br = _block7_kmlm_spy(d)
        assert br.qqq == 1.0
        assert br.weight == 0.25

    def test_block7_kmlm_below_sma(self) -> None:
        d = _make_ticker_data(spy_rsi10=40.0, kmlm_rsi10=60.0, kmlm_close=25.0, kmlm_sma20=30.0)
        assert _block7_kmlm_spy(d).qqq == 1.0

    def test_block7_oversold_shv(self) -> None:
        d = _make_ticker_data(spy_rsi10=40.0, kmlm_rsi10=60.0, kmlm_close=35.0, kmlm_sma20=30.0, qqq_rsi10=30.0)
        assert _block7_kmlm_spy(d).shv == 1.0

    def test_block7_psq(self) -> None:
        d = _make_ticker_data(spy_rsi10=40.0, kmlm_rsi10=60.0, kmlm_close=35.0, kmlm_sma20=30.0, qqq_rsi10=50.0)
        assert _block7_kmlm_spy(d).psq == 1.0

    def test_block10_hyd_beats_kmlm(self) -> None:
        d = _make_ticker_data(hyd_rsi10=60.0, kmlm_rsi10=40.0)
        assert _block10_kmlm_hyd(d).qqq == 1.0

    def test_block10_oversold(self) -> None:
        d = _make_ticker_data(hyd_rsi10=40.0, kmlm_rsi10=60.0, qqq_rsi10=30.0)
        assert _block10_kmlm_hyd(d).shv == 1.0

    def test_block14_fdn_beats_xlu(self) -> None:
        d = _make_ticker_data(fdn_rsi200=60.0, xlu_rsi200=40.0)
        assert _block14_fdn200_xlu200(d).qqq == 1.0

    def test_block14_xlu_beats_fdn(self) -> None:
        d = _make_ticker_data(fdn_rsi200=40.0, xlu_rsi200=60.0)
        assert _block14_fdn200_xlu200(d).shv == 1.0


class TestOverboughtOversold:
    def test_overbought_spy(self) -> None:
        d = _make_ticker_data(spy_rsi10=85.0)
        ob, os_ = _check_overbought_oversold(d)
        assert ob is True
        assert os_ is False

    def test_overbought_qqq(self) -> None:
        d = _make_ticker_data(qqq_rsi10=82.0)
        ob, _ = _check_overbought_oversold(d)
        assert ob is True

    def test_overbought_xlp(self) -> None:
        d = _make_ticker_data(xlp_rsi10=78.0)
        ob, _ = _check_overbought_oversold(d)
        assert ob is True

    def test_oversold_qqq(self) -> None:
        d = _make_ticker_data(qqq_rsi10=25.0)
        ob, os_ = _check_overbought_oversold(d)
        assert ob is False
        assert os_ is True

    def test_oversold_spy(self) -> None:
        d = _make_ticker_data(spy_rsi10=25.0)
        ob, os_ = _check_overbought_oversold(d)
        assert ob is False
        assert os_ is True

    def test_neutral(self) -> None:
        d = _make_ticker_data()
        ob, os_ = _check_overbought_oversold(d)
        assert ob is False
        assert os_ is False


class TestComputeBorgTranswarp:
    def test_returns_result(self) -> None:
        d = _make_ticker_data()
        result = compute_borg_transwarp(d)
        assert isinstance(result, BorgTranswarpResult)

    def test_allocations_sum_to_one(self) -> None:
        d = _make_ticker_data()
        result = compute_borg_transwarp(d)
        total = result.psq + result.qqq + result.shv
        assert total == pytest.approx(1.0, abs=0.01)

    def test_allocations_non_negative(self) -> None:
        d = _make_ticker_data()
        result = compute_borg_transwarp(d)
        assert result.psq >= 0
        assert result.qqq >= 0
        assert result.shv >= 0

    def test_bullish_scenario_high_qqq(self) -> None:
        # Most blocks should favor QQQ when TLT > PSQ, AGG > SH, etc.
        d = _make_ticker_data(
            tlt_rsi20=70.0, psq_rsi20=30.0,
            agg_rsi20=70.0, sh_rsi60=30.0,
            bnd_pct60=0.05, shv_pct60=0.001,
            vwo_pct126=0.10, shv_pct126=0.001,
            vwo_pct63=0.05, shv_pct63=0.001,
            spy_rsi10=65.0, kmlm_rsi10=35.0,
            xlk_rsi10=65.0, smh_rsi10=65.0, hyd_rsi10=65.0,
            spy_close=450.0, spy_sma200=400.0,
            xlu_rsi126=40.0, xlk_rsi126=60.0,
            spy_sma100=420.0, qqq_close=380.0, qqq_sma25=370.0,
            fdn_rsi200=60.0, xlu_rsi200=40.0,
        )
        result = compute_borg_transwarp(d)
        assert result.qqq > 0.6

    def test_nan_data_returns_neutral(self) -> None:
        d = _make_ticker_data(spy_close=float("nan"))
        result = compute_borg_transwarp(d)
        assert result.shv == 1.0
        assert result.qqq == 0.0
        assert result.psq == 0.0

    def test_frozen_dataclass(self) -> None:
        d = _make_ticker_data()
        result = compute_borg_transwarp(d)
        with pytest.raises(AttributeError):
            result.qqq = 0.5  # type: ignore[misc]


class TestPrepareBorgTickerData:
    def test_output_length_matches_input(self) -> None:
        closes = _make_multi_ticker_closes(n=300)
        data = prepare_borg_ticker_data(closes)
        assert len(data) == 300

    def test_returns_borg_ticker_data(self) -> None:
        closes = _make_multi_ticker_closes(n=300)
        data = prepare_borg_ticker_data(closes)
        assert isinstance(data[0], BorgTickerData)

    def test_late_bars_have_valid_data(self) -> None:
        closes = _make_multi_ticker_closes(n=300)
        data = prepare_borg_ticker_data(closes)
        # Last bar should have all fields populated (past warmup)
        d = data[-1]
        import math
        assert not math.isnan(d.spy_rsi10)
        assert not math.isnan(d.qqq_rsi10)
        assert not math.isnan(d.spy_sma200)


class TestComputeBorgTranswarpSeries:
    def test_output_length(self) -> None:
        closes = _make_multi_ticker_closes(n=300)
        results = compute_borg_transwarp_series(closes)
        assert len(results) == 300

    def test_allocations_sum_to_one_for_valid_bars(self) -> None:
        closes = _make_multi_ticker_closes(n=300)
        results = compute_borg_transwarp_series(closes)
        # Check last 50 bars (should be past warmup)
        for r in results[-50:]:
            total = r.psq + r.qqq + r.shv
            assert total == pytest.approx(1.0, abs=0.01)

    def test_has_variety_of_allocations(self) -> None:
        closes = _make_multi_ticker_closes(n=300)
        results = compute_borg_transwarp_series(closes)
        valid = results[-50:]
        qqq_values = [r.qqq for r in valid]
        # With random data, should see some variation
        assert max(qqq_values) > min(qqq_values)
