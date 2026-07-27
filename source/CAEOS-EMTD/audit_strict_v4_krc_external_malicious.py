from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
from typing import Any, Dict

import numpy as np
from scipy.stats import wilcoxon

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_") or (
        "unnamed"
    )


def oriented(
    candidate: Dict[str, float],
    comparator: Dict[str, float],
    metric: str,
) -> float:
    if metric == "unknown_fpr95":
        return float(comparator[metric]) - float(candidate[metric])
    return float(candidate[metric]) - float(comparator[metric])


def bootstrap(
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


def holm(raw: Dict[str, float]) -> Dict[str, float]:
    ordered = sorted(raw.items(), key=lambda item: (item[1], item[0]))
    adjusted = {}
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
    seed: int,
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
        gains["known_macro_f1"] = float(
            record["candidate"]["known_macro_f1"]
        ) - float(record["comparator"]["known_macro_f1"])
        grouped[
            (record["dataset"], record["unknown_attack_family"])
        ].append(gains)
    blocks = []
    for (dataset, attack), seed_values in sorted(grouped.items()):
        if len(seed_values) != 3:
            raise ValueError(
                f"independent audit needs three seeds: {dataset}/{attack}"
            )
        blocks.append(
            {
                "dataset": dataset,
                "unknown_attack_family": attack,
                "gains": {
                    metric: float(
                        np.mean(
                            [value[metric] for value in seed_values]
                        )
                    )
                    for metric in (*METRICS, "known_macro_f1")
                },
            }
        )
    raw_p = {}
    metric_summary = {}
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
        metric_summary[metric] = {
            "oriented_mean_gain": float(values.mean()),
            "label_block_bootstrap_95ci": bootstrap(
                values, repetitions, int(seed) + offset
            ),
            "wilcoxon_raw_p": raw_p[metric],
        }
    adjusted = holm(raw_p)
    for metric in METRICS:
        metric_summary[metric]["wilcoxon_holm_p"] = adjusted[metric]
    datasets = {}
    for dataset in sorted({block["dataset"] for block in blocks}):
        subset = [block for block in blocks if block["dataset"] == dataset]
        datasets[dataset] = {
            metric: float(
                np.mean(
                    [block["gains"][metric] for block in subset]
                )
            )
            for metric in (*METRICS, "known_macro_f1")
        }
    return {
        "label_blocks": blocks,
        "label_block_count": len(blocks),
        "metrics": metric_summary,
        "datasets": datasets,
        "known_macro_f1_mean_gain": float(
            np.mean(
                [
                    block["gains"]["known_macro_f1"]
                    for block in blocks
                ]
            )
        ),
    }


def gate(
    aggregation: Dict[str, Any], gates: Dict[str, Any]
) -> Dict[str, bool]:
    return {
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


def report(value: Dict[str, Any]) -> Dict[str, float]:
    return {
        name: float(value[name])
        for name in (*METRICS, "known_macro_f1")
    }


def audit(
    protocol: Dict[str, Any],
    summary: Dict[str, Any],
    run_root: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_external_malicious_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
        or summary.get("schema_version")
        != "strict_v4_krc_external_malicious_summary_v1"
        or summary.get("manifest_sha256") != canonical_hash(summary)
        or summary.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("canonical KRC external protocol and summary required")

    pairwise_records = []
    opendetect_records = []
    observed_file_hashes = {}
    structural = {
        "execution_complete_marker_exists": (
            run_root / "execution_complete"
        ).is_file(),
        "failure_count_zero": not list(run_root.rglob("failure.json")),
    }
    all_task_checks = True
    for task in protocol["tasks"]:
        block = (
            run_root
            / task["dataset"]
            / (
                f"{slug(task['unknown_attack_family'])}_"
                f"seed{task['training_seed']}"
            )
        )
        candidate_path = block / "krc_csr_caeos_v1" / "metrics.json"
        open_path = block / "opendetect" / "metrics.json"
        candidate_provenance_path = (
            block / "krc_csr_caeos_v1" / "provenance.json"
        )
        open_provenance_path = block / "opendetect" / "provenance.json"
        candidate = load(candidate_path)
        opendetect = load(open_path)
        candidate_provenance = load(candidate_provenance_path)
        open_provenance = load(open_provenance_path)
        for path in (candidate_path, open_path):
            observed_file_hashes[
                path.relative_to(run_root).as_posix()
            ] = file_hash(path)

        candidate_split = candidate.get("split_metadata", {})
        open_split = opendetect.get("split_metadata", {})
        overlap = candidate_split.get("fingerprint_overlap", {})
        open_overlap = open_split.get("fingerprint_overlap", {})
        candidate_routing = candidate.get("routing", {})
        diagnostics = candidate.get("diagnostics", {})
        task_ok = bool(
            candidate.get("schema_version")
            == "strict_v4_krc_external_runtime_metrics_v1"
            and candidate.get("manifest_sha256")
            == canonical_hash(candidate)
            and candidate.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
            and candidate.get("dataset") == task["dataset"]
            and candidate.get("unknown_attack_family")
            == task["unknown_attack_family"]
            and int(candidate.get("training_seed", -1))
            == int(task["training_seed"])
            and all(int(value) == 0 for value in overlap.values())
            and all(int(value) == 0 for value in open_overlap.values())
            and candidate_split.get("cross_label_fingerprint_filter", {}).get(
                "unknown_labels_used"
            )
            is False
            and open_split.get("cross_label_fingerprint_filter", {}).get(
                "unknown_labels_used"
            )
            is False
            and candidate_split.get("split_fingerprint")
            == open_split.get("split_fingerprint")
            and diagnostics.get(
                "unknown_or_test_labels_used_for_fit_selection_calibration_"
                "threshold_or_routing"
            )
            is False
            and diagnostics.get("external_parameters_reselected") is False
            and all(
                candidate_routing.get(name) is True
                for name in (
                    "prediction_exactly_pairwise_all_rows",
                    "probability_exactly_pairwise_all_rows",
                    "risk_monotone_not_below_pairwise",
                    "inactive_risk_exactly_pairwise",
                    "disabled_risk_exactly_pairwise_all_rows",
                )
            )
            and opendetect.get("method") == "opendetect"
            and candidate_provenance.get("manifest_sha256")
            == canonical_hash(candidate_provenance)
            and open_provenance.get("manifest_sha256")
            == canonical_hash(open_provenance)
            and candidate_provenance.get("metrics_sha256")
            == file_hash(candidate_path)
            and open_provenance.get("metrics_sha256")
            == file_hash(open_path)
            and candidate_provenance.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
            and open_provenance.get("protocol_manifest_sha256")
            == protocol["manifest_sha256"]
        )
        all_task_checks = all_task_checks and task_ok
        candidate_report = report(candidate["reports"]["candidate"])
        base = {
            "dataset": task["dataset"],
            "unknown_attack_family": task["unknown_attack_family"],
            "seed": int(task["training_seed"]),
            "candidate": candidate_report,
        }
        pairwise_records.append(
            {
                **base,
                "comparator": report(
                    candidate["reports"]["embedded_pairwise"]
                ),
            }
        )
        opendetect_records.append(
            {
                **base,
                "comparator": report(
                    opendetect["reports"]["opendetect"]
                ),
            }
        )

    statistics = protocol["statistics"]
    repetitions = int(statistics["bootstrap_repetitions"])
    seed = int(statistics["bootstrap_seed"])
    aggregations = {
        "embedded_pairwise": aggregate(
            pairwise_records, repetitions=repetitions, seed=seed
        ),
        "opendetect": aggregate(
            opendetect_records,
            repetitions=repetitions,
            seed=seed + 1000,
        ),
    }
    gates = protocol["confirmation_gate"]["against_each_comparator"]
    checks_by_comparator = {
        name: gate(value, gates)
        for name, value in aggregations.items()
    }
    effect_passes = all(
        all(checks.values()) for checks in checks_by_comparator.values()
    )
    expected = int(
        protocol["task_counts"]["total_scenarios_per_algorithm"]
    )
    structural.update(
        {
            "all_96_task_identities_validate": (
                all_task_checks
                and len(pairwise_records) == expected
                and len(opendetect_records) == expected
            ),
            "metric_file_inventory_matches_summary": (
                observed_file_hashes == summary["metric_file_sha256"]
            ),
            "aggregations_match_independent_recomputation": (
                aggregations == summary["aggregations"]
            ),
            "comparator_checks_match_independent_recomputation": (
                checks_by_comparator == summary["checks_by_comparator"]
            ),
            "reported_effect_decision_matches": (
                summary[
                    "fresh_two_dataset_external_malicious_confirmation_passes"
                ]
                is effect_passes
                and summary["selection"]
                == (
                    "krc_csr_caeos_v1"
                    if effect_passes
                    else "caeos_pairwise"
                )
            ),
        }
    )
    validation_passes = all(structural.values())
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_external_malicious_audit_v1"
        ),
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "scenario_count": expected,
        "independent_aggregations": aggregations,
        "independent_checks_by_comparator": checks_by_comparator,
        "independently_recomputed_effect_gate_passes": effect_passes,
        "checks": structural,
        "passes": validation_passes,
        "decision_matches_summary": validation_passes,
        "external_effect_gate_passes": effect_passes,
        "claim_boundary": {
            "audit_does_not_import_summary_implementation": True,
            "audit_pass_does_not_imply_external_effect_gate_pass": True,
            "failed_effect_gate_is_preserved_not_overridden": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        load(args.protocol),
        load(args.summary),
        args.run_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
