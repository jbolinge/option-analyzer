"""FastAPI application factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from options_analyzer.api.routers.health import router as health_router
from options_analyzer.api.routers.market_conditions import (
    router as market_conditions_router,
)

# Frontend build output — relative to project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_FRONTEND_DIST = _PROJECT_ROOT / "frontend" / "dist"


def create_app(
    *,
    lifespan: Any | None = None,
    cors_origins: list[str] | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application.

    Args:
        lifespan: Optional lifespan context manager. Pass None for tests
                  (providers can be injected via dependency overrides).
        cors_origins: Allowed CORS origins. Defaults to Vite dev server.
    """
    if cors_origins is None:
        cors_origins = ["http://localhost:5173"]

    app = FastAPI(
        title="options-analyzer",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes (must be registered before SPA catch-all)
    app.include_router(health_router, prefix="/api")
    app.include_router(market_conditions_router, prefix="/api")

    # Serve built SPA static files if available
    _mount_spa(app)

    return app


def _mount_spa(app: FastAPI) -> None:
    """Mount the frontend SPA if the dist directory exists.

    Serves static assets from frontend/dist/assets/ and falls back
    to index.html for all other paths (client-side routing).
    """
    if not _FRONTEND_DIST.exists():
        return

    assets_dir = _FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    index_html = _FRONTEND_DIST / "index.html"

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve static files or fall back to index.html for SPA routing."""
        file_path = _FRONTEND_DIST / full_path
        if file_path.exists() and file_path.is_file() and ".." not in full_path:
            return FileResponse(str(file_path))
        return FileResponse(str(index_html))


def create_production_app() -> FastAPI:
    """Create app with full lifespan (provider connection/disconnection)."""
    from options_analyzer.api.dependencies import lifespan

    return create_app(lifespan=lifespan)


# Default app instance for `uvicorn options_analyzer.api.app:app`
app = create_production_app()
