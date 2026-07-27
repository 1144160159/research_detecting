from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


TRAINING_SEEDS = [701, 709, 719]
CORRUPTION_SEEDS = [727, 733, 739]


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(value: Dict[str, Any], path: Path) -> None:
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"non-canonical manifest: {path}")


def create_design(
    project_root: Path,
    krc_protocol_path: Path,
    diagnostic_path: Path,
    output_path: Path,
) -> Dict[str, Any]:
    protocol = load_json(krc_protocol_path)
    diagnostic = load_json(diagnostic_path)
    require_canonical(protocol, krc_protocol_path)
    require_canonical(diagnostic, diagnostic_path)
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_csr_confirmation_protocol_v1"
        or diagnostic.get("schema_version")
        != "strict_v4_krc_certificate_bottleneck_audit_v1"
        or diagnostic.get("passes") is not True
        or diagnostic.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or diagnostic.get("data_use_boundary", {}).get(
            "test_effect_metrics_read"
        )
        is not False
    ):
        raise ValueError("canonical known-only KRC diagnosis required")

    source_identities = {
        f"{row['suite']}/{row['scenario']}"
        for row in protocol["source_registry"]
    }
    prior_development = set(protocol["development_scenario_identities"])
    diagnostic_identities = set(
        diagnostic["data_use_boundary"][
            "observed_identities_become_development_only_for_rrc"
        ]
    )
    if not diagnostic_identities <= source_identities:
        raise ValueError("diagnostic identities must be in source registry")
    all_development = prior_development | diagnostic_identities
    heldout = sorted(source_identities - all_development)
    if len(source_identities) != 102 or len(heldout) != 83:
        raise ValueError("expected 102 sources and 83 RRC held-out scenarios")

    implementation_paths = [
        project_root / "audit_krc_known_certificate_bottleneck.py",
        project_root / "create_strict_v4_rrc_csr_fallback_design.py",
        project_root / "caeos" / "krc_csr_runtime.py",
        project_root / "caeos" / "csr_runtime.py",
        project_root / "caeos" / "csr_exact_replay_runtime.py",
    ]
    implementation_sha256 = {
        path.relative_to(project_root).as_posix(): file_hash(path)
        for path in implementation_paths
    }

    value: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_fallback_design_v1",
        "state": "frozen_design_only_waiting_terminal_negative_krc",
        "algorithm": "rrc_csr_caeos_v1",
        "execution_admitted": False,
        "activation_condition": {
            "current_krc_final_summary_required": True,
            "current_krc_independent_audit_required": True,
            "activate_only_if_krc_primary_gate_fails": True,
            "cancel_if_krc_selects_krc_csr_caeos_v1": True,
        },
        "source_krc_protocol_manifest_sha256": protocol["manifest_sha256"],
        "source_krc_protocol_file_sha256": file_hash(krc_protocol_path),
        "known_only_diagnostic_manifest_sha256": diagnostic[
            "manifest_sha256"
        ],
        "known_only_diagnostic_file_sha256": file_hash(diagnostic_path),
        "implementation_sha256": implementation_sha256,
        "certificate": {
            "unit": "scenario_pooled_across_three_training_seeds",
            "training_seed_count": 3,
            "scenario_mean_error_detection_auroc_minimum": 0.7,
            "per_seed_error_detection_auroc_minimum": 0.68,
            "per_seed_known_safety_active_rate_one_sided_95pct_upper_maximum": (
                0.01
            ),
            "prediction_exact_pairwise_required": True,
            "probability_exact_pairwise_required": True,
            "inactive_risk_exact_pairwise_required": True,
            "risk_uplift_monotone_required": True,
            "known_macro_f1_delta_exact_zero_required": True,
            "absolute_known_macro_f1_threshold": None,
            "unknown_or_test_labels_used": False,
            "selection_uses_test_effect_metrics": False,
        },
        "data_isolation": {
            "prior_krc_development_identities": sorted(prior_development),
            "known_only_diagnostic_identities": sorted(
                diagnostic_identities
            ),
            "overlap_count": len(
                prior_development & diagnostic_identities
            ),
            "all_rrc_development_identities": sorted(all_development),
            "heldout_confirmation_identities": heldout,
            "heldout_confirmation_identity_count": len(heldout),
            "diagnostic_test_effect_metrics_read": False,
            "current_krc_results_not_reused_as_rrc_confirmation": True,
        },
        "confirmation": {
            "training_seeds": TRAINING_SEEDS,
            "corruption_seeds": CORRUPTION_SEEDS,
            "training_seed_overlap_with_krc": False,
            "corruption_seed_overlap_with_krc": False,
            "heldout_scenario_count": len(heldout),
            "capture_count": len(heldout) * len(TRAINING_SEEDS),
            "conditions_per_capture": 6,
            "evaluation_count": (
                len(heldout) * len(TRAINING_SEEDS) * 6
            ),
            "primary_enabled_scenario_count_minimum": 18,
            "primary_enabled_suite_count_minimum": 4,
            "suite_nonnegative_count_minimum_each_metric": 5,
            "overall_directed_means_strictly_positive": True,
            "modality_missing_composite_improves": True,
            "gaussian_drift_composite_improves": True,
            "each_family_metric_regression_maximum": 0.02,
            "bootstrap_replicates": 10000,
            "bootstrap_seed": 20260727,
        },
        "output_counts_at_freeze": {
            "execution_protocol": 0,
            "captures": 0,
            "evaluations": 0,
            "summary": 0,
            "audit": 0,
        },
        "claim_boundary": {
            "design_is_not_algorithm_effect_evidence": True,
            "known_only_diagnosis_is_not_test_effect_evidence": True,
            "current_krc_protocol_and_conclusion_unchanged": True,
            "rrc_requires_new_runtime_execution_and_independent_audit": True,
            "rrc_success_would_not_alone_establish_sota": True,
        },
        "output_path": output_path.resolve().as_posix(),
    }
    value["manifest_sha256"] = canonical_hash(value)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--krc-protocol", type=Path, required=True)
    parser.add_argument("--diagnostic", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_design(
        args.project_root.resolve(),
        args.krc_protocol.resolve(),
        args.diagnostic.resolve(),
        args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "manifest_sha256": value["manifest_sha256"],
                "file_sha256": file_hash(args.output.resolve()),
                "heldout_scenario_count": value["confirmation"][
                    "heldout_scenario_count"
                ],
                "execution_admitted": value["execution_admitted"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
