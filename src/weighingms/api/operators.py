"""Operator identification endpoints (FR-19)."""

from fastapi import APIRouter, Depends
from pydantic import Field

from weighingms.api.container import Container, get_container
from weighingms.api.schemas import ApiModel
from weighingms.domain.operators import Operator

router = APIRouter(prefix="/api/operators", tags=["Operators"])


class OperatorOut(ApiModel):
    operator_id: str
    name: str
    shift: str
    role: str

    @classmethod
    def of(cls, operator: Operator) -> "OperatorOut":
        return cls(
            operator_id=operator.operator_id,
            name=operator.name,
            shift=operator.shift,
            role=operator.role,
        )


class SignInIn(ApiModel):
    badge_id: str = Field(min_length=1, max_length=32)


@router.get("/current", response_model=OperatorOut)
def current(container: Container = Depends(get_container)) -> OperatorOut:
    return OperatorOut.of(container.operators.current())


@router.post("/sign-in", response_model=OperatorOut)
def sign_in(body: SignInIn, container: Container = Depends(get_container)) -> OperatorOut:
    return OperatorOut.of(container.operators.sign_in(body.badge_id.strip()))
