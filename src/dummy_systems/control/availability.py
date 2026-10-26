"""Failure injection: each external system can be switched unavailable (HTTP 503)."""

import threading
from collections.abc import Callable

from dummy_systems.common.errors import ApiError

SYSTEMS = ("orgatex", "scale-3kg", "scale-32kg", "scanner", "printer")


class Availability:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state = dict.fromkeys(SYSTEMS, True)

    def snapshot(self) -> dict[str, bool]:
        with self._lock:
            return dict(self._state)

    def is_available(self, system: str) -> bool:
        with self._lock:
            return self._state[system]

    def set(self, system: str, available: bool) -> None:
        if system not in SYSTEMS:
            raise ApiError(404, "SYSTEM_NOT_FOUND", f"Unknown system {system}.")
        with self._lock:
            self._state[system] = available

    def reset(self) -> None:
        with self._lock:
            self._state = dict.fromkeys(SYSTEMS, True)

    def ensure(self, system: str) -> None:
        if not self.is_available(system):
            raise ApiError(
                503,
                "SYSTEM_UNAVAILABLE",
                f"{system} is unavailable (training failure injection).",
                {"system": system},
            )

    def dependency(self, system: str) -> Callable[[], None]:
        """A FastAPI dependency that fails with 503 while `system` is unavailable."""

        def _check() -> None:
            self.ensure(system)

        return _check
