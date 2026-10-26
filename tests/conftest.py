"""Shared fixtures.

- The training-substitutes (dummy) app runs in-process with fixed clocks and a fake ticker.
- WeighingMS talks to it through its real HTTP adapters: Starlette's `TestClient` is an
  `httpx.Client`, so it can be handed to the adapters as their HTTP client.
"""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dummy_systems.app import DEFAULT_SEED_PATH
from dummy_systems.app import create_app as create_dummy_app
from weighingms.api.app import create_app as create_wms_app
from weighingms.api.container import Container, build_container
from weighingms.config import REPO_ROOT, Settings, load_station_config
from weighingms.infrastructure.orgatex.http_adapter import HttpOrgatexAdapter

FIXED_NOW = datetime(2026, 10, 26, 7, 47, 3, tzinfo=UTC)
STATION_CONFIG = REPO_ROOT / "config" / "station.toml"


class MutableClock:
    """A wall clock that tests can move forward."""

    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += timedelta(seconds=seconds)


class FakeTicker:
    """Monotonic time that only moves when a test advances it."""

    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def ticker() -> FakeTicker:
    return FakeTicker()


@pytest.fixture
def dummy_app(tmp_path: Path, ticker: FakeTicker) -> FastAPI:
    return create_dummy_app(
        db_path=tmp_path / "dummy.db",
        seed_path=DEFAULT_SEED_PATH,
        clock=lambda: FIXED_NOW,
        reading_clock=lambda: FIXED_NOW,
        ticker=ticker,
    )


@pytest.fixture
def dummy_client(dummy_app: FastAPI) -> Iterator[TestClient]:
    with TestClient(dummy_app) as client:
        yield client


@pytest.fixture
def orgatex_adapter(dummy_client: TestClient) -> HttpOrgatexAdapter:
    return HttpOrgatexAdapter(dummy_client)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        orgatex_base_url="http://testserver",
        devices_base_url="http://testserver",
        db_path=tmp_path / "weighingms.db",
        station=load_station_config(STATION_CONFIG),
    )


@pytest.fixture
def wms_clock() -> MutableClock:
    return MutableClock(FIXED_NOW)


@pytest.fixture
def container(
    settings: Settings, dummy_client: TestClient, wms_clock: "MutableClock"
) -> Iterator[Container]:
    built = build_container(
        settings, orgatex_client=dummy_client, devices_client=dummy_client, clock=wms_clock
    )
    yield built
    built.close()


@pytest.fixture
def wms_client(container: Container) -> Iterator[TestClient]:
    with TestClient(create_wms_app(container)) as client:
        yield client


def set_available(dummy_client: TestClient, system: str, available: bool) -> None:
    response = dummy_client.put(
        f"/api/control/availability/{system}", json={"available": available}
    )
    assert response.status_code == 200
