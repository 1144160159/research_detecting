from __future__ import annotations

import json
from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_pug_execution_protocol import create_protocol


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DESIGN_PATH = (
    PROJECT_ROOT / "results/strict_v4_pug_design_v1/design_protocol.json"
)


def test_execution_protocol_preserves_frozen_design() -> None:
    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    protocol = create_protocol(
        design,
        DESIGN_PATH,
        Path("results/strict_v4_pug_design_v1/design_protocol.json"),
        {"train_hybrid_open_set.py": "a" * 64},
    )

    assert protocol["manifest_sha256"] == canonical_hash(protocol)
    assert len(protocol["tasks"]) == 18
    assert protocol["pilot_scope"]["seeds"] == [283, 293, 307]
    assert protocol["execution"]["pseudo_unknown_max_alpha"] == 0.5
    assert protocol["execution"]["pseudo_unknown_min_fold_gain"] == -0.05
    assert protocol["claim_boundary"][
        "isolated_seed997_smoke_is_implementation_evidence_only"
    ] is True


def test_execution_protocol_rejects_design_gate_drift() -> None:
    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    design["training_time_selection"]["gate"][
        "mean_unknown_fpr95_oriented_improvement_minimum"
    ] = 0.0

    with pytest.raises(ValueError, match="canonical zero-result PUG design"):
        create_protocol(
            design,
            DESIGN_PATH,
            Path("results/strict_v4_pug_design_v1/design_protocol.json"),
            {"train_hybrid_open_set.py": "a" * 64},
        )
