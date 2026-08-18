from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


IDENTITIES = (
    "split37_model101",
    "split37_model103",
    "split37_model107",
    "split41_model109",
    "split41_model113",
    "split41_model127",
)
OPERATIONAL = (
    "alert_accuracy",
    "benign_fpr",
    "known_attack_type_accuracy",
    "unknown_attack_alert_recall",
    "unknown_attack_recall",
)
RESEARCH = {
    "known_macro_f1": ("closed_set_known", "known_macro_f1"),
    "known_balanced_accuracy": (
        "closed_set_known",
        "known_balanced_accuracy",
    ),
    "unknown_auroc": ("unknown_detection", "unknown_auroc"),
    "unknown_aupr_out": ("unknown_detection", "unknown_aupr_out"),
    "fpr_known_at_95_unknown_tpr": (
        "unknown_detection",
        "fpr_known_at_95_unknown_tpr",
    ),
    "oscr_exact_v2": ("joint_open_set", "oscr_exact_v2"),
}


def research_values(contract: dict[str, Any]) -> dict[str, float]:
    return {
        name: float(contract[group][metric])
        for name, (group, metric) in RESEARCH.items()
    }


def finite_history(report: dict[str, Any]) -> tuple[bool, list[int]]:
    invalid_epochs = []
    for item in report["training"]["history"]:
        values = (
            item["training_loss"],
            item["validation_loss"],
            item["meta_outer_loss"],
        )
        if any(value is None or not math.isfinite(float(value)) for value in values):
            invalid_epochs.append(int(item["epoch"]))
    return not invalid_epochs, invalid_epochs


def summarize(evidence_root: Path) -> dict[str, Any]:
    evidence_root = evidence_root.resolve()
    completion_path = evidence_root / "completion.json"
    completion = load_canonical(completion_path, "ensemble completion")
    members = {}
    mean_utilizations = []
    for identity in IDENTITIES:
        evaluation_path = evidence_root / f"member_evaluation_{identity}.json"
        audit_path = evidence_root / f"resource_audit_{identity}.json"
        metrics_path = evidence_root / "members" / identity / "metrics.json"
        evaluation = load_canonical(
            evaluation_path,
            f"{identity} member evaluation",
        )
        audit = load_canonical(audit_path, f"{identity} resource audit")
        metrics = load_canonical(metrics_path, f"{identity} metrics")
        history_is_finite, invalid_epochs = finite_history(metrics)
        fixed = evaluation["fixed_evaluation"]
        mean_utilization = float(
            audit["observed"]["mean_gpu_utilization_percent"]
        )
        mean_utilizations.append(mean_utilization)
        members[identity] = {
            "history_all_losses_finite": history_is_finite,
            "non_finite_epochs": invalid_epochs,
            "operational": {
                name: float(fixed["metrics"][name]) for name in OPERATIONAL
            },
            "research_main": research_values(
                fixed["research_metric_contract"]
            ),
            "resource": {
                "audit_pass": bool(audit["gates"]["all_pass"]),
                "mean_gpu_utilization_percent": mean_utilization,
                "median_gpu_utilization_percent": float(
                    audit["observed"]["median_gpu_utilization_percent"]
                ),
                "peak_gpu_utilization_percent": float(
                    audit["observed"]["peak_gpu_utilization_percent"]
                ),
                "torch_peak_memory_reserved_mib": float(
                    audit["observed"]["torch_peak_memory_reserved_mib"]
                ),
            },
            "source_sha256": {
                "metrics": file_hash(metrics_path),
                "member_evaluation": file_hash(evaluation_path),
                "resource_audit": file_hash(audit_path),
            },
        }
    ensembles = {}
    diagnostic_values: dict[str, list[float]] = {
        "attack_probability_pearson": [],
        "open_score_pearson": [],
        "type_prediction_agreement": [],
    }
    for split_seed in (37, 41):
        path = evidence_root / f"evaluation_split{split_seed}.json"
        evaluation = load_canonical(path, f"split{split_seed} evaluation")
        for split_name in ("validation", "test"):
            for item in evaluation["member_diagnostics"][split_name]:
                for name in diagnostic_values:
                    value = item[name]
                    if value is not None:
                        diagnostic_values[name].append(float(value))
        ensembles[str(split_seed)] = {
            "state": evaluation["state"],
            "operational": {
                name: float(evaluation["operational_metrics"][name])
                for name in OPERATIONAL
            },
            "research_main": research_values(
                evaluation["research_metric_contract"]
            ),
            "expansion_gate": evaluation["expansion_gate"],
            "evaluation_sha256": file_hash(path),
        }
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_fhmm_same_split_ensemble_local_summary_v1"
        ),
        "state": "complete_read_only_local_aggregation",
        "members": members,
        "ensembles": ensembles,
        "macro_mean": completion["macro_mean"],
        "resource_summary": {
            "all_member_audits_pass": all(
                item["resource"]["audit_pass"] for item in members.values()
            ),
            "mean_of_member_mean_gpu_utilization_percent": float(
                np.mean(mean_utilizations)
            ),
            "minimum_member_mean_gpu_utilization_percent": float(
                np.min(mean_utilizations)
            ),
            "maximum_member_mean_gpu_utilization_percent": float(
                np.max(mean_utilizations)
            ),
        },
        "pairwise_diagnostic_range": {
            name: {
                "minimum": float(np.min(values)),
                "maximum": float(np.max(values)),
            }
            for name, values in diagnostic_values.items()
        },
        "decision": {
            "expand_to_seven_scenarios": bool(
                completion["expand_to_seven_scenarios"]
            ),
            "all_effect_gates_passed": bool(
                completion["all_effect_gates_passed"]
            ),
            "all_integrity_passed": bool(
                completion["all_integrity_passed"]
            ),
            "non_finite_member_identities": [
                identity
                for identity, item in members.items()
                if not item["history_all_losses_finite"]
            ],
            "simple_mean_ensemble_adopted_as_self_algorithm": False,
        },
        "source": {
            "evidence_root": str(evidence_root),
            "completion_sha256": file_hash(completion_path),
            "completion_manifest_sha256": completion["manifest_sha256"],
        },
        "claim_boundary": {
            "local_summary_only": True,
            "formal_training_occurred_on_remote_cuda_gpu": True,
            "posthoc_member_evaluation_did_not_select_weights_or_thresholds": True,
            "development_pilot_not_formal_five_seed_confirmation": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    result = summarize(args.evidence_root)
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
