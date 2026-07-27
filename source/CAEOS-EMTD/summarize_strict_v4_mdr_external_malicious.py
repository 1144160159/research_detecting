from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

import numpy as np
from scipy.stats import wilcoxon

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_mdr_external_malicious import (
    load,
    slug,
    verify_protocol,
)


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def metric_report(
    metrics: Dict[str, Any], method: str
) -> Dict[str, float]:
    if method == "mdr_caeos_v1":
        if (
            metrics.get("schema_version")
            != "strict_v4_mdr_external_runtime_metrics_v1"
        ):
            raise ValueError("unexpected MDR external metrics schema")
        diagnostics = metrics.get("diagnostics", {})
        routing = metrics.get("routing", {})
        if (
            diagnostics.get(
                "unknown_or_test_labels_used_for_fit_selection_calibration_"
                "threshold_or_routing"
            )
            is not False
            or diagnostics.get("test_labels_used_for_final_metrics_only")
            is not True
            or diagnostics.get("external_weight_reselected") is not False
            or any(
                routing.get(name) is not True
                for name in (
                    "inactive_prediction_exactly_pairwise",
                    "inactive_risk_exactly_pairwise",
                    "inactive_probability_exactly_pairwise",
                )
            )
        ):
            raise ValueError("MDR external leakage or fallback gate failed")
        value = metrics.get("reports", {}).get("candidate")
    elif method == "opendetect":
        if metrics.get("method") != "opendetect":
            raise ValueError("unexpected OpenDetect external metrics")
        value = metrics.get("reports", {}).get("opendetect")
    else:
        raise ValueError(f"unsupported external method: {method}")
    if not isinstance(value, dict):
        raise ValueError(f"report missing for {method}")
    return {
        name: float(value[name])
        for name in (*METRICS, "known_macro_f1")
    }


def split_integrity(metrics: Dict[str, Any]) -> bool:
    split = metrics.get("split_metadata", {})
    overlap = (
        split.get("fingerprint_overlap", {})
        if isinstance(split, dict)
        else {}
    )
    filter_info = (
        split.get("cross_label_fingerprint_filter", {})
        if isinstance(split, dict)
        else {}
    )
    return (
        overlap.get("train_validation") == 0
        and overlap.get("train_test") == 0
        and overlap.get("validation_test") == 0
        and filter_info.get("unknown_labels_used") is False
    )


def oriented(
    candidate: Dict[str, float],
    comparator: Dict[str, float],
    metric: str,
) -> float:
    if metric == "unknown_fpr95":
        return comparator[metric] - candidate[metric]
    return candidate[metric] - comparator[metric]


def bootstrap_interval(
    values: np.ndarray, repetitions: int, seed: int
) -> list[float]:
    rng = np.random.default_rng(int(seed))
    indices = rng.integers(
        0, len(values), size=(int(repetitions), len(values))
    )
    means = values[indices].mean(axis=1)
    return [
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    ]


def holm_adjust(raw: Dict[str, float]) -> Dict[str, float]:
    ordered = sorted(raw.items(), key=lambda item: (item[1], item[0]))
    adjusted: Dict[str, float] = {}
    running = 0.0
    total = len(ordered)
    for index, (name, value) in enumerate(ordered):
        running = max(running, min(1.0, (total - index) * value))
        adjusted[name] = running
    return adjusted


def aggregate(
    records: list[Dict[str, Any]],
    *,
    repetitions: int,
    bootstrap_seed: int,
) -> Dict[str, Any]:
    grouped: Dict[tuple[str, str], list[Dict[str, float]]] = defaultdict(
        list
    )
    for record in records:
        gains = {
            metric: oriented(
                record["candidate"], record["comparator"], metric
            )
            for metric in METRICS
        }
        gains["known_macro_f1"] = (
            record["candidate"]["known_macro_f1"]
            - record["comparator"]["known_macro_f1"]
        )
        grouped[
            (record["dataset"], record["unknown_attack_family"])
        ].append(gains)
    blocks = []
    for (dataset, attack), values in sorted(grouped.items()):
        if len(values) != 3:
            raise ValueError(
                f"three seed records required for {dataset}/{attack}"
            )
        blocks.append(
            {
                "dataset": dataset,
                "unknown_attack_family": attack,
                "gains": {
                    metric: float(
                        np.mean([value[metric] for value in values])
                    )
                    for metric in (*METRICS, "known_macro_f1")
                },
            }
        )
    if not blocks:
        raise ValueError("MDR external aggregation has no label blocks")
    raw_p: Dict[str, float] = {}
    summary: Dict[str, Any] = {}
    for offset, metric in enumerate(METRICS):
        values = np.asarray(
            [block["gains"][metric] for block in blocks], dtype=float
        )
        try:
            raw_p[metric] = float(
                wilcoxon(
                    values, alternative="greater", zero_method="wilcox"
                ).pvalue
            )
        except ValueError:
            raw_p[metric] = 1.0
        summary[metric] = {
            "oriented_mean_gain": float(values.mean()),
            "label_block_bootstrap_95ci": bootstrap_interval(
                values, repetitions, int(bootstrap_seed) + offset
            ),
            "wilcoxon_raw_p": raw_p[metric],
        }
    adjusted = holm_adjust(raw_p)
    for metric in METRICS:
        summary[metric]["wilcoxon_holm_p"] = adjusted[metric]
    datasets = {}
    for dataset in sorted({block["dataset"] for block in blocks}):
        subset = [block for block in blocks if block["dataset"] == dataset]
        datasets[dataset] = {
            metric: float(
                np.mean([block["gains"][metric] for block in subset])
            )
            for metric in (*METRICS, "known_macro_f1")
        }
    return {
        "label_blocks": blocks,
        "label_block_count": len(blocks),
        "metrics": summary,
        "datasets": datasets,
        "known_macro_f1_mean_gain": float(
            np.mean(
                [block["gains"]["known_macro_f1"] for block in blocks]
            )
        ),
    }


def load_bound_metrics(
    output: Path,
    protocol: Dict[str, Any],
    scenario: Dict[str, Any],
    method: str,
) -> Dict[str, Any]:
    metrics_path = output / "metrics.json"
    provenance_path = output / "provenance.json"
    metrics, provenance = load(metrics_path), load(provenance_path)
    if (
        provenance.get("manifest_sha256") != canonical_hash(provenance)
        or provenance.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or provenance.get("metrics_sha256") != file_hash(metrics_path)
        or provenance.get("method") != method
        or provenance.get("dataset") != scenario["dataset"]
        or provenance.get("unknown_attack_family")
        != scenario["unknown_attack_family"]
        or int(provenance.get("seed", -1)) != int(scenario["seed"])
        or provenance.get(
            "unknown_or_test_metrics_used_for_configuration"
        )
        is not False
    ):
        raise ValueError(f"MDR external provenance failed: {output}")
    return metrics


def summarize(
    protocol: Dict[str, Any], run_root: Path
) -> Dict[str, Any]:
    records = []
    for scenario in protocol["scenarios"]:
        block = (
            run_root
            / scenario["dataset"]
            / (
                f"{slug(scenario['unknown_attack_family'])}_"
                f"seed{scenario['seed']}"
            )
        )
        candidate_metrics = load_bound_metrics(
            block / "mdr_caeos_v1",
            protocol,
            scenario,
            "mdr_caeos_v1",
        )
        comparator_metrics = load_bound_metrics(
            block / "opendetect", protocol, scenario, "opendetect"
        )
        if not split_integrity(candidate_metrics) or not split_integrity(
            comparator_metrics
        ):
            raise ValueError(f"MDR external split integrity failed: {block}")
        if (
            candidate_metrics["split_metadata"]["split_fingerprint"]
            != comparator_metrics["split_metadata"]["split_fingerprint"]
        ):
            raise ValueError("candidate/comparator split fingerprint mismatch")
        records.append(
            {
                "dataset": scenario["dataset"],
                "unknown_attack_family": scenario[
                    "unknown_attack_family"
                ],
                "seed": int(scenario["seed"]),
                "candidate": metric_report(
                    candidate_metrics, "mdr_caeos_v1"
                ),
                "comparator": metric_report(
                    comparator_metrics, "opendetect"
                ),
            }
        )
    statistics = protocol["statistics"]
    aggregation = aggregate(
        records,
        repetitions=int(statistics["bootstrap_repetitions"]),
        bootstrap_seed=int(statistics["bootstrap_seed"]),
    )
    gates = protocol["confirmation_gate"]
    checks = {
        "coverage_complete_and_failure_count_zero": (
            2 * len(records) == protocol["expected_formal_runs"]
            and not list(run_root.glob("**/failure.json"))
        ),
        "unknown_or_test_labels_used_for_fit_selection_or_threshold": False,
        "all_four_oriented_means_strictly_positive": all(
            aggregation["metrics"][metric]["oriented_mean_gain"] > 0.0
            for metric in METRICS
        ),
        "all_four_label_block_bootstrap_95ci_lower_strictly_positive": all(
            aggregation["metrics"][metric][
                "label_block_bootstrap_95ci"
            ][0]
            > 0.0
            for metric in METRICS
        ),
        "all_four_wilcoxon_holm_p_below_0_05": all(
            aggregation["metrics"][metric]["wilcoxon_holm_p"] < 0.05
            for metric in METRICS
        ),
        "both_dataset_four_metric_means_nonnegative": all(
            aggregation["datasets"][dataset][metric] >= 0.0
            for dataset in aggregation["datasets"]
            for metric in METRICS
        ),
        "known_macro_f1_mean_gain_minimum": (
            aggregation["known_macro_f1_mean_gain"]
            >= float(gates["known_macro_f1_mean_gain_minimum"])
        ),
        "known_macro_f1_each_dataset_gain_minimum": all(
            aggregation["datasets"][dataset]["known_macro_f1"]
            >= float(gates["known_macro_f1_each_dataset_gain_minimum"])
            for dataset in aggregation["datasets"]
        ),
    }
    # The frozen gate value is false; pass means forbidden use stayed absent.
    leakage_passes = (
        gates[
            "unknown_or_test_labels_used_for_fit_selection_or_threshold"
        ]
        is False
        and checks[
            "unknown_or_test_labels_used_for_fit_selection_or_threshold"
        ]
        is False
    )
    effective = {
        **checks,
        "unknown_or_test_labels_used_for_fit_selection_or_threshold": (
            leakage_passes
        ),
    }
    passes = all(effective.values())
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_external_malicious_summary_v1"
        ),
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": "mdr_caeos_v1",
        "primary_comparator": "opendetect",
        "scenario_count": len(records),
        "formal_run_count": 2 * len(records),
        "failure_count": len(list(run_root.glob("**/failure.json"))),
        "aggregation": aggregation,
        "validation": {"checks": effective, "passes": passes},
        "fresh_two_dataset_external_malicious_confirmation_passes": passes,
        "claim_boundary": protocol["claim_boundary"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    verify_protocol(protocol, args.project_root)
    value = summarize(protocol, args.run_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output.parent / "summary_complete").touch()
    print(json.dumps(value["validation"], sort_keys=True))


if __name__ == "__main__":
    main()
