"""Tests for the ``market-outlook`` CLI."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest

from options_analyzer.cli import market_outlook
from options_analyzer.config.schema import AppConfig, ProviderConfig, ReportConfig


def _make_config(output_dir: str) -> AppConfig:
    return AppConfig(
        provider=ProviderConfig(
            client_secret="secret",  # type: ignore[arg-type]
            refresh_token="token",  # type: ignore[arg-type]
        ),
        reports=ReportConfig(output_dir=output_dir),
    )


def _expected_name() -> str:
    return f"{date.today().isoformat()}-daily-market-conditions.pdf"


class TestResolveOutputPath:
    def test_default_uses_config_dir_and_dated_filename(self, tmp_path: Path) -> None:
        config = _make_config(str(tmp_path / "reports"))
        path = market_outlook.resolve_output_path(None, config)
        assert path == tmp_path / "reports" / _expected_name()
        assert path.parent.is_dir()  # created

    def test_directory_argument_appends_default_filename(self, tmp_path: Path) -> None:
        config = _make_config(str(tmp_path / "unused"))
        target = tmp_path / "out"
        path = market_outlook.resolve_output_path(str(target), config)
        assert path == target / _expected_name()
        assert path.parent.is_dir()

    def test_pdf_argument_used_verbatim(self, tmp_path: Path) -> None:
        config = _make_config(str(tmp_path / "unused"))
        target = tmp_path / "nested" / "custom.pdf"
        path = market_outlook.resolve_output_path(str(target), config)
        assert path == target
        assert path.parent.is_dir()

    def test_pdf_suffix_is_case_insensitive(self, tmp_path: Path) -> None:
        config = _make_config(str(tmp_path / "unused"))
        target = tmp_path / "REPORT.PDF"
        path = market_outlook.resolve_output_path(str(target), config)
        assert path == target


class _FakeFigure:
    def __init__(self) -> None:
        self.write_calls: list[tuple[str, str]] = []

    def write_image(self, path: str, format: str) -> None:  # noqa: A002
        self.write_calls.append((path, format))
        Path(path).write_bytes(b"%PDF-1.4 fake")


class _FakeProviders:
    def __init__(self) -> None:
        self.market_data = object()
        self.disconnected = False

    async def disconnect(self) -> None:
        self.disconnected = True


class TestMain:
    def test_main_wires_args_to_pdf_export(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = _make_config(str(tmp_path / "reports"))
        fake_fig = _FakeFigure()
        fake_providers = _FakeProviders()
        captured: dict[str, Any] = {}

        async def fake_create_providers(cfg: AppConfig) -> _FakeProviders:
            captured["config"] = cfg
            return fake_providers

        async def fake_build(market_data: Any, zoom_days: int | None) -> _FakeFigure:
            captured["market_data"] = market_data
            captured["zoom_days"] = zoom_days
            return fake_fig

        monkeypatch.setattr(market_outlook, "load_config", lambda: config)
        monkeypatch.setattr(market_outlook, "create_providers", fake_create_providers)
        monkeypatch.setattr(market_outlook, "build_dashboard_figure", fake_build)

        target = tmp_path / "out"
        rc = market_outlook.main(["-o", str(target)])

        assert rc == 0
        expected = target / _expected_name()
        assert fake_fig.write_calls == [(str(expected), "pdf")]
        assert expected.exists()
        assert captured["zoom_days"] == market_outlook.ZOOM_DAYS
        assert captured["market_data"] is fake_providers.market_data
        assert fake_providers.disconnected is True

    def test_main_returns_error_code_on_failure(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        def boom() -> AppConfig:
            raise RuntimeError("no credentials")

        monkeypatch.setattr(market_outlook, "load_config", boom)

        rc = market_outlook.main([])

        assert rc == 1
        assert "no credentials" in capsys.readouterr().err

    def test_disconnects_even_when_render_fails(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = _make_config(str(tmp_path / "reports"))
        fake_providers = _FakeProviders()

        async def fake_create_providers(cfg: AppConfig) -> _FakeProviders:
            return fake_providers

        async def fake_build(market_data: Any, zoom_days: int | None) -> Any:
            raise RuntimeError("fetch failed")

        monkeypatch.setattr(market_outlook, "load_config", lambda: config)
        monkeypatch.setattr(market_outlook, "create_providers", fake_create_providers)
        monkeypatch.setattr(market_outlook, "build_dashboard_figure", fake_build)

        rc = market_outlook.main([])

        assert rc == 1
        assert fake_providers.disconnected is True
