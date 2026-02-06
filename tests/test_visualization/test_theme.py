"""Tests for Bloomberg dark theme."""

import plotly.graph_objects as go

from options_analyzer.visualization.theme import (
    BLOOMBERG_TEMPLATE,
    PALETTE,
    apply_theme,
)


class TestPalette:
    """Tests for PALETTE color constants."""

    def test_has_primary_color(self) -> None:
        assert PALETTE["primary"] == "#ff6600"

    def test_has_secondary_color(self) -> None:
        assert PALETTE["secondary"] == "#00cccc"

    def test_has_tertiary_color(self) -> None:
        assert PALETTE["tertiary"] == "#cc00cc"

    def test_has_positive_color(self) -> None:
        assert PALETTE["positive"] == "#00cc66"

    def test_has_negative_color(self) -> None:
        assert PALETTE["negative"] == "#cc3333"

    def test_has_neutral_color(self) -> None:
        assert PALETTE["neutral"] == "#888888"


class TestBloombergTemplate:
    """Tests for BLOOMBERG_TEMPLATE plotly template."""

    def test_paper_bgcolor(self) -> None:
        assert BLOOMBERG_TEMPLATE.layout.paper_bgcolor == "#000000"  # type: ignore[union-attr]

    def test_plot_bgcolor(self) -> None:
        assert BLOOMBERG_TEMPLATE.layout.plot_bgcolor == "#1a1a2e"  # type: ignore[union-attr]

    def test_font_family_is_monospace(self) -> None:
        font = BLOOMBERG_TEMPLATE.layout.font  # type: ignore[union-attr]
        assert "Consolas" in font.family
        assert "monospace" in font.family

    def test_font_color(self) -> None:
        assert BLOOMBERG_TEMPLATE.layout.font.color == "#e0e0e0"  # type: ignore[union-attr]

    def test_xaxis_gridcolor(self) -> None:
        assert BLOOMBERG_TEMPLATE.layout.xaxis.gridcolor == "#2d2d44"  # type: ignore[union-attr]

    def test_yaxis_gridcolor(self) -> None:
        assert BLOOMBERG_TEMPLATE.layout.yaxis.gridcolor == "#2d2d44"  # type: ignore[union-attr]

    def test_title_font_size(self) -> None:
        assert BLOOMBERG_TEMPLATE.layout.title.font.size == 16  # type: ignore[union-attr]


class TestApplyTheme:
    """Tests for apply_theme function."""

    def test_applies_template_to_figure(self) -> None:
        fig = go.Figure()
        result = apply_theme(fig)
        assert result.layout.template == BLOOMBERG_TEMPLATE

    def test_returns_figure_for_chaining(self) -> None:
        fig = go.Figure()
        result = apply_theme(fig)
        assert result is fig

    def test_applies_to_figure_with_data(self) -> None:
        fig = go.Figure(data=[go.Scatter(x=[1, 2], y=[3, 4])])
        result = apply_theme(fig)
        assert result.layout.template == BLOOMBERG_TEMPLATE
        assert len(result.data) == 1
