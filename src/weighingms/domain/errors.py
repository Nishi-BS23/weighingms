"""Domain and integration errors with stable codes; the API maps them to the standard error body."""

from typing import Any


class DomainError(Exception):
    """A business-rule violation or integration failure with a stable `code`."""

    status_code = 400
    code = "DOMAIN_ERROR"

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFound(DomainError):
    status_code = 404


class Conflict(DomainError):
    status_code = 409


class BatchNotFound(NotFound):
    code = "BATCH_NOT_FOUND"


class DependencyUnavailable(DomainError):
    status_code = 503


class BatchNotSelectable(Conflict):
    code = "BATCH_NOT_SELECTABLE"


class SessionNotFound(NotFound):
    code = "SESSION_NOT_FOUND"


class ComponentNotFound(NotFound):
    code = "COMPONENT_NOT_FOUND"


class ComponentAlreadyDone(Conflict):
    code = "COMPONENT_ALREADY_DONE"


class SessionCompleted(Conflict):
    code = "SESSION_COMPLETED"


class NoActiveComponent(Conflict):
    code = "NO_ACTIVE_COMPONENT"


class OperatorNotFound(NotFound):
    code = "OPERATOR_NOT_FOUND"


class OutOfTolerance(Conflict):
    code = "OUT_OF_TOLERANCE"


class ScaleCalibrationExpired(Conflict):
    code = "SCALE_CALIBRATION_EXPIRED"


class OverrideNotAuthorised(DomainError):
    status_code = 403
    code = "OVERRIDE_NOT_AUTHORISED"


class OverrideNotNeeded(Conflict):
    code = "OVERRIDE_NOT_NEEDED"


class BatchIncomplete(Conflict):
    code = "BATCH_INCOMPLETE"


class SessionNotCompleted(Conflict):
    code = "SESSION_NOT_COMPLETED"
