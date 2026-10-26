"""Batch endpoints used by Screen 1 and the recipe rail (FR-1, FR-3, FR-4)."""

from fastapi import APIRouter, Depends

from weighingms.api.container import Container, get_container
from weighingms.api.schemas import BatchOut, BatchQueueOut, RecipeOut

router = APIRouter(prefix="/api/batches", tags=["Batches"])


@router.get("", response_model=BatchQueueOut)
def list_batches(container: Container = Depends(get_container)) -> BatchQueueOut:
    queue, batches = container.batches.queue()
    return BatchQueueOut(received_at=queue.received_at, batches=[BatchOut.of(b) for b in batches])


@router.get("/{batch_id}", response_model=BatchOut)
def get_batch(batch_id: str, container: Container = Depends(get_container)) -> BatchOut:
    return BatchOut.of(container.batches.batch(batch_id))


@router.get("/{batch_id}/recipe", response_model=RecipeOut)
def get_recipe(batch_id: str, container: Container = Depends(get_container)) -> RecipeOut:
    return RecipeOut.of(container.batches.recipe(batch_id))
