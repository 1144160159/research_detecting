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
from evaluate_strict_v4_comp_confirmation import METRICS, oriented_delta
from evaluate_strict_v4_comp_cross_suite_confirmation import (
    load,
    validate_protocol,
)


METHODS = ("pairwise", "caeos_comp", "opendetect")


def validate_records(
    protocol: dict[str, Any], records: list[dict[str, Any]]
) -> None:
    expected = {
        (task["suite"], task["scenario"], int(task["seed"]))
        for task in protocol["confirmation_universe"]["tasks"]
    }
    observed = []
    for record in records:
        if (
            record.get("schema_version")
            != "strict_v4_comp_cross_suite_task_evaluation_v1"
            or record.get("state")
            != "single_paired_task_evaluation_complete"
            or record.get("manifest_sha256") != canonical_hash(record)
            or record.get("input_evidence", {}).get(
                "protocol_manifest_sha256"
            )
            != protocol["manifest_sha256"]
        ):
            raise ValueError("canonical task evaluation required")
        task = record.get("task", {})
        identity = (task.get("suite"), task.get("scenario"), task.get("seed"))
        evaluation = record.get("evaluation", {})
        if (
            identity
            != (
                evaluation.get("suite"),
                evaluation.get("scenario"),
                evaluation.get("seed"),
            )
            or evaluation.get("group") != "cross_suite"
        ):
            raise ValueError("task evaluation identity drifted")
        for method in METHODS:
            report = evaluation.get(method)
            if not isinstance(report, dict):
                raise ValueError("three complete method reports required")
            for metric, _direction in METRICS:
                value = report.get(metric)
                if (
                    not isinstance(value, (int, float))
                    or not np.isfinite(value)
                ):
                    raise ValueError("finite task metrics required")
        observed.append(identity)
    if (
        len(records) != 306
        or len(set(observed)) != 306
        or set(observed) != expected
    ):
        raise ValueError("exactly 306 frozen task evaluations required")


def scenario_seed_means(
    records: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, dict[str, float]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        row = record["evaluation"]
        grouped[(row["suite"], row["scenario"])].append(row)
    result = {}
    for identity, rows in grouped.items():
        if sorted(int(row["seed"]) for row in rows) != [269, 271, 277]:
            raise ValueError("three frozen seeds required per scenario")
        result[identity] = {
            method: {
                metric: float(
                    np.mean([row[method][metric] for row in rows])
                )
                for metric, _direction in METRICS
            }
            for method in METHODS
        }
    if len(result) != 102:
        raise ValueError("exactly 102 scenario seed means required")
    return result


def paired_summary(
    scenario_means: dict[
        tuple[str, str], dict[str, dict[str, float]]
    ],
    candidate: str,
    reference: str,
) -> dict[str, Any]:
    suites = sorted({suite for suite, _scenario in scenario_means})
    if len(suites) != 7:
        raise ValueError("seven suites required for equal-suite aggregation")
    metrics = {}
    for metric, direction in METRICS:
        by_suite = {}
        scenario_deltas = []
        for suite in suites:
            values = [
                reports
                for (row_suite, _scenario), reports in scenario_means.items()
                if row_suite == suite
            ]
            candidate_mean = float(
                np.mean([value[candidate][metric] for value in values])
            )
            reference_mean = float(
                np.mean([value[reference][metric] for value in values])
            )
            delta = oriented_delta(
                candidate_mean, reference_mean, direction
            )
            by_suite[suite] = {
                "candidate_mean": candidate_mean,
                "reference_mean": reference_mean,
                "oriented_delta": float(delta),
                "scenario_count": len(values),
            }
            scenario_deltas.extend(
                oriented_delta(
                    value[candidate][metric],
                    value[reference][metric],
                    direction,
                )
                for value in values
            )
        suite_deltas = np.asarray(
            [value["oriented_delta"] for value in by_suite.values()],
            dtype=np.float64,
        )
        candidate_equal_suite = float(
            np.mean(
                [value["candidate_mean"] for value in by_suite.values()]
            )
        )
        reference_equal_suite = float(
            np.mean(
                [value["reference_mean"] for value in by_suite.values()]
            )
        )
        metrics[metric] = {
            "direction": direction,
            "candidate_equal_suite_mean": candidate_equal_suite,
            "reference_equal_suite_mean": reference_equal_suite,
            "equal_suite_oriented_delta": float(suite_deltas.mean()),
            "nonnegative_suite_count": int((suite_deltas >= -1e-12).sum()),
            "positive_suite_count": int((suite_deltas > 1e-12).sum()),
            "minimum_suite_oriented_delta": float(suite_deltas.min()),
            "maximum_suite_oriented_delta": float(suite_deltas.max()),
            "minimum_scenario_oriented_delta": float(
                np.min(scenario_deltas)
            ),
            "by_suite": by_suite,
        }
    return {
        "candidate": candidate,
        "reference": reference,
        "suite_count": 7,
        "scenario_count": 102,
        "aggregation": "seed_mean_then_equal_suite_mean",
        "metrics": metrics,
    }


def deterministic_bootstrap(
    scenario_means: dict[
        tuple[str, str], dict[str, dict[str, float]]
    ],
    candidate: str,
    reference: str,
    repetitions: int,
    seed: int,
) -> dict[str, Any]:
    suites = sorted({suite for suite, _scenario in scenario_means})
    scenarios_by_suite = {
        suite: sorted(
            scenario
            for row_suite, scenario in scenario_means
            if row_suite == suite
        )
        for suite in suites
    }
    rng = np.random.default_rng(seed)
    samples = {metric: np.empty(repetitions) for metric, _ in METRICS}
    directions = dict(METRICS)
    for repetition in range(repetitions):
        selected_suites = rng.choice(suites, size=len(suites), replace=True)
        per_suite = {metric: [] for metric, _ in METRICS}
        for suite in selected_suites:
            scenarios = scenarios_by_suite[str(suite)]
            selected = rng.choice(
                scenarios, size=len(scenarios), replace=True
            )
            for metric, _direction in METRICS:
                deltas = [
                    oriented_delta(
                        scenario_means[(str(suite), str(scenario))][candidate][
                            metric
                        ],
                        scenario_means[(str(suite), str(scenario))][reference][
                            metric
                        ],
                        directions[metric],
                    )
                    for scenario in selected
                ]
                per_suite[metric].append(float(np.mean(deltas)))
        for metric, _direction in METRICS:
            samples[metric][repetition] = float(
                np.mean(per_suite[metric])
            )
    return {
        "repetitions": repetitions,
        "seed": seed,
        "blocks": "suite_then_scenario",
        "reporting_only_not_an_admission_gate": True,
        "metrics": {
            metric: {
                "lower_95": float(np.quantile(values, 0.025)),
                "median": float(np.quantile(values, 0.5)),
                "upper_95": float(np.quantile(values, 0.975)),
            }
            for metric, values in samples.items()
        },
    }


def gate_decision(
    protocol: dict[str, Any],
    records: list[dict[str, Any]],
    vs_pairwise: dict[str, Any],
    vs_opendetect: dict[str, Any],
) -> dict[str, Any]:
    gates = protocol["admission_gate"]
    pair_gate = gates["candidate_vs_pairwise"]
    open_gate = gates["candidate_vs_opendetect"]
    pair = vs_pairwise["metrics"]
    open_metrics = vs_opendetect["metrics"]
    known_f1_differences = [
        abs(
            record["evaluation"]["caeos_comp"]["known_macro_f1"]
            - record["evaluation"]["pairwise"]["known_macro_f1"]
        )
        for record in records
    ]
    task_fpr95_deltas = [
        record["evaluation"]["pairwise"]["unknown_fpr95"]
        - record["evaluation"]["caeos_comp"]["unknown_fpr95"]
        for record in records
    ]
    open_nonnegative_minimum = open_gate[
        "per_metric_nonnegative_suite_count_minimum"
    ]
    checks = {
        "pairwise_fpr95_equal_suite_improvement": pair["unknown_fpr95"][
            "equal_suite_oriented_delta"
        ]
        >= pair_gate[
            "equal_suite_mean_fpr95_oriented_improvement_minimum"
        ],
        "pairwise_auroc_nonregression": pair["unknown_auroc"][
            "equal_suite_oriented_delta"
        ]
        >= pair_gate["equal_suite_mean_auroc_oriented_nonregression"],
        "pairwise_aupr_nonregression": pair["unknown_aupr"][
            "equal_suite_oriented_delta"
        ]
        >= pair_gate["equal_suite_mean_aupr_oriented_nonregression"],
        "pairwise_oscr_nonregression": pair["oscr"][
            "equal_suite_oriented_delta"
        ]
        >= pair_gate["equal_suite_mean_oscr_oriented_nonregression"],
        "pairwise_known_f1_invariant": max(known_f1_differences)
        <= pair_gate["known_macro_f1_absolute_tolerance"],
        "pairwise_per_task_fpr95_nonregression": min(task_fpr95_deltas)
        >= -pair_gate["per_task_fpr95_regression_tolerance"],
        "pairwise_fpr95_suite_breadth": pair["unknown_fpr95"][
            "positive_suite_count"
        ]
        >= pair_gate["suite_fpr95_positive_count_minimum"],
        "pairwise_worst_suite_fpr95_nonregression": pair["unknown_fpr95"][
            "minimum_suite_oriented_delta"
        ]
        >= -pair_gate["worst_suite_fpr95_oriented_regression_tolerance"],
        "opendetect_fpr95_noninferiority": open_metrics["unknown_fpr95"][
            "equal_suite_oriented_delta"
        ]
        >= -open_gate["equal_suite_mean_fpr95_noninferiority_margin"],
        "opendetect_auroc_nonregression": open_metrics["unknown_auroc"][
            "equal_suite_oriented_delta"
        ]
        >= open_gate["equal_suite_mean_auroc_oriented_nonregression"],
        "opendetect_aupr_nonregression": open_metrics["unknown_aupr"][
            "equal_suite_oriented_delta"
        ]
        >= open_gate["equal_suite_mean_aupr_oriented_nonregression"],
        "opendetect_oscr_nonregression": open_metrics["oscr"][
            "equal_suite_oriented_delta"
        ]
        >= open_gate["equal_suite_mean_oscr_oriented_nonregression"],
        "opendetect_known_f1_nonregression": open_metrics[
            "known_macro_f1"
        ]["equal_suite_oriented_delta"]
        >= open_gate["equal_suite_mean_known_f1_oriented_nonregression"],
        "opendetect_suite_breadth_all_metrics": all(
            metric["nonnegative_suite_count"] >= open_nonnegative_minimum
            for metric in open_metrics.values()
        ),
    }
    return {
        "passes": all(checks.values()),
        "checks": checks,
        "all_checks_required": True,
        "positive_action": (
            "caeos_comp_becomes_provisional_accuracy_incumbent"
        ),
        "negative_action": "retain_pairwise_incumbent",
    }


def build_summary(
    *,
    protocol: dict[str, Any],
    records: list[dict[str, Any]],
    task_record_sha256: dict[str, str],
    protocol_file_sha256: str,
    summarizer_sha256: str,
) -> dict[str, Any]:
    validate_protocol(protocol, check_implementation=False)
    validate_records(protocol, records)
    means = scenario_seed_means(records)
    vs_pairwise = paired_summary(means, "caeos_comp", "pairwise")
    vs_opendetect = paired_summary(means, "caeos_comp", "opendetect")
    repetitions = int(
        protocol["primary_statistics"]["bootstrap_repetitions"]
    )
    bootstrap_seed = int(protocol["manifest_sha256"][:8], 16)
    result: dict[str, Any] = {
        "schema_version": (
            "strict_v4_comp_cross_suite_confirmation_summary_v1"
        ),
        "state": "cross_suite_confirmation_summary_complete",
        "validation": {
            "passes": True,
            "task_record_count": len(records),
            "scenario_count": len(means),
            "suite_count": 7,
            "seeds": [269, 271, 277],
            "duplicate_task_count": 0,
            "partial_metrics_aggregated": False,
        },
        "candidate_vs_pairwise": vs_pairwise,
        "candidate_vs_opendetect": vs_opendetect,
        "bootstrap_reporting": {
            "candidate_vs_pairwise": deterministic_bootstrap(
                means,
                "caeos_comp",
                "pairwise",
                repetitions,
                bootstrap_seed,
            ),
            "candidate_vs_opendetect": deterministic_bootstrap(
                means,
                "caeos_comp",
                "opendetect",
                repetitions,
                bootstrap_seed + 1,
            ),
        },
        "decision": gate_decision(
            protocol, records, vs_pairwise, vs_opendetect
        ),
        "input_evidence": {
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "protocol_file_sha256": protocol_file_sha256,
            "task_record_sha256": dict(sorted(task_record_sha256.items())),
        },
        "implementation_sha256": {
            "summarize_strict_v4_comp_cross_suite_confirmation.py": (
                summarizer_sha256
            )
        },
        "claim_boundary": {
            "summary_requires_independent_audit_before_selection": True,
            "summary_pass_does_not_authorize_universal_sota": True,
            "external_malicious_parrot_deployment_and_efficiency_still_required": True,
            "no_dataset_metric_or_evidence_splicing": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_comp_cross_suite_confirmation_v1/"
            "execution_protocol.json"
        ),
    )
    parser.add_argument(
        "--task-root",
        type=Path,
        default=Path(
            "results/strict_v4_comp_cross_suite_confirmation_v1/tasks"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_comp_cross_suite_confirmation_v1/summary.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol_path = resolve(args.protocol)
    task_root = resolve(args.task_root)
    output_path = resolve(args.output)
    if not protocol_path.is_file():
        if output_path.exists():
            raise ValueError("pending protocol must not retain a summary")
        print("state=pending_execution_protocol")
        return
    protocol = load(protocol_path)
    validate_protocol(protocol)
    paths = sorted(task_root.rglob("*.json")) if task_root.is_dir() else []
    if len(paths) != 306:
        if output_path.exists():
            raise ValueError("partial tasks must not retain a summary")
        print(f"state=pending_tasks_{len(paths):03d}_of_306")
        return
    records = [load(path) for path in paths]
    summarizer_path = Path(__file__).resolve()
    summary = build_summary(
        protocol=protocol,
        records=records,
        task_record_sha256={
            str(path.relative_to(root)): file_hash(path) for path in paths
        },
        protocol_file_sha256=file_hash(protocol_path),
        summarizer_sha256=file_hash(summarizer_path),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        existing = load(output_path)
        if existing != summary:
            raise ValueError("existing summary is immutable")
    else:
        temporary = output_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output_path)
    print(json.dumps(summary["decision"], indent=2, sort_keys=True))
    print(f"manifest_sha256={summary['manifest_sha256']}")
    print(f"file_sha256={file_hash(output_path)}")


if __name__ == "__main__":
    main()
