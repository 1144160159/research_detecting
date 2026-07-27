from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_krc_external_malicious import slug
from summarize_strict_v4_mdr_external_malicious import (
    METRICS,
    aggregate,
    metric_report,
    split_integrity,
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def candidate_report(
    metrics: Dict[str, Any], report_name: str
) -> Dict[str, float]:
    if (
        metrics.get("schema_version")
        != "strict_v4_krc_external_runtime_metrics_v1"
        or metrics.get("manifest_sha256") != canonical_hash(metrics)
        or metrics.get("algorithm") != "krc_csr_caeos_v1"
        or metrics.get("state") != "complete"
    ):
        raise ValueError("unexpected KRC external metrics")
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
        or diagnostics.get("external_parameters_reselected") is not False
        or any(
            routing.get(name) is not True
            for name in (
                "prediction_exactly_pairwise_all_rows",
                "probability_exactly_pairwise_all_rows",
                "risk_monotone_not_below_pairwise",
                "inactive_risk_exactly_pairwise",
                "disabled_risk_exactly_pairwise_all_rows",
            )
        )
    ):
        raise ValueError("KRC external leakage or routing gate failed")
    report_value = metrics.get("reports", {}).get(report_name)
    if not isinstance(report_value, dict):
        raise ValueError(f"KRC external report missing: {report_name}")
    return {
        name: float(report_value[name])
        for name in (*METRICS, "known_macro_f1")
    }


def load_bound_metrics(
    output: Path,
    protocol: Dict[str, Any],
    task: Dict[str, Any],
    method: str,
) -> Dict[str, Any]:
    metrics_path = output / "metrics.json"
    provenance_path = output / "provenance.json"
    metrics = load(metrics_path)
    provenance = load(provenance_path)
    if (
        provenance.get("manifest_sha256") != canonical_hash(provenance)
        or provenance.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or provenance.get("metrics_sha256") != file_hash(metrics_path)
        or provenance.get("method") != method
        or provenance.get("dataset") != task["dataset"]
        or provenance.get("unknown_attack_family")
        != task["unknown_attack_family"]
        or int(provenance.get("training_seed", -1))
        != int(task["training_seed"])
        or provenance.get("csv_sha256") != task["csv_sha256"]
        or provenance.get("sidecar_file_sha256")
        != task["sidecar_file_sha256"]
        or provenance.get("config_sha256") != task["config_sha256"]
        or provenance.get(
            "unknown_or_test_metrics_used_for_configuration"
        )
        is not False
    ):
        raise ValueError(f"KRC external provenance failed: {output}")
    return metrics


def comparator_checks(
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


def summarize(
    protocol: Dict[str, Any], run_root: Path
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_external_malicious_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
        or not (run_root / "execution_complete").is_file()
    ):
        raise ValueError("complete admitted KRC external execution required")

    pairwise_records = []
    opendetect_records = []
    metric_files = []
    for task in protocol["tasks"]:
        block = (
            run_root
            / task["dataset"]
            / (
                f"{slug(task['unknown_attack_family'])}_"
                f"seed{task['training_seed']}"
            )
        )
        candidate_metrics = load_bound_metrics(
            block / "krc_csr_caeos_v1",
            protocol,
            task,
            "krc_csr_caeos_v1",
        )
        opendetect_metrics = load_bound_metrics(
            block / "opendetect",
            protocol,
            task,
            "opendetect",
        )
        if (
            not split_integrity(candidate_metrics)
            or not split_integrity(opendetect_metrics)
            or candidate_metrics["split_metadata"]["split_fingerprint"]
            != opendetect_metrics["split_metadata"]["split_fingerprint"]
        ):
            raise ValueError(
                f"KRC external split integrity failed: {block}"
            )
        candidate = candidate_report(candidate_metrics, "candidate")
        pairwise = candidate_report(
            candidate_metrics, "embedded_pairwise"
        )
        opendetect = metric_report(opendetect_metrics, "opendetect")
        base = {
            "dataset": task["dataset"],
            "unknown_attack_family": task["unknown_attack_family"],
            "seed": int(task["training_seed"]),
            "candidate": candidate,
        }
        pairwise_records.append({**base, "comparator": pairwise})
        opendetect_records.append({**base, "comparator": opendetect})
        metric_files.extend(
            [
                block / "krc_csr_caeos_v1" / "metrics.json",
                block / "opendetect" / "metrics.json",
            ]
        )

    statistics = protocol["statistics"]
    repetitions = int(statistics["bootstrap_repetitions"])
    seed = int(statistics["bootstrap_seed"])
    aggregations = {
        "embedded_pairwise": aggregate(
            pairwise_records,
            repetitions=repetitions,
            bootstrap_seed=seed,
        ),
        "opendetect": aggregate(
            opendetect_records,
            repetitions=repetitions,
            bootstrap_seed=seed + 1000,
        ),
    }
    gates = protocol["confirmation_gate"]["against_each_comparator"]
    checks_by_comparator = {
        name: comparator_checks(aggregation, gates)
        for name, aggregation in aggregations.items()
    }
    expected = int(
        protocol["task_counts"]["total_scenarios_per_algorithm"]
    )
    failures = list(run_root.rglob("failure.json"))
    coverage_checks = {
        "coverage_complete_and_failure_count_zero": (
            len(pairwise_records) == expected
            and len(opendetect_records) == expected
            and len(metric_files) == 2 * expected
            and len(failures) == 0
        ),
        "all_metric_files_remain_hash_bound": all(
            path.is_file() for path in metric_files
        ),
        "unknown_or_test_labels_excluded_from_fit_selection_threshold_"
        "and_routing": True,
        "both_comparators_pass_without_splicing": all(
            all(checks.values())
            for checks in checks_by_comparator.values()
        ),
    }
    passes = all(coverage_checks.values())
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_external_malicious_summary_v1"
        ),
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "algorithm": "krc_csr_caeos_v1",
        "comparators": ["embedded_pairwise", "opendetect"],
        "scenario_count": expected,
        "formal_metric_report_count": 3 * expected,
        "failure_count": len(failures),
        "metric_file_sha256": {
            path.relative_to(run_root).as_posix(): file_hash(path)
            for path in sorted(metric_files)
        },
        "aggregations": aggregations,
        "checks_by_comparator": checks_by_comparator,
        "validation": {
            "checks": coverage_checks,
            "passes": passes,
        },
        "fresh_two_dataset_external_malicious_confirmation_passes": passes,
        "selection": (
            "krc_csr_caeos_v1" if passes else "caeos_pairwise"
        ),
        "claim_boundary": {
            **protocol["claim_boundary"],
            "summary_integrity_does_not_override_failed_effect_gate": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(load(args.protocol), args.run_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
