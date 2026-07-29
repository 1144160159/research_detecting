import hashlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from summarize_krc_cross_suite_diagnostic import build_summary, render_markdown


def write_json(path: Path, payload: dict) -> str:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(tmp_path: Path):
    progress = {
        "schema_version": "strict_v4_krc_csr_confirmation_progress_audit_v1",
        "manifest_sha256": "1" * 64,
        "observed_totals": {"captures": 4, "evaluations": 24},
    }
    progress_path = tmp_path / "progress.json"
    progress_hash = write_json(progress_path, progress)
    records = [
        {
            "suite": "suite_a",
            "scenario": "one",
            "training_seed": seed,
            "known_class_count": 32,
            "calibration_known_macro_f1": value,
            "calibration_error_detection_auroc": auroc,
            "source_safety_active_count": 0,
            "source_safety_active_rate": 0.0,
            "source_safety_active_rate_upper_95pct": 0.01,
        }
        for seed, value, auroc in (
            (7, 0.6, 0.69),
            (19, 0.7, 0.71),
            (31, 0.8, 0.72),
        )
    ]
    records.append(
        {
            "suite": "suite_b",
            "scenario": "two",
            "training_seed": 7,
            "known_class_count": 8,
            "calibration_known_macro_f1": 0.95,
            "calibration_error_detection_auroc": 0.91,
            "source_safety_active_count": 1,
            "source_safety_active_rate": 0.02,
            "source_safety_active_rate_upper_95pct": 0.03,
        }
    )
    audit = {
        "schema_version": "strict_v4_krc_certificate_bottleneck_audit_v1",
        "passes": True,
        "manifest_sha256": "2" * 64,
        "progress_manifest_sha256": progress["manifest_sha256"],
        "progress_file_sha256": progress_hash,
        "records": records,
        "diagnostics": {
            "scenario_records": [
                {
                    "identity": "suite_a/one",
                    "complete_three_seed_scenario": True,
                    "all_source_safety_checks_pass": True,
                    "rrc_diagnostic_eligible": True,
                },
                {
                    "identity": "suite_b/two",
                    "complete_three_seed_scenario": False,
                    "all_source_safety_checks_pass": False,
                    "rrc_diagnostic_eligible": False,
                },
            ]
        },
    }
    audit_path = tmp_path / "audit.json"
    write_json(audit_path, audit)
    return audit, progress, audit_path, progress_path


def test_build_summary_separates_suites_and_preserves_claim_boundary(tmp_path):
    audit, progress, audit_path, progress_path = inputs(tmp_path)
    result = build_summary(audit, progress, audit_path, progress_path)

    assert result["suite_summaries"]["suite_a"][
        "complete_three_seed_scenario_count"
    ] == 1
    assert result["suite_summaries"]["suite_a"][
        "rrc_diagnostic_eligible_complete_scenario_count"
    ] == 1
    assert result["suite_summaries"]["suite_b"]["calibration_known_macro_f1"][
        "passes_absolute_threshold_count"
    ] == 1
    assert result["claim_boundary"]["authorizes_algorithm_selection"] is False
    assert result["claim_boundary"]["authorizes_gate_changes"] is False
    assert "suite_a" in render_markdown(result)


def test_rejects_progress_file_drift(tmp_path):
    audit, progress, audit_path, progress_path = inputs(tmp_path)
    progress_path.write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="file SHA256 mismatch"):
        build_summary(audit, progress, audit_path, progress_path)
