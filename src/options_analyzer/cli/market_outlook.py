"""``market-outlook`` CLI — generate the daily SPX Market Conditions Dashboard.

Reproduces block 6 of ``notebooks/06_dstfs_trend_analysis.ipynb`` (the
"SPX — Market Conditions Dashboard (Daily)") as a one-shot command and saves it
as a PDF named ``{date}-daily-market-conditions.pdf``.

Usage:
    market-outlook                 # save to the configured default directory
    market-outlook -o /some/dir    # save into a directory (default filename)
    market-outlook -o out.pdf      # save to an explicit file path
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date
from pathlib import Path

from options_analyzer.api.services.market_conditions import build_dashboard_figure
from options_analyzer.config import AppConfig, find_project_root, load_config
from options_analyzer.factory import create_providers

# Default view: most recent 90 calendar days.
ZOOM_DAYS = 90

_FILENAME_TEMPLATE = "{date}-daily-market-conditions.pdf"


def _default_filename() -> str:
    """Return the report filename stamped with today's local date."""
    return _FILENAME_TEMPLATE.format(date=date.today().isoformat())


def resolve_output_path(output: str | None, config: AppConfig) -> Path:
    """Resolve the final PDF path from the CLI value and config default.

    - ``None`` → ``<config.reports.output_dir>/<today>-daily-market-conditions.pdf``
      (a relative ``output_dir`` is resolved against the project root).
    - a value ending in ``.pdf`` → used as an explicit file path.
    - any other value → treated as a directory; the default filename is appended.

    The parent directory is created if it does not exist.
    """
    if output is None:
        base = Path(config.reports.output_dir).expanduser()
        if not base.is_absolute():
            base = find_project_root() / base
        path = base / _default_filename()
    else:
        candidate = Path(output).expanduser()
        if candidate.suffix.lower() == ".pdf":
            path = candidate
        else:
            path = candidate / _default_filename()

    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="market-outlook",
        description=(
            "Generate the daily SPX Market Conditions Dashboard and save it as "
            "a PDF (default view: last 90 days)."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        default=None,
        help=(
            "Save location: a directory (default filename is used) or an "
            "explicit '.pdf' file path. Defaults to the configured reports "
            "directory."
        ),
    )
    return parser.parse_args(argv)


async def _run(config: AppConfig, output_path: Path) -> None:
    providers = await create_providers(config)
    try:
        fig = await build_dashboard_figure(
            providers.market_data, zoom_days=ZOOM_DAYS
        )
    finally:
        await providers.disconnect()

    # Static PDF export via kaleido; honors the figure's own width/height.
    fig.write_image(str(output_path), format="pdf")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config()
        output_path = resolve_output_path(args.output, config)
        asyncio.run(_run(config, output_path))
    except Exception as exc:  # noqa: BLE001 — surface a clean message to the user
        print(f"market-outlook: error: {exc}", file=sys.stderr)
        return 1

    print(f"Saved {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
