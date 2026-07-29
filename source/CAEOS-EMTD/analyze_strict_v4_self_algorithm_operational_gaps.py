from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


TARGET = 0.95
FPR_LIMIT = 0.05


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


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_canonical(payload: dict[str, Any], label: str) -> None:
    declared = payload.get("manifest_sha256")
    body = dict(payload)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError(f"{label} canonical mismatch")


def metric_gaps(metrics: dict[str, float]) -> dict[str, float]:
    unknown_alert = float(metrics["unknown_attack_alert_recall"])
    unknown_label = float(metrics["unknown_attack_recall"])
    return {
        "alert_accuracy_deficit_to_95": max(
            0.0, TARGET - float(metrics["alert_accuracy"])
        ),
        "benign_fpr_excess_over_5": max(
            0.0, float(metrics["benign_fpr"]) - FPR_LIMIT
        ),
        "known_attack_type_accuracy_deficit_to_95": max(
            0.0, TARGET - float(metrics["known_attack_type_accuracy"])
        ),
        "unknown_attack_recall_deficit_to_95": max(
            0.0, TARGET - unknown_label
        ),
        "unknown_missed_before_alert_fraction": max(0.0, 1.0 - unknown_alert),
        "unknown_alerted_but_not_labeled_unknown_fraction": max(
            0.0, unknown_alert - unknown_label
        ),
    }


def ranking(
    records: list[dict[str, Any]], metric: str, reverse: bool
) -> list[dict[str, Any]]:
    ranked = sorted(
        records,
        key=lambda record: float(record["operational_metrics"][metric]),
        reverse=reverse,
    )
    return [
        {
            "scenario": record["scenario"],
            "seed": record["seed"],
            "value": float(record["operational_metrics"][metric]),
        }
        for record in ranked
    ]


def build_analysis(
    evaluation: dict[str, Any], evaluation_path: Path
) -> dict[str, Any]:
    verify_canonical(evaluation, "core warning evaluation")
    records = evaluation.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("evaluation records are required")
    per_seed = {
        seed: {
            "metrics": value["mean"],
            "gates": value["gates"],
            "gaps": metric_gaps(value["mean"]),
        }
        for seed, value in evaluation["by_seed"].items()
    }
    aggregate = evaluation["suite_equal_mean"]
    result: dict[str, Any] = {
        "schema_version": "strict_v4_self_algorithm_operational_gap_analysis_v1",
        "state": "complete_read_only_analysis",
        "scope": {
            "algorithm": "Pairwise-CAEOS hierarchical probability warning",
            "suite": evaluation["suites"],
            "seeds": evaluation["observed_seeds"],
            "scenario_count": evaluation["scenario_count"],
            "self_algorithm_target_only": True,
        },
        "target_contract": {
            "alert_accuracy_at_least": TARGET,
            "benign_fpr_strictly_below": FPR_LIMIT,
            "known_attack_type_accuracy_at_least": TARGET,
            "unknown_attack_recall_at_least": TARGET,
            "all_fresh_seeds_must_pass": True,
        },
        "current_effect": {
            "aggregate_metrics": aggregate,
            "aggregate_gates": evaluation["aggregate_gates"],
            "all_seed_basic_warning_95_5_gate": evaluation[
                "all_seed_basic_warning_95_5_gate"
            ],
            "all_seed_full_known_unknown_95_5_gate": evaluation[
                "all_seed_full_known_unknown_95_5_gate"
            ],
            "aggregate_gaps": metric_gaps(aggregate),
            "per_seed": per_seed,
        },
        "failure_rankings": {
            "lowest_unknown_attack_recall": ranking(
                records, "unknown_attack_recall", False
            ),
            "highest_benign_fpr": ranking(records, "benign_fpr", True),
            "lowest_known_attack_type_accuracy": ranking(
                records, "known_attack_type_accuracy", False
            ),
            "lowest_alert_accuracy": ranking(records, "alert_accuracy", False),
        },
        "diagnosis": {
            "known_type_mean_passes": (
                aggregate["known_attack_type_accuracy"] >= TARGET
            ),
            "seed_stable_fpr_control_fails": any(
                value["mean"]["benign_fpr"] >= FPR_LIMIT
                for value in evaluation["by_seed"].values()
            ),
            "unknown_labeling_is_primary_effect_gap": (
                aggregate["unknown_attack_recall"] < TARGET
            ),
            "unknown_gap_has_two_stages": {
                "pre_alert_miss": (
                    1.0 - aggregate["unknown_attack_alert_recall"]
                ),
                "alerted_but_not_unknown": (
                    aggregate["unknown_attack_alert_recall"]
                    - aggregate["unknown_attack_recall"]
                ),
            },
        },
        "next_experiment_constraints": {
            "development_source": "seed7 only",
            "fresh_confirmation_must_use_new_unseen_seeds": True,
            "alert_and_unknown_thresholds_must_be_decoupled": True,
            "alert_threshold_must_use_known_validation_benign_only": True,
            "unknown_threshold_may_use_training_derived_pseudo_unknown_only": True,
            "fresh_test_or_unknown_labels_may_select_nothing": True,
            "recommended_first_changes": [
                "cross-fitted or upper-confidence benign alert calibration",
                "class-conditional pseudo-unknown rejection calibration",
                "capture-group-balanced benign validation sampling",
            ],
        },
        "claim_boundary": {
            "aggregate_mean_pass_does_not_authorize_a_claim": True,
            "read_only_failure_analysis_does_not_select_hyperparameters": True,
            "xgboost_or_other_baseline_cannot_satisfy_the_self_algorithm_target": True,
        },
        "binding": {
            "evaluation_file_sha256": file_hash(evaluation_path),
            "evaluation_manifest_sha256": evaluation["manifest_sha256"],
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def render_markdown(analysis: dict[str, Any]) -> str:
    effect = analysis["current_effect"]
    metrics = effect["aggregate_metrics"]
    gaps = effect["aggregate_gaps"]
    lines = [
        "# strict-v4 self-algorithm operational gap analysis",
        "",
        "## Conclusion",
        "",
        "- The 95/5 target applies to the self algorithm only.",
        (
            f"- Aggregate alert accuracy is {metrics['alert_accuracy']:.4%}; "
            f"benign FPR is {metrics['benign_fpr']:.4%}."
        ),
        (
            "- Known attack type accuracy is "
            f"{metrics['known_attack_type_accuracy']:.4%}; unknown attack "
            f"recall is {metrics['unknown_attack_recall']:.4%}."
        ),
        (
            "- Aggregate means are not sufficient: all-seed basic gate = "
            f"{effect['all_seed_basic_warning_95_5_gate']}; all-seed full "
            f"gate = {effect['all_seed_full_known_unknown_95_5_gate']}."
        ),
        "",
        "## Primary gaps",
        "",
        (
            "- Unknown samples missed before alert: "
            f"{gaps['unknown_missed_before_alert_fraction']:.4%}."
        ),
        (
            "- Unknown samples alerted but not labeled unknown: "
            f"{gaps['unknown_alerted_but_not_labeled_unknown_fraction']:.4%}."
        ),
        (
            "- Unknown recall deficit to 95%: "
            f"{gaps['unknown_attack_recall_deficit_to_95']:.4%}."
        ),
        "",
        "## Per-seed hard gate",
        "",
        "| Seed | Alert accuracy | Benign FPR | Known type accuracy | Unknown recall | Basic | Full |",
        "|---:|---:|---:|---:|---:|:---:|:---:|",
    ]
    for seed, value in effect["per_seed"].items():
        mean = value["metrics"]
        gates = value["gates"]
        lines.append(
            f"| {seed} | {mean['alert_accuracy']:.4%} | "
            f"{mean['benign_fpr']:.4%} | "
            f"{mean['known_attack_type_accuracy']:.4%} | "
            f"{mean['unknown_attack_recall']:.4%} | "
            f"{gates['basic_warning_95_5_gate']} | "
            f"{gates['full_known_unknown_95_5_gate']} |"
        )
    lines.extend(
        [
            "",
            "## Next experiment",
            "",
            "Use seed7 only for development. Decouple alert calibration from unknown rejection, then confirm the frozen choice on new unseen seeds. No fresh test or unknown label may select a threshold.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()
    evaluation_path = args.evaluation.resolve()
    analysis = build_analysis(load(evaluation_path), evaluation_path)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text(render_markdown(analysis), encoding="utf-8")
    print(json.dumps(analysis, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
