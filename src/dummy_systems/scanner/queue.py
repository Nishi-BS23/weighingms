"""Dummy Scanner: an ordered, in-memory queue of simulated scans."""

import threading
from datetime import datetime

from pydantic import Field

from dummy_systems.common.clock import Clock
from dummy_systems.common.models import ApiModel


class ScanRequest(ApiModel):
    code: str = Field(min_length=1, max_length=64)


class Scan(ApiModel):
    seq: int
    code: str
    scanned_at: datetime


class ScanBatch(ApiModel):
    scans: list[Scan]
    last_seq: int


class ScanQueue:
    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._scans: list[Scan] = []

    def add(self, code: str) -> Scan:
        with self._lock:
            scan = Scan(seq=len(self._scans) + 1, code=code.strip(), scanned_at=self._clock())
            self._scans.append(scan)
            return scan

    def after(self, seq: int) -> ScanBatch:
        with self._lock:
            return ScanBatch(
                scans=[s for s in self._scans if s.seq > seq], last_seq=len(self._scans)
            )

    def reset(self) -> None:
        with self._lock:
            self._scans = []
