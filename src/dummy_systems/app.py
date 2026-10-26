"""Training substitutes service (port 8100).

Run with: `uvicorn dummy_systems.app:create_app --factory --port 8100`
"""

import os
from pathlib import Path

from fastapi import Depends, FastAPI

from dummy_systems.common.clock import Clock, Ticker, monotonic, utc_now, utc_now_ms
from dummy_systems.common.db import sqlite_engine
from dummy_systems.common.errors import install_error_handlers
from dummy_systems.control.availability import Availability
from dummy_systems.control.routes import build_router as control_router
from dummy_systems.orgatex.routes import build_router as orgatex_router
from dummy_systems.orgatex.seed import load_seed
from dummy_systems.orgatex.store import OrgatexStore
from dummy_systems.printer.routes import build_router as printer_router
from dummy_systems.printer.store import PrinterStore
from dummy_systems.scale.bank import ScaleBank
from dummy_systems.scale.routes import build_router as scale_router
from dummy_systems.scanner.queue import ScanQueue
from dummy_systems.scanner.routes import build_router as scanner_router

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "data" / "dummy.db"
DEFAULT_SEED_PATH = REPO_ROOT / "data" / "seed" / "orgatex-seed.json"

DESCRIPTION = (
    "Training substitutes for OrgaTEX, the weighing scales, the barcode scanner and the ticket "
    "printer. These are **training contracts only** — they make no claim about the real OrgaTEX "
    "interface or real device protocols."
)


def create_app(
    db_path: Path | None = None,
    seed_path: Path | None = None,
    clock: Clock = utc_now,
    reading_clock: Clock = utc_now_ms,
    ticker: Ticker = monotonic,
) -> FastAPI:
    db_path = db_path or Path(os.environ.get("DUMMY_DB_PATH", DEFAULT_DB_PATH))
    seed_path = seed_path or Path(os.environ.get("DUMMY_SEED_PATH", DEFAULT_SEED_PATH))

    app = FastAPI(title="WeighingMS Training Substitutes", description=DESCRIPTION, version="0.1.0")
    install_error_handlers(app)

    engine = sqlite_engine(db_path)
    seed = load_seed(seed_path)
    availability = Availability()
    orgatex_store = OrgatexStore(engine)
    printer_store = PrinterStore(engine)
    scales = ScaleBank(clock=reading_clock, ticker=ticker)
    scans = ScanQueue(clock=clock)

    def reset_all() -> None:
        orgatex_store.reset()
        printer_store.reset()
        scales.reset()
        scans.reset()
        availability.reset()

    app.include_router(
        orgatex_router(
            seed, orgatex_store, clock, dependencies=[Depends(availability.dependency("orgatex"))]
        )
    )
    app.include_router(scale_router(scales, availability))
    app.include_router(scanner_router(scans, availability))
    app.include_router(printer_router(printer_store, availability, clock))
    app.include_router(control_router(availability, scales, reset_all))

    @app.get("/health", tags=["Health"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "training-substitutes"}

    return app
