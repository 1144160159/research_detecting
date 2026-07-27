from __future__ import annotations

from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_pug_cross_suite_design import (
    SEEDS,
    create_design,
    formal_output_counts,
    load,
)


ROOT = Path(__file__).resolve().parents[1]
PUG_DESIGN = (
    ROOT / "results/strict_v4_pug_design_v1/design_protocol.json"
)
PUG_PROTOCOL = (
    ROOT
    / "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
)
KRC_PROTOCOL = (
    ROOT / "results/strict_v4_krc_csr_confirmation_v1/protocol.json"
)


def build(result_root: Path) -> dict:
    return create_design(
        pug_design=load(PUG_DESIGN),
        pug_protocol=load(PUG_PROTOCOL),
        krc_protocol=load(KRC_PROTOCOL),
        input_file_sha256={
            "pug_design": "a" * 64,
            "pug_execution_protocol": "b" * 64,
            "krc_protocol": "c" * 64,
        },
        implementation_sha256={
            "create_strict_v4_pug_cross_suite_design.py": "d" * 64
        },
        observed_output_counts=formal_output_counts(result_root),
    )


def test_design_freezes_full102_three_seed_universe(tmp_path: Path) -> None:
    design = build(tmp_path / "formal")
    universe = design["confirmation_universe"]
    tasks = universe["tasks"]

    assert design["manifest_sha256"] == canonical_hash(design)
    assert universe["suite_count"] == 7
    assert universe["scenario_count"] == 102
    assert universe["fresh_seeds"] == SEEDS
    assert len(tasks) == 306
    assert len(
        {(row["suite"], row["scenario"], row["seed"]) for row in tasks}
    ) == 306
    assert set(row["seed"] for row in tasks) == set(SEEDS)
    assert design["execution_admitted_at_freeze"] is False
    assert not any(design["formal_result_counts_at_freeze"].values())
    assert (
        design["admission_gate"]["route_coverage"][
            "pug_selected_suite_count_minimum"
        ]
        == 4
    )


def test_design_rejects_existing_formal_outputs(tmp_path: Path) -> None:
    result = tmp_path / "formal"
    result.mkdir()
    (result / "activation.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="outputs must be zero"):
        build(result)


def test_design_rejects_pilot_boundary_drift(tmp_path: Path) -> None:
    pug_design = load(PUG_DESIGN)
    pug_design["fresh_pilot"]["seeds"] = [1, 2, 3]
    with pytest.raises(ValueError, match="pilot design boundary"):
        create_design(
            pug_design=pug_design,
            pug_protocol=load(PUG_PROTOCOL),
            krc_protocol=load(KRC_PROTOCOL),
            input_file_sha256={},
            implementation_sha256={},
            observed_output_counts=formal_output_counts(tmp_path / "formal"),
        )
