from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CORE_DATASETS = ("cicids2017",)
CONFIRMATION_SEEDS = (907, 911, 919)
MAIN_BASELINES = (
    "xgboost_binary_warning",
    "mlp_msp",
    "mlp_energy",
    "mlp_openmax",
    "mahalanobis_pp",
    "opendetect",
    "ronetc",
)
SELF_ALGORITHMS = (
    "hierarchical_pairwise",
    "hierarchical_rrc_if_confirmed",
)


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_protocol(implementation_sha256: str) -> dict[str, Any]:
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_core_warning_protocol_v1",
        "status": "frozen_before_fresh_seed_confirmation",
        "purpose": (
            "separate an operational 95/5 warning gate from the broad "
            "strict-v4 open-set SOTA claim"
        ),
        "output_hierarchy": [
            "benign",
            "known_attack_type",
            "unknown_attack",
        ],
        "core_confirmation": {
            "datasets": list(CORE_DATASETS),
            "dataset_role": (
                "CICIDS2017 is a canonical pilot and first confirmation suite; "
                "it is not evidence of cross-dataset generalization"
            ),
            "fresh_seeds": list(CONFIRMATION_SEEDS),
            "development_seed_excluded": 7,
            "split_rule": "capture-or-group-disjoint before model fitting",
            "threshold_source": "validation benign samples only",
            "reporting_unit": "scenario mean, seed mean, and pooled confusion counts",
            "all_fresh_seeds_must_pass": True,
        },
        "basic_warning_gate": {
            "alert_accuracy_min": 0.95,
            "alert_precision_min": 0.95,
            "attack_recall_min": 0.95,
            "benign_fpr_strict_max": 0.05,
            "known_attack_type_accuracy_min": 0.95,
        },
        "open_set_gate": {
            "unknown_attack_alert_recall_min": 0.95,
            "unknown_label_recall_min": 0.95,
            "unknown_label_precision_reported": True,
            "known_macro_f1_reported": True,
            "auroc_aupr_fpr95_oscr_reported": True,
            "selective_sota_allowed": True,
            "selective_sota_requires_predeclared_metrics_and_comparators": True,
        },
        "data_optimization": {
            "allowed": [
                "pre-model label normalization and attack-family hierarchy",
                "cross-label duplicate removal",
                "capture-or-group-disjoint splitting",
                "training-only class weighting or resampling",
                "predeclared minimum-support routing to a rare-class challenge set",
            ],
            "forbidden": [
                "dropping scenarios after observing test metrics",
                "selecting a dataset because its seed7 result passed",
                "balancing or filtering the test set to inflate accuracy",
                "using unknown or test labels for threshold selection",
                "merging labels after observing the confusion matrix",
            ],
            "rare_classes": (
                "remain in malicious-alert evaluation and are reported separately "
                "when excluded from fine-grained type confirmation"
            ),
        },
        "model_structure": {
            "stage_1": (
                "benign-versus-malicious warning score calibrated to a validation "
                "benign FPR budget"
            ),
            "stage_2": (
                "known attack type versus unknown attack using the frozen open-set "
                "risk score"
            ),
            "no_test_time_oracle": True,
        },
        "main_baselines": list(MAIN_BASELINES),
        "self_algorithms": list(SELF_ALGORITHMS),
        "baseline_policy": {
            "main_table_count": len(MAIN_BASELINES),
            "knn_vim_arpl_cade_role": "supplementary_or_paper_native_metric_table",
            "ablation_methods_are_not_external_baselines": True,
        },
        "claim_boundary": {
            "seed7_sensitivity_is_diagnostic_only": True,
            "single_dataset_pass_is_not_comprehensive_sota": True,
            "basic_gate_and_open_set_sota_are_distinct_claims": True,
            "cross_dataset_claim_requires_additional_frozen_suites": True,
        },
        "implementation_sha256": {
            "create_strict_v4_core_warning_protocol.py": implementation_sha256
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    args = parser.parse_args()
    implementation = (
        args.project_root.resolve() / "create_strict_v4_core_warning_protocol.py"
    )
    protocol = create_protocol(file_hash(implementation))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
