"""Dummy OrgaTEX endpoints — the workbook's training contract, not the real OrgaTEX interface."""

from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter

from dummy_systems.common.clock import Clock
from dummy_systems.common.errors import ApiError
from dummy_systems.orgatex.models import (
    Batch,
    BatchList,
    BatchStatus,
    ConsumptionPosting,
    ConsumptionReceipt,
    Recipe,
    StatusUpdate,
    StoredConsumption,
)
from dummy_systems.orgatex.seed import OrgatexSeed
from dummy_systems.orgatex.store import OrgatexStore


def build_router(
    seed: OrgatexSeed, store: OrgatexStore, clock: Clock, dependencies: Sequence[Any] = ()
) -> APIRouter:
    router = APIRouter(
        prefix="/api/batches",
        tags=["Dummy OrgaTEX (training contract)"],
        dependencies=list(dependencies),
    )

    def current(batch_id: str) -> Batch:
        batch = seed.batches.get(batch_id)
        if batch is None:
            raise ApiError(404, "BATCH_NOT_FOUND", f"Batch {batch_id} does not exist.")
        status = store.status_overrides().get(batch_id, batch.status)
        return batch.model_copy(update={"status": status})

    @router.get("", response_model=BatchList)
    def list_batches(status: BatchStatus | None = None) -> BatchList:
        batches = [current(batch_id) for batch_id in seed.batches]
        if status is not None:
            batches = [b for b in batches if b.status == status]
        return BatchList(generated_at=clock(), batches=batches)

    @router.get("/{batch_id}", response_model=Batch)
    def get_batch(batch_id: str) -> Batch:
        return current(batch_id)

    @router.get("/{batch_id}/recipe", response_model=Recipe)
    def get_recipe(batch_id: str) -> Recipe:
        current(batch_id)
        return seed.recipes[batch_id]

    @router.post("/{batch_id}/consumption", response_model=ConsumptionReceipt)
    def post_consumption(batch_id: str, posting: ConsumptionPosting) -> ConsumptionReceipt:
        current(batch_id)
        return store.record_consumption(batch_id, posting, clock())

    @router.get("/{batch_id}/consumption", response_model=list[StoredConsumption])
    def list_consumption(batch_id: str) -> list[StoredConsumption]:
        current(batch_id)
        return store.consumptions(batch_id)

    @router.patch("/{batch_id}/status", response_model=Batch)
    def set_status(batch_id: str, update: StatusUpdate) -> Batch:
        current(batch_id)
        store.set_status(batch_id, update.status, clock())
        return current(batch_id)

    return router
