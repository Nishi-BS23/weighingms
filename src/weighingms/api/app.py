"""WeighingMS API (port 8000).

Run with: `uvicorn weighingms.api.app:create_app --factory --port 8000`
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from weighingms.api import batches, devices, operators, sessions, tickets, training
from weighingms.api.container import Container, build_container
from weighingms.api.errors import install_error_handlers
from weighingms.api.middleware import install_request_logging
from weighingms.config import load_settings
from weighingms.logging_setup import configure_logging


def create_app(container: Container | None = None) -> FastAPI:
    configure_logging()
    container = container or build_container(load_settings())

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        container.close()

    app = FastAPI(
        title="WeighingMS API",
        description="Assisted dyestuff weighing station — the API used by the operator terminal.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.container = container
    install_error_handlers(app)
    install_request_logging(app)
    app.include_router(batches.router)
    app.include_router(devices.router)
    app.include_router(operators.router)
    app.include_router(sessions.router)
    app.include_router(sessions.records_router)
    app.include_router(tickets.router)
    if container.settings.station.training_mode:
        logging.getLogger("weighingms").warning(
            "Training mode is ON: /api/training/* is enabled (never on a real station, ADR-003)"
        )
        app.include_router(training.router)

    @app.get("/api/health", tags=["Health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "weighingms"}

    return app
