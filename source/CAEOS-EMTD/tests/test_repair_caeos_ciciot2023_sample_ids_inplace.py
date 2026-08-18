from __future__ import annotations

import hashlib
from pathlib import Path

from repair_caeos_ciciot2023_sample_ids_inplace import (
    apply_fixed_width_patches,
    hash_with_substitutions,
)


def test_hash_substitution_matches_inplace_result(tmp_path: Path) -> None:
    path = tmp_path / "class.csv"
    old_id = "11" * 32
    new_id = "22" * 32
    value = ("prefix," + old_id + ",suffix\n").encode("ascii")
    path.write_bytes(value)
    offset = value.index(old_id.encode("ascii"))
    patch = {
        "old_sample_id": old_id,
        "new_sample_id": new_id,
        "final_sample_offset": offset,
    }

    old_sha256, predicted_sha256 = hash_with_substitutions(
        path, [patch], tmp_path / "progress.json"
    )
    assert old_sha256 == hashlib.sha256(value).hexdigest()

    apply_fixed_width_patches(path, [patch], "final_sample_offset")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == predicted_sha256
    assert path.stat().st_size == len(value)


def test_fixed_width_patch_rolls_forward_exactly(tmp_path: Path) -> None:
    path = tmp_path / "part.csv"
    first = "aa" * 32
    second = "bb" * 32
    path.write_bytes((first + "\n").encode("ascii"))
    patch = {
        "old_sample_id": first,
        "new_sample_id": second,
        "part_sample_offset": 0,
    }

    apply_fixed_width_patches(path, [patch], "part_sample_offset")

    assert path.read_bytes() == (second + "\n").encode("ascii")
