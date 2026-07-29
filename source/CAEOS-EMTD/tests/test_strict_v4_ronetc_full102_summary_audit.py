from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit_strict_v4_ronetc_full102 import audit, completion
from summarize_strict_v4_ronetc_full102 import (
    build_summary,
    canonical_hash,
    file_hash,
)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def metric_payload(method: str, suite: str, scenario: str, index: int) -> dict:
    is_candidate = method == "ronetc"
    report = {
        "known_macro_f1": 0.75 + index / 10000,
        "unknown_auroc": 0.72 if is_candidate else 0.70,
        "unknown_aupr": 0.68 if is_candidate else 0.65,
        "unknown_fpr95": 0.25 if is_candidate else 0.30,
        "oscr": 0.66 if is_candidate else 0.62,
    }
    return {
        "model": method,
        "method": method,
        "unknown_classes": [f"Attack{index}"],
        "seed": 7,
        "sample_counts": {"Benign": 20, f"Attack{index}": 10},
        "split_metadata": {
            "split_fingerprint": {"combined": f"split-{index}"}
        },
        "reports": {method: report},
        "selection_evidence": {
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "arguments": {"suite": suite, "scenario": scenario},
    }


def build_fixture(tmp_path: Path) -> dict[str, Path]:
    project_root = tmp_path / "project"
    project_root.mkdir()
    for name in (
        "summarize_strict_v4_ronetc_full102.py",
        "audit_strict_v4_ronetc_full102.py",
    ):
        (project_root / name).write_text(f"# {name}\n", encoding="utf-8")
    result_root = tmp_path / "ronetc"
    opendetect_root = tmp_path / "opendetect"
    tasks = []
    suites = [f"suite_{index}" for index in range(7)]
    for index in range(102):
        suite = suites[index % len(suites)]
        scenario = f"scenario_{index:03d}"
        tasks.append(
            {
                "suite": suite,
                "scenario": scenario,
                "unknown_classes": f"Attack{index}",
                "model": "ronetc",
                "seed": 7,
                "output_dir": str(
                    result_root / suite / f"{scenario}_seed7_ronetc"
                ),
                "required_artifacts": [
                    "metrics.json",
                    "scores.npz",
                    "provenance.json",
                ],
            }
        )
        for method, root in (
            ("ronetc", result_root),
            ("opendetect", opendetect_root),
        ):
            directory = root / suite / f"{scenario}_seed7_{method}"
            write_json(
                directory / "metrics.json",
                metric_payload(method, suite, scenario, index),
            )
            (directory / "scores.npz").write_bytes(
                f"{method}-{index}".encode("ascii")
            )
            write_json(
                directory / "provenance.json",
                {
                    "schema_version": 1,
                    "task": {
                        "suite": suite,
                        "scenario": scenario,
                        "unknown_classes": f"Attack{index}",
                        "model": method,
                        "seed": 7,
                    },
                },
            )
    full_summary_path = tmp_path / "full_summary.json"
    baseline_manifest_path = tmp_path / "baseline_manifest.json"
    baseline_manifest = {
        "schema_version": "strict_v4_baseline_manifest_v2",
        "scenario_inference_units": 102,
        "seed": 7,
        "reported_methods": ["opendetect"],
    }
    baseline_manifest["manifest_sha256"] = canonical_hash(baseline_manifest)
    write_json(baseline_manifest_path, baseline_manifest)
    full_summary = {
        "schema_version": "strict_v4_full103_coverage_summary_v1",
        "baseline_manifest_sha256": baseline_manifest["manifest_sha256"],
        "validation": {
            "passes": True,
            "scenario_count": 102,
        },
    }
    write_json(full_summary_path, full_summary)
    protocol_path = tmp_path / "protocol.json"
    protocol = {
        "schema_version": "strict_v4_ronetc_full102_protocol_v1",
        "state": "frozen_zero_result",
        "source_evidence_sha256": {
            "strict_v4_full102_summary": file_hash(full_summary_path),
            "strict_v4_baseline_manifest_v2": file_hash(
                baseline_manifest_path
            ),
        },
        "tasks": tasks,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    write_json(protocol_path, protocol)
    protocol_audit_path = tmp_path / "protocol_audit.json"
    protocol_audit = {
        "schema_version": "strict_v4_ronetc_full102_protocol_audit_v1",
        "passed": True,
        "checks": {"manifest_matches": True, "universe_exact": True},
    }
    protocol_audit["audit_manifest_sha256"] = canonical_hash(
        protocol_audit, "audit_manifest_sha256"
    )
    write_json(protocol_audit_path, protocol_audit)
    return {
        "project_root": project_root,
        "result_root": result_root,
        "opendetect_root": opendetect_root,
        "protocol": protocol_path,
        "protocol_audit": protocol_audit_path,
        "baseline_manifest": baseline_manifest_path,
        "full_summary": full_summary_path,
    }


def test_full102_summary_and_independent_audit_complete(tmp_path):
    paths = build_fixture(tmp_path)
    summary = build_summary(
        paths["protocol"],
        paths["protocol_audit"],
        paths["result_root"],
        paths["opendetect_root"],
        paths["baseline_manifest"],
        paths["full_summary"],
        paths["project_root"],
    )
    summary_path = tmp_path / "summary.json"
    write_json(summary_path, summary)

    result = audit(
        paths["protocol"],
        paths["protocol_audit"],
        summary_path,
        paths["result_root"],
        paths["opendetect_root"],
        paths["baseline_manifest"],
        paths["full_summary"],
        paths["project_root"],
    )

    assert summary["validation"]["scenario_count"] == 102
    assert len(summary["by_suite"]) == 7
    assert summary["claim_boundary"]["authorizes_comprehensive_sota"] is False
    assert result["passes"] is True
    audit_path = tmp_path / "audit.json"
    write_json(audit_path, result)
    marker = completion(paths["protocol"], summary_path, audit_path, result)
    assert marker["state"] == "complete"
    assert marker["authorizes_comprehensive_sota"] is False


def test_audit_rejects_raw_metric_tamper_after_summary(tmp_path):
    paths = build_fixture(tmp_path)
    summary = build_summary(
        paths["protocol"],
        paths["protocol_audit"],
        paths["result_root"],
        paths["opendetect_root"],
        paths["baseline_manifest"],
        paths["full_summary"],
        paths["project_root"],
    )
    summary_path = tmp_path / "summary.json"
    write_json(summary_path, summary)
    metrics_path = (
        paths["result_root"]
        / "suite_0/scenario_000_seed7_ronetc/metrics.json"
    )
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metrics["reports"]["ronetc"]["unknown_auroc"] = 0.99
    write_json(metrics_path, metrics)

    result = audit(
        paths["protocol"],
        paths["protocol_audit"],
        summary_path,
        paths["result_root"],
        paths["opendetect_root"],
        paths["baseline_manifest"],
        paths["full_summary"],
        paths["project_root"],
    )

    assert result["passes"] is False
    assert result["checks"]["raw_artifact_and_task_integrity"] is False
