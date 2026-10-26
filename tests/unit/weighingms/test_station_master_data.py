"""Container assignment (TA-08) and operator directory (TA-09) from configuration."""

import pytest

from tests.conftest import STATION_CONFIG
from weighingms.config import load_station_config
from weighingms.domain.errors import OperatorNotFound

STATION = load_station_config(STATION_CONFIG)


@pytest.mark.parametrize(
    ("dyestuff", "scale_class", "container", "tare"),
    [
        ("DYE-1180", "PRECISION", "C-09", "214"),
        ("DYE-2204", "PRECISION", "C-11", "214"),
        ("DYE-4471", "PRECISION", "C-12", "214"),
        ("AUX-0101", "FLOOR", "D-03", "1.850"),
        ("AUX-0107", "FLOOR", "D-05", "1.850"),
        ("DYE-9999", "PRECISION", "C-01", "214"),
        ("AUX-9999", "FLOOR", "D-01", "1.850"),
    ],
)
def test_container_assignment_matches_the_prototype(
    dyestuff: str, scale_class: str, container: str, tare: str
) -> None:
    assigned = STATION.containers.container_for(dyestuff, scale_class)  # type: ignore[arg-type]

    assert assigned.container_id == container
    assert str(assigned.tare.value) == tare


def test_operator_directory() -> None:
    assert STATION.operators.by_id("OP-1001").name == "R. Karim"
    assert STATION.operators.by_badge("2001").role == "SUPERVISOR"
    assert STATION.default_operator_id == "OP-1001"
    with pytest.raises(OperatorNotFound):
        STATION.operators.by_badge("0000")


def test_training_mode_is_on_in_this_build() -> None:
    assert STATION.training_mode is True
