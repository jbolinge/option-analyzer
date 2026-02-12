"""Tests for Bloomberg dark theme."""

import plotly.graph_objects as go

from options_analyzer.visualization.theme import (
    BLOOMBERG_TEMPLATE,
    COLOR_CYCLE,
    GRID_COLOR,
    LINE_WIDTH,
    MARKER_SIZE,
    MARKER_SYMBOL,
    OVERLAY_DASH,
    PALETTE,
    REFERENCE_DASH,
    REFERENCE_LINE_WIDTH,
    SURFACE_COLORSCALE,
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


class TestStyleConstants:
    """Tests for styling constants consolidated in theme.py."""

    def test_line_width_is_positive_int(self) -> None:
        assert isinstance(LINE_WIDTH, int)
        assert LINE_WIDTH > 0

    def test_reference_line_width_is_positive_int(self) -> None:
        assert isinstance(REFERENCE_LINE_WIDTH, int)
        assert REFERENCE_LINE_WIDTH > 0

    def test_reference_line_thinner_than_trace(self) -> None:
        assert REFERENCE_LINE_WIDTH < LINE_WIDTH

    def test_reference_dash_is_string(self) -> None:
        assert REFERENCE_DASH == "dash"

    def test_overlay_dash_is_string(self) -> None:
        assert OVERLAY_DASH == "dot"

    def test_marker_size_is_positive_int(self) -> None:
        assert isinstance(MARKER_SIZE, int)
        assert MARKER_SIZE > 0

    def test_marker_symbol_is_string(self) -> None:
        assert isinstance(MARKER_SYMBOL, str)
        assert MARKER_SYMBOL == "diamond"

    def test_surface_colorscale_is_string(self) -> None:
        assert isinstance(SURFACE_COLORSCALE, str)
        assert SURFACE_COLORSCALE == "Plasma"

    def test_grid_color_is_hex(self) -> None:
        assert isinstance(GRID_COLOR, str)
        assert GRID_COLOR.startswith("#")
        assert len(GRID_COLOR) == 7

    def test_grid_color_matches_template_xaxis(self) -> None:
        assert GRID_COLOR == BLOOMBERG_TEMPLATE.layout.xaxis.gridcolor  # type: ignore[union-attr]

    def test_color_cycle_is_list(self) -> None:
        assert isinstance(COLOR_CYCLE, list)
        assert len(COLOR_CYCLE) == 6

    def test_color_cycle_matches_palette_order(self) -> None:
        expected = [
            PALETTE["primary"],
            PALETTE["secondary"],
            PALETTE["tertiary"],
            PALETTE["positive"],
            PALETTE["negative"],
            PALETTE["neutral"],
        ]
        assert COLOR_CYCLE == expected

    def test_color_cycle_matches_template_colorway(self) -> None:
        colorway = list(BLOOMBERG_TEMPLATE.layout.colorway)  # type: ignore[union-attr]
        assert COLOR_CYCLE == colorway
