from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_postselection_corruption import build_tasks, task_key
from summarize_strict_v4_postselection_corruption import (
    METRICS,
    degradation,
    extract_metrics,
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def wrapper_record_hash(wrapper: dict[str, Any]) -> str:
    body = dict(wrapper)
    body.pop("record_sha256", None)
    return canonical_hash(body)


def collect_values(
    *,
    protocol: dict[str, Any],
    base: dict[str, Any],
    coverage: dict[str, Any],
    project: Path,
    run_root: Path,
) -> dict[str, dict[str, dict[str, list[float]]]]:
    tasks = build_tasks(base, coverage)
    values: dict[str, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {metric: [] for metric in METRICS})
    )
    observed = 0
    for task in tasks:
        if task.tier != "full102":
            continue
        wrapper_path = run_root / task_key(task) / "corruption_metrics.json"
        wrapper = load(wrapper_path)
        if (
            wrapper.get("schema_version")
            != "strict_v4_postselection_corruption_run_v1"
            or wrapper.get("record_sha256") != wrapper_record_hash(wrapper)
            or wrapper.get("validation_passes") is not True
            or wrapper.get(
                "unknown_or_test_labels_used_for_generation_fitting_or_selection"
            )
            is not False
            or wrapper.get("task") != task.__dict__
        ):
            raise ValueError(
                f"corruption wrapper validation failed: {wrapper_path}"
            )
        metrics_path = Path(wrapper["metrics_path"])
        clean_path = (
            project
            / base["clean_anchor"]["root"]
            / task.suite
            / f"{task.scenario}_seed7"
            / "metrics.json"
        )
        if (
            file_hash(metrics_path) != wrapper["metrics_sha256"]
            or file_hash(clean_path) != wrapper["clean_metrics_sha256"]
        ):
            raise ValueError(f"metric file SHA mismatch: {wrapper_path}")
        corrupted = extract_metrics(metrics_path)
        clean = extract_metrics(clean_path)
        for metric in METRICS:
            values[task.corruption][task.suite][metric].append(
                degradation(clean, corrupted, metric)
            )
        observed += 1
    if observed != protocol["expected_full102_runs"]:
        raise ValueError("full102 wrapper count mismatch")
    return values


def create_audit(
    *,
    protocol: dict[str, Any],
    base: dict[str, Any],
    coverage: dict[str, Any],
    summary: dict[str, Any],
    values: dict[str, dict[str, dict[str, list[float]]]],
) -> dict[str, Any]:
    require_canonical(
        protocol,
        "strict_v4_postselection_corruption_suite_gate_protocol_v1",
        "suite gate protocol",
    )
    require_canonical(
        base,
        "strict_v4_postselection_corruption_protocol_v1",
        "base corruption protocol",
    )
    require_canonical(
        coverage, "strict_v4_coverage_manifest_v2", "coverage manifest"
    )
    require_canonical(
        summary,
        "strict_v4_postselection_corruption_summary_v1",
        "authority corruption summary",
    )
    if (
        protocol.get("base_protocol_manifest_sha256")
        != base["manifest_sha256"]
        or protocol.get("coverage_manifest_sha256")
        != coverage["manifest_sha256"]
        or summary.get("protocol_manifest_sha256")
        != base["manifest_sha256"]
    ):
        raise ValueError("frozen input manifest binding mismatch")
    validation = summary.get("validation", {})
    if (
        summary.get("status") != "complete"
        or validation.get("expected_runs") != 783
        or validation.get("observed_runs") != 783
        or validation.get("full102_runs") != 510
        or validation.get("passes") is not True
    ):
        raise ValueError("authority corruption summary is incomplete")

    expected_suites = protocol["suite_scenario_counts"]
    expected_families = protocol["corruption_families"]
    reported = protocol["reported_metrics"]
    thresholded = protocol["thresholded_metrics"]
    thresholds = protocol["maximum_mean_degradation"]
    results: dict[str, Any] = {}
    all_threshold_gates: list[bool] = []
    checked_runs = 0
    for family in expected_families:
        family_result: dict[str, Any] = {}
        for suite, expected_count in expected_suites.items():
            metric_result: dict[str, Any] = {}
            for metric in reported:
                observed_values = np.asarray(
                    values[family][suite][metric], dtype=np.float64
                )
                if (
                    observed_values.ndim != 1
                    or observed_values.size != expected_count
                    or not np.all(np.isfinite(observed_values))
                ):
                    raise ValueError(
                        f"invalid values for {family}/{suite}/{metric}"
                    )
                mean = float(observed_values.mean())
                recorded = summary["full102_confirmation"][family][
                    "by_suite_mean_degradation"
                ][suite][metric]
                if not np.isclose(mean, float(recorded), rtol=0.0, atol=1e-12):
                    raise ValueError(
                        f"summary recomputation mismatch: "
                        f"{family}/{suite}/{metric}"
                    )
                item: dict[str, Any] = {
                    "n_scenarios": int(observed_values.size),
                    "mean_degradation": mean,
                    "thresholded": metric in thresholded,
                }
                if metric in thresholded:
                    limit = float(thresholds[metric])
                    item["maximum_mean_degradation"] = limit
                    item["passes"] = mean <= limit
                    all_threshold_gates.append(item["passes"])
                else:
                    item["passes"] = None
                metric_result[metric] = item
            family_result[suite] = metric_result
            checked_runs += expected_count
        results[family] = family_result

    threshold_count = len(all_threshold_gates)
    aggregate_passes = (
        summary.get("confirmatory_gate", {}).get("passes") is True
    )
    passes = (
        aggregate_passes
        and threshold_count
        == protocol["gate_contract"]["threshold_check_count"]
        and all(all_threshold_gates)
    )
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_postselection_corruption_suite_gate_audit_v1"
        ),
        "status": "complete",
        "selected_algorithm_anchor": protocol["selected_algorithm_anchor"],
        "base_protocol_manifest_sha256": base["manifest_sha256"],
        "suite_gate_protocol_manifest_sha256": protocol["manifest_sha256"],
        "authority_summary_manifest_sha256": summary["manifest_sha256"],
        "validation": {
            "expected_full102_runs": 510,
            "observed_full102_runs": checked_runs,
            "suite_count": len(expected_suites),
            "corruption_family_count": len(expected_families),
            "threshold_metric_count": len(thresholded),
            "suite_threshold_checks": threshold_count,
            "descriptive_ece_suite_values": (
                len(expected_suites) * len(expected_families)
            ),
            "all_values_finite_and_summary_recomputed": True,
            "passes": checked_runs == 510 and threshold_count == 175,
        },
        "aggregate_family_gate_passes": aggregate_passes,
        "suite_results": results,
        "all_175_suite_threshold_checks_pass": (
            threshold_count == 175 and all(all_threshold_gates)
        ),
        "passes": passes,
        "claim_boundary": {
            "ece_is_descriptive_without_a_frozen_threshold": True,
            "aggregate_family_means_do_not_substitute_for_suite_gates": True,
            "negative_result_required_if_any_suite_gate_fails": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--suite-protocol", type=Path, required=True)
    parser.add_argument("--base-protocol", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--authority-summary", type=Path, required=True)
    parser.add_argument(
        "--record-hash-compatibility", type=Path, required=True
    )
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.suite_protocol)
    compatibility = load(args.record_hash_compatibility)
    project = args.project_root.resolve()
    require_canonical(
        compatibility,
        (
            "strict_v4_postselection_corruption_suite_gate_"
            "record_hash_compatibility_v1"
        ),
        "record-hash compatibility",
    )
    current_auditor_sha = file_hash(Path(__file__).resolve())
    if (
        file_hash(args.base_protocol)
        != protocol["input_file_sha256"]["base_protocol"]
        or file_hash(args.coverage)
        != protocol["input_file_sha256"]["coverage_manifest"]
        or file_hash(project / "summarize_strict_v4_postselection_corruption.py")
        != protocol["implementation_sha256"]["summarizer"]
        or compatibility.get("suite_gate_protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or compatibility.get("superseded_auditor_sha256")
        != protocol["implementation_sha256"]["suite_auditor"]
        or compatibility.get("corrected_auditor_sha256")
        != current_auditor_sha
    ):
        raise ValueError("frozen file SHA mismatch")
    base, coverage, summary = (
        load(args.base_protocol),
        load(args.coverage),
        load(args.authority_summary),
    )
    values = collect_values(
        protocol=protocol,
        base=base,
        coverage=coverage,
        project=project,
        run_root=args.run_root,
    )
    value = create_audit(
        protocol=protocol,
        base=base,
        coverage=coverage,
        summary=summary,
        values=values,
    )
    if (
        compatibility.get("authority_summary_manifest_sha256")
        != summary["manifest_sha256"]
        or compatibility.get("authority_summary_file_sha256")
        != file_hash(args.authority_summary)
        or compatibility.get(
            "effect_thresholds_or_suite_means_used_for_change"
        )
        is not False
        or not all(compatibility.get("allowed_change", {}).values())
    ):
        raise ValueError("record-hash compatibility binding mismatch")
    value["record_hash_compatibility_manifest_sha256"] = compatibility[
        "manifest_sha256"
    ]
    value["input_file_sha256"] = {
        "suite_protocol": file_hash(args.suite_protocol),
        "base_protocol": file_hash(args.base_protocol),
        "coverage_manifest": file_hash(args.coverage),
        "authority_summary": file_hash(args.authority_summary),
        "record_hash_compatibility": file_hash(
            args.record_hash_compatibility
        ),
    }
    value["audit_implementation_sha256"] = current_auditor_sha
    value["manifest_sha256"] = canonical_hash(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.output.parent / "audit_complete").touch()
    print("PASS" if value["passes"] else "FAIL")


if __name__ == "__main__":
    main()
