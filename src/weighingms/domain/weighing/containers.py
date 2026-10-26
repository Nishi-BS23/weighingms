"""Container master data and assignment (FR-6, FR-7, TA-08)."""

from dataclasses import dataclass, field
from typing import Literal

from weighingms.domain.quantity import Quantity
from weighingms.domain.scale_selection import ScaleClass

ContainerType = Literal["BUCKET", "DRUM"]


@dataclass(frozen=True)
class Container:
    container_id: str
    container_type: ContainerType
    tare: Quantity
    dyestuff_codes: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class ContainerMaster:
    containers: dict[str, Container]
    defaults: dict[ScaleClass, str]

    def container_for(self, dyestuff_code: str, scale_class: ScaleClass) -> Container:
        """The container assigned to a dyestuff, else the default container for the scale class."""
        for container in self.containers.values():
            if dyestuff_code in container.dyestuff_codes:
                return container
        return self.containers[self.defaults[scale_class]]
