import json
from pathlib import Path

from audit_csr_caeos_pilot_integrity_failure import audit
from create_strict_v4_external_confirmation_protocol import canonical_hash
from finalize_csr_caeos_pilot_integrity_failure import finalize


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write_evaluations(root: Path, design):
    evaluations = []
    index = 0
    for suite, scenarios in design["development"]["scenarios"].items():
        for scenario in scenarios:
            for condition in design["development"]["conditions"]:
                routing = {
                    "prediction_exactly_pairwise_all_rows": True,
                    "probability_exactly_pairwise_all_rows": index != 7,
                    "risk_monotone_not_below_pairwise": True,
                    "inactive_risk_exactly_pairwise": True,
                    "unknown_or_test_labels_used": False,
                }
                value = canonical(
                    {
                        "schema_version": (
                            "strict_v4_csr_caeos_pilot_evaluation_v1"
                        ),
                        "state": "complete",
                        "algorithm": "csr_caeos_v1",
                        "design_manifest_sha256": design["manifest_sha256"],
                        "suite": suite,
                        "scenario": scenario,
                        "condition": condition,
                        "routing": routing,
                        "pairwise_report": {"unknown_auroc": 0.1},
                        "candidate_report": {"unknown_auroc": 0.9},
                    }
                )
                path = root / suite / scenario / condition / "evaluation.json"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(
                    json.dumps(value, indent=2) + "\n", encoding="utf-8"
                )
                evaluations.append((path, value))
                index += 1
    return evaluations


def fixtures(tmp_path):
    scenarios = {
        f"suite_{suite}": [f"scenario_{suite}_0", f"scenario_{suite}_1"]
        for suite in range(7)
    }
    conditions = [
        "clean",
        "modality_missing",
        "field_missing",
        "row_missing",
        "feature_shuffle",
        "gaussian_drift",
    ]
    design = canonical(
        {
            "schema_version": "strict_v4_csr_caeos_design_v4",
            "development": {
                "scenarios": scenarios,
                "conditions": conditions,
            },
        }
    )
    protocol = canonical(
        {
            "schema_version": (
                "strict_v4_csr_caeos_pilot_protocol_v1"
            ),
            "design_manifest_sha256": design["manifest_sha256"],
        }
    )
    admission = canonical(
        {
            "schema_version": "strict_v4_csr_caeos_clean_admission_v1",
            "design_manifest_sha256": design["manifest_sha256"],
            "passes": True,
            "test_effect_metrics_read": False,
        }
    )
    evaluations = write_evaluations(tmp_path / "evaluations", design)
    return protocol, design, admission, evaluations


def test_integrity_failure_is_effect_blind_and_blocks_expansion(tmp_path):
    protocol, design, admission, evaluations = fixtures(tmp_path)
    rejection = finalize(
        protocol,
        design,
        admission,
        evaluations,
        finalizer_file_sha256="f" * 64,
    )
    assert rejection["evaluation_count"] == 84
    assert rejection["invalid_routing_count"] == 1
    assert rejection["valid_routing_count"] == 83
    assert rejection["failed_fields"] == [
        "probability_exactly_pairwise_all_rows"
    ]
    assert rejection["effect_metric_fields_accessed_for_integrity_decision"] == []
    assert rejection["scientific_effect_decision"] is None
    assert rejection["expand_to_full102"] is False


def test_independent_integrity_audit_recomputes_exact_rejection(tmp_path):
    protocol, design, admission, evaluations = fixtures(tmp_path)
    rejection = finalize(
        protocol,
        design,
        admission,
        evaluations,
        finalizer_file_sha256="f" * 64,
    )
    result = audit(
        protocol,
        design,
        admission,
        rejection,
        evaluations,
        finalizer_file_sha256="f" * 64,
        auditor_file_sha256="a" * 64,
    )
    assert result["passes"] is True
    assert result["claim_boundary"][
        "audit_passes_means_negative_branch_integrity_only"
    ] is True
