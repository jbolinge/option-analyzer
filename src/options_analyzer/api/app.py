"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from options_analyzer.api.routers.health import router as health_router
from options_analyzer.api.routers.market_conditions import (
    router as market_conditions_router,
)


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

    app.include_router(health_router, prefix="/api")
    app.include_router(market_conditions_router, prefix="/api")

    return app


def create_production_app() -> FastAPI:
    """Create app with full lifespan (provider connection/disconnection)."""
    from options_analyzer.api.dependencies import lifespan

    return create_app(lifespan=lifespan)


# Default app instance for `uvicorn options_analyzer.api.app:app`
app = create_production_app()
