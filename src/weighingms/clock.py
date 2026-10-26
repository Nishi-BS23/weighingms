"""Injectable clocks for WeighingMS (tests replace them)."""

import time
from collections.abc import Callable
from datetime import UTC, datetime

Clock = Callable[[], datetime]
Ticker = Callable[[], float]


def utc_now() -> datetime:
    return datetime.now(UTC)


monotonic: Ticker = time.monotonic
