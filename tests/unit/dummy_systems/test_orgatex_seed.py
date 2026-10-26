"""Seed loader consistency checks."""

import json
from pathlib import Path
from typing import Any

import pytest

from dummy_systems.app import DEFAULT_SEED_PATH
from dummy_systems.orgatex.seed import SeedError, load_seed


def _write_seed(tmp_path: Path, mutate: Any) -> Path:
    data = json.loads(DEFAULT_SEED_PATH.read_text())
    mutate(data["batches"][0])
    path = tmp_path / "seed.json"
    path.write_text(json.dumps(data))
    return path


def test_real_seed_loads() -> None:
    seed = load_seed(DEFAULT_SEED_PATH)

    assert list(seed.batches) == ["B-24187", "B-24188", "B-24190", "B-24191"]
    assert len(seed.recipes["B-24187"].components) == 5


def test_component_count_mismatch_is_rejected(tmp_path: Path) -> None:
    path = _write_seed(tmp_path, lambda b: b.update(componentCount=6))

    with pytest.raises(SeedError, match="componentCount"):
        load_seed(path)


def test_recipe_of_another_batch_is_rejected(tmp_path: Path) -> None:
    path = _write_seed(tmp_path, lambda b: b["recipe"].update(batchId="B-99999"))

    with pytest.raises(SeedError, match="does not belong"):
        load_seed(path)


def test_broken_sequence_is_rejected(tmp_path: Path) -> None:
    path = _write_seed(tmp_path, lambda b: b["recipe"]["components"][0].update(sequence=9))

    with pytest.raises(SeedError, match="sequence"):
        load_seed(path)
