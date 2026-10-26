"""Operators at the station (FR-19, TA-09). Training directory comes from configuration."""

import hashlib
import hmac
from dataclasses import dataclass
from typing import Literal

from weighingms.domain.errors import OperatorNotFound

Role = Literal["OPERATOR", "SUPERVISOR"]


@dataclass(frozen=True)
class Operator:
    operator_id: str
    name: str
    shift: str
    badge_id: str
    role: Role
    pin_hash: str | None = None


@dataclass(frozen=True)
class OperatorDirectory:
    operators: dict[str, Operator]

    def by_id(self, operator_id: str) -> Operator:
        operator = self.operators.get(operator_id)
        if operator is None:
            raise OperatorNotFound(f"Operator {operator_id} is not known at this station.")
        return operator

    def supervisor_for_pin(self, pin: str) -> Operator | None:
        """The supervisor whose PIN matches, or None. PINs are never stored or logged in clear."""
        for operator in self.operators.values():
            if (
                operator.role == "SUPERVISOR"
                and operator.pin_hash
                and verify_pin(operator.pin_hash, pin)
            ):
                return operator
        return None

    def by_badge(self, badge_id: str) -> Operator:
        for operator in self.operators.values():
            if operator.badge_id == badge_id:
                return operator
        raise OperatorNotFound(f"Badge {badge_id} is not registered at this station.")


def verify_pin(pin_hash: str, pin: str) -> bool:
    """Check a PIN against `pbkdf2_sha256$<iterations>$<salt hex>$<digest hex>` in constant time."""
    try:
        algorithm, iterations, salt, digest = pin_hash.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(salt), int(iterations))
    return hmac.compare_digest(candidate.hex(), digest)
