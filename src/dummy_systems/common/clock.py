"""Injectable clocks so dummy behaviour is deterministic in tests."""

import time
from collections.abc import Callable
from datetime import UTC, datetime

Clock = Callable[[], datetime]
Ticker = Callable[[], float]
"""Monotonic seconds; used only to measure elapsed simulation time."""


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def utc_now_ms() -> datetime:
    now = datetime.now(UTC)
    return now.replace(microsecond=now.microsecond // 1000 * 1000)


monotonic: Ticker = time.monotonic
