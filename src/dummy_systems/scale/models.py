"""Dummy Scale training contract models."""

from datetime import date, datetime
from typing import Literal

from dummy_systems.common.models import ApiModel, Quantity

ScaleClass = Literal["PRECISION", "FLOOR"]
SimulationProfile = Literal["dispense", "overshoot", "below", "exact"]


class ScaleInfo(ApiModel):
    scale_id: str
    scale_class: ScaleClass
    label: str
    capacity: Quantity
    resolution: Quantity
    available: bool
    calibration_due: date


class ScaleStatus(ApiModel):
    scale_id: str
    available: bool
    calibration_due: date
    calibration_valid: bool
    simulating: bool


class ScaleReading(ApiModel):
    scale_id: str
    gross: Quantity
    tare: Quantity
    net: Quantity
    stable: bool
    read_at: datetime


class SimulationRequest(ApiModel):
    profile: SimulationProfile
    net: Quantity
    """Landing net weight (ramp profiles) or the exact net weight (`exact`)."""


class LoadRequest(ApiModel):
    gross: Quantity
    """Total load now on the scale, e.g. an empty container (tare is unchanged)."""


class CalibrationUpdate(ApiModel):
    calibration_due: date
