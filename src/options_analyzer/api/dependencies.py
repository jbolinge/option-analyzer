"""Shared FastAPI dependencies — provider lifecycle and injection."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import cast

from fastapi import FastAPI, Request

from options_analyzer.config.loader import load_config
from options_analyzer.config.schema import AppConfig
from options_analyzer.factory import ProviderContext, create_providers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan: connect providers on startup, disconnect on shutdown."""
    config = load_config()
    ctx = await create_providers(config)
    app.state.config = config
    app.state.providers = ctx
    yield
    await ctx.disconnect()


def get_providers(request: Request) -> ProviderContext:
    """FastAPI dependency — returns the shared ProviderContext."""
    return cast(ProviderContext, request.app.state.providers)


def get_config(request: Request) -> AppConfig:
    """FastAPI dependency — returns the application config."""
    return cast(AppConfig, request.app.state.config)
