from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit_strict_v4_ronetc_full102_protocol import audit_protocol
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


def evidence(tmp_path: Path) -> tuple[Path, Path, Path]:
    summary = tmp_path / "summary.json"
    coverage = tmp_path / "coverage.json"
    baseline = tmp_path / "baseline.json"
    summary.write_text('{"summary": true}\n', encoding="utf-8")
    coverage.write_text('{"coverage": true}\n', encoding="utf-8")
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


def write_protocol(
    tmp_path: Path,
    root: Path,
    summary: Path,
    coverage: Path,
    baseline: Path,
) -> Path:
    protocol = build_protocol(
        root, summary, coverage, baseline, tmp_path / "runs"
    )
    path = tmp_path / "protocol.json"
    path.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def test_audit_accepts_exact_zero_result_protocol(tmp_path):
    root = source_tree(tmp_path)
    summary, coverage, baseline = evidence(tmp_path)
    protocol = write_protocol(
        tmp_path, root, summary, coverage, baseline
    )

    audit = audit_protocol(
        protocol, root, summary, coverage, baseline
    )

    assert audit["passed"] is True
    assert all(audit["checks"].values())
    assert audit["artifact_counts"] == {
        "metrics.json": 0,
        "scores.npz": 0,
        "provenance.json": 0,
    }


def test_audit_rejects_manifest_tamper(tmp_path):
    root = source_tree(tmp_path)
    summary, coverage, baseline = evidence(tmp_path)
    protocol = write_protocol(
        tmp_path, root, summary, coverage, baseline
    )
    payload = json.loads(protocol.read_text(encoding="utf-8"))
    payload["universe"]["task_count"] = 101
    protocol.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    audit = audit_protocol(
        protocol, root, summary, coverage, baseline
    )

    assert audit["passed"] is False
    assert audit["checks"]["manifest_matches"] is False
    assert audit["checks"]["universe_exact"] is False
