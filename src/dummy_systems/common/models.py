"""API model conventions shared by the dummy services: camelCase JSON and exact quantities."""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel

Unit = Literal["g", "kg"]


class ApiModel(BaseModel):
    """Base for every request/response model: snake_case in Python, camelCase on the wire."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, frozen=True)


class Quantity(ApiModel):
    """An exact quantity. Serialised as a decimal string, never a JSON number (NFR-11)."""

    value: Decimal
    unit: Unit

    @field_serializer("value")
    def _value_as_string(self, value: Decimal) -> str:
        return str(value)


class DeviceStatus(ApiModel):
    """Status of a peripheral; returned only while the device is reachable (otherwise 503)."""

    available: bool
