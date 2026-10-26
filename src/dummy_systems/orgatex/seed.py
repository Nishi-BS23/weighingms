"""Load and validate the Dummy OrgaTEX seed file (reference data, never modified at runtime)."""

from dataclasses import dataclass
from pathlib import Path

from dummy_systems.common.models import ApiModel
from dummy_systems.orgatex.models import Batch, Recipe


class _SeedBatch(Batch):
    recipe: Recipe


class _SeedFile(ApiModel):
    note: str
    batches: list[_SeedBatch]


@dataclass(frozen=True)
class OrgatexSeed:
    batches: dict[str, Batch]
    recipes: dict[str, Recipe]


class SeedError(ValueError):
    """The seed file is inconsistent."""


def load_seed(path: Path) -> OrgatexSeed:
    raw = _SeedFile.model_validate_json(path.read_bytes())
    batches: dict[str, Batch] = {}
    recipes: dict[str, Recipe] = {}
    for entry in raw.batches:
        recipe = entry.recipe
        if recipe.batch_id != entry.batch_id or recipe.recipe_id != entry.recipe_id:
            raise SeedError(f"{entry.batch_id}: recipe does not belong to the batch")
        if entry.component_count != len(recipe.components):
            raise SeedError(f"{entry.batch_id}: componentCount does not match the recipe")
        sequences = [c.sequence for c in recipe.components]
        if sequences != list(range(1, len(sequences) + 1)):
            raise SeedError(f"{entry.batch_id}: component sequence must be 1..n")
        batches[entry.batch_id] = Batch.model_validate(entry.model_dump(exclude={"recipe"}))
        recipes[entry.batch_id] = recipe
    return OrgatexSeed(batches=batches, recipes=recipes)
