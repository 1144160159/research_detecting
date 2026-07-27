from pathlib import Path

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_evidence_reuse_design import create_design


def canonical(schema):
    value = {"schema_version": schema}
    value["manifest_sha256"] = canonical_hash(value)
    return value


def values(tmp_path: Path, observed=0):
    implementation = {
        "create_strict_v4_mdr_evidence_reuse_design.py": "a",
        "caeos/mdr_evidence_reuse_runtime.py": "b",
        "caeos/mdr_runtime.py": "c",
        "caeos/mdr_fusion.py": "d",
        "caeos/pairwise_runtime.py": "e",
        "caeos/hybrid_open_set.py": "f",
        "tests/test_mdr_evidence_reuse_runtime.py": "g",
    }
    return create_design(
        project_root=tmp_path,
        mdr_design=canonical("strict_v4_mdr_caeos_design_v2"),
        selected_system_design=canonical(
            "strict_v4_mdr_selected_system_design_v1"
        ),
        opendetect_efficiency_design=canonical(
            "strict_v4_mdr_opendetect_efficiency_design_v1"
        ),
        input_file_sha256={"inputs": "hash"},
        implementation_sha256=implementation,
        observed_outputs=observed,
    )


def test_design_freezes_exact_five_to_two_pass_optimization(tmp_path):
    design = values(tmp_path)
    assert (
        design["optimization"]["original_model_evidence_passes_per_batch"][
            "total"
        ]
        == 5
    )
    assert (
        design["optimization"]["optimized_model_evidence_passes_per_batch"][
            "total"
        ]
        == 2
    )
    assert design["formal_equivalence"]["condition_count"] == 1836
    assert design["manifest_sha256"] == canonical_hash(design)


def test_design_rejects_existing_outputs(tmp_path):
    with pytest.raises(ValueError, match="zero formal outputs"):
        values(tmp_path, observed=1)
