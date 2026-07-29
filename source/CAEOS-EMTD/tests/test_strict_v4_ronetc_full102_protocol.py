import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from create_strict_v4_ronetc_full102_protocol import (
    CACHE_ARGUMENTS,
    build_protocol,
    canonical_hash,
    file_hash,
)


def source_tree(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "caeos").mkdir(parents=True)
    for name in (
        "create_strict_v4_ronetc_full102_protocol.py",
        "run_neural_baseline_matrix.py",
        "train_neural_open_set.py",
        "caeos/ronetc.py",
        "summarize_strict_v4_ronetc_full102.py",
        "audit_strict_v4_ronetc_full102.py",
    ):
        path = root / name
        path.write_text(f"# {name}\n", encoding="utf-8")
    return root


def evidence(tmp_path: Path):
    summary = tmp_path / "summary.json"
    coverage = tmp_path / "coverage.json"
    baseline = tmp_path / "baseline.json"
    summary.write_text(json.dumps({"scenarios": 102}), encoding="utf-8")
    coverage.write_text(json.dumps({"scenarios": 102}), encoding="utf-8")
    cache_artifacts = {}
    for suite in CACHE_ARGUMENTS:
        path = tmp_path / "caches" / suite / "seed7.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{suite}\n", encoding="utf-8")
        sidecar = Path(f"{path}.json")
        sidecar.write_text("{}\n", encoding="utf-8")
        cache_artifacts[suite] = {
            "path": str(path),
            "sha256": file_hash(path),
            "sidecar_sha256": file_hash(sidecar),
        }
    baseline_value = {
        "schema_version": "strict_v4_baseline_manifest_v2",
        "seed": 7,
        "scenario_inference_units": 102,
        "cache_artifacts": cache_artifacts,
    }
    baseline_value["manifest_sha256"] = canonical_hash(baseline_value)
    baseline.write_text(json.dumps(baseline_value), encoding="utf-8")
    return summary, coverage, baseline


def test_protocol_freezes_exact_primary102_and_claim_boundary(tmp_path):
    root = source_tree(tmp_path)
    summary, coverage, baseline = evidence(tmp_path)
    protocol = build_protocol(
        root, summary, coverage, baseline, tmp_path / "runs"
    )

    assert protocol["universe"]["scenario_count"] == 102
    assert protocol["universe"]["suite_count"] == 7
    assert len(protocol["tasks"]) == 102
    assert {task["model"] for task in protocol["tasks"]} == {"ronetc"}
    assert {task["seed"] for task in protocol["tasks"]} == {7}
    assert protocol["baseline_scope"]["primary_domain_nearest"] == [
        "opendetect",
        "ronetc",
    ]
    assert (
        protocol["claim_boundary"]["authorizes_comprehensive_sota_before_execution"]
        is False
    )
    assert protocol["formal_output_counts_at_freeze"]["metrics"] == 0
    assert (
        protocol["paired_input_contract"][
            "postselection_corruption_cache_is_not_used"
        ]
        is True
    )


def test_protocol_refuses_existing_result_artifact(tmp_path):
    root = source_tree(tmp_path)
    summary, coverage, baseline = evidence(tmp_path)
    result = tmp_path / "runs/nf_unsw/analysis_seed7_ronetc/metrics.json"
    result.parent.mkdir(parents=True)
    result.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="before results exist"):
        build_protocol(
            root, summary, coverage, baseline, tmp_path / "runs"
        )
