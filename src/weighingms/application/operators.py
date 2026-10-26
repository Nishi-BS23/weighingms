"""The station's current operator (FR-19, TA-09)."""

import logging

from weighingms.application.ports import AuditStore, StateStore
from weighingms.clock import Clock, utc_now
from weighingms.domain.operators import Operator, OperatorDirectory

log = logging.getLogger("weighingms.operators")

CURRENT_OPERATOR_KEY = "current_operator_id"


class OperatorService:
    def __init__(
        self,
        directory: OperatorDirectory,
        state: StateStore,
        audit: AuditStore,
        default_operator_id: str,
        clock: Clock = utc_now,
    ) -> None:
        self._directory = directory
        self._state = state
        self._audit = audit
        self._default = default_operator_id
        self._clock = clock

    def current(self) -> Operator:
        return self._directory.by_id(self._state.get(CURRENT_OPERATOR_KEY) or self._default)

    def sign_in(self, badge_id: str) -> Operator:
        operator = self._directory.by_badge(badge_id)
        previous = self.current()
        if operator.operator_id != previous.operator_id:
            self._state.set(CURRENT_OPERATOR_KEY, operator.operator_id)
            self._audit.add(
                "OPERATOR_CHANGE",
                operator.operator_id,
                self._clock(),
                detail={"from": previous.operator_id, "to": operator.operator_id},
            )
            log.info("Operator changed: %s -> %s", previous.operator_id, operator.operator_id)
        return operator

    def supervisor_for_pin(self, pin: str) -> Operator | None:
        return self._directory.supervisor_for_pin(pin)

    def reset(self) -> None:
        """Training reset: back to the default operator."""
        self._state.clear()
