"""Settings: environment variables for wiring, `config/station.toml` for business configuration."""

import os
import tomllib
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import cast
from zoneinfo import ZoneInfo

from weighingms.domain.operators import Operator, OperatorDirectory, Role
from weighingms.domain.quantity import Quantity, Unit
from weighingms.domain.scale_selection import ScaleClass, ScaleDefinition, ScaleSelectionPolicy
from weighingms.domain.tolerance import DefaultToleranceRule
from weighingms.domain.weighing.containers import Container, ContainerMaster, ContainerType

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class StationConfig:
    station_id: str
    station_name: str
    language: str
    selectable_statuses: tuple[str, ...]
    scales: dict[str, ScaleDefinition]
    scale_policy: ScaleSelectionPolicy
    default_tolerance: DefaultToleranceRule
    containers: ContainerMaster
    operators: OperatorDirectory
    default_operator_id: str
    training_mode: bool
    timezone: ZoneInfo
    ticket_header: str
    short_names: dict[str, str] = field(default_factory=dict)

    def short_name(self, name: str) -> str:
        return self.short_names.get(name, name)


@dataclass(frozen=True)
class Settings:
    orgatex_base_url: str
    devices_base_url: str
    db_path: Path
    station: StationConfig


def _quantity(raw: dict[str, str]) -> Quantity:
    return Quantity(Decimal(raw["value"]), cast(Unit, raw["unit"]))


def load_station_config(path: Path) -> StationConfig:
    data = tomllib.loads(path.read_text())
    scales = {
        s["id"]: ScaleDefinition(
            scale_id=s["id"],
            scale_class=cast(ScaleClass, s["class"]),
            label=s["label"],
            strip_label=s["strip_label"],
        )
        for s in data["scales"]
    }
    selection = data["scale_selection"]
    tolerance = data["tolerance_default"]
    containers = {
        c["id"]: Container(
            container_id=c["id"],
            container_type=cast(ContainerType, c["type"]),
            tare=_quantity(c["tare"]),
            dyestuff_codes=frozenset(c.get("dyestuffs", [])),
        )
        for c in data["containers"]
    }
    operators = {
        o["id"]: Operator(
            operator_id=o["id"],
            name=o["name"],
            shift=o["shift"],
            badge_id=o["badge"],
            role=cast(Role, o["role"]),
            pin_hash=o.get("pin_hash"),
        )
        for o in data["operators"]
    }
    return StationConfig(
        station_id=data["station"]["id"],
        station_name=data["station"]["name"],
        language=data["station"]["language"],
        selectable_statuses=tuple(data["batches"]["selectable_statuses"]),
        scales=scales,
        scale_policy=ScaleSelectionPolicy(
            threshold=_quantity(selection["threshold"]),
            precision=scales[selection["precision_scale"]],
            floor=scales[selection["floor_scale"]],
        ),
        default_tolerance=DefaultToleranceRule(
            percent=Decimal(tolerance["percent"]),
            min_precision=_quantity(tolerance["min_precision"]),
            min_floor=_quantity(tolerance["min_floor"]),
        ),
        containers=ContainerMaster(
            containers=containers,
            defaults={cast(ScaleClass, k): v for k, v in data["container_defaults"].items()},
        ),
        operators=OperatorDirectory(operators),
        default_operator_id=data["station"]["default_operator"],
        training_mode=bool(data["station"].get("training_mode", False)),
        timezone=ZoneInfo(data["station"].get("timezone", "UTC")),
        ticket_header=data["ticket"]["header"],
        short_names=dict(data.get("short_names", {})),
    )


def load_settings() -> Settings:
    config_path = Path(os.environ.get("WEIGHINGMS_CONFIG", REPO_ROOT / "config" / "station.toml"))
    return Settings(
        orgatex_base_url=os.environ.get("ORGATEX_BASE_URL", "http://127.0.0.1:8100"),
        devices_base_url=os.environ.get("DEVICES_BASE_URL", "http://127.0.0.1:8100"),
        db_path=Path(os.environ.get("WEIGHINGMS_DB_PATH", REPO_ROOT / "data" / "weighingms.db")),
        station=load_station_config(config_path),
    )
