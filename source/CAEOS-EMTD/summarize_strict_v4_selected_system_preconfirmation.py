from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_selected_system_preconfirmation_protocol import (
    SCHEMA as PROTOCOL_SCHEMA,
    load,
    require_canonical,
    write_json,
)
from evaluate_strict_v4_comparative_corruption import METRICS
from evaluate_strict_v4_selected_system_preconfirmation import (
    SCHEMA as RECORD_SCHEMA,
)
from run_strict_v4_selected_system_parrot_safety import block_path
from summarize_strict_v4_comparative_corruption import (
    holm_adjust,
    mean_ci,
)


SCHEMA = "strict_v4_selected_system_preconfirmation_summary_v1"
COMPARATIVE_METRICS = (*METRICS, "ece")


def mean_report(reports: list[dict[str, float]]) -> dict[str, float]:
    if not reports:
        raise ValueError("at least one metric report required")
    return {
        metric: float(np.mean([float(report[metric]) for report in reports]))
        for metric in METRICS
    }


def oriented_delta(
    candidate: float, reference: float, metric: str
) -> float:
    delta = float(candidate) - float(reference)
    return -delta if metric == "unknown_fpr95" else delta


def validate_record(
    record: dict[str, Any],
    protocol: dict[str, Any],
    source: dict[str, Any],
) -> None:
    expected_source = {
        "suite": source["suite"],
        "scenario": source["scenario"],
        "training_seed": int(source["training_seed"]),
        "corruption_seed": int(source["corruption_seed"]),
        "source_split_fingerprint": source["source_split_fingerprint"],
    }
    if (
        record.get("schema_version") != RECORD_SCHEMA
        or record.get("manifest_sha256") != canonical_hash(record)
        or record.get("state") != "complete"
        or record.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or record.get("selected_algorithm") != protocol["selected_algorithm"]
        or record.get("source") != expected_source
        or record.get("same_candidate_opendetect_clean_arrays") is not True
        or record.get("same_corrupted_arrays_per_condition") is not True
        or record.get("fresh_candidate_refit_performed") is not True
        or record.get("fresh_opendetect_refit_performed") is not True
        or record.get(
            "mahalanobis_pp_recomputed_from_same_fresh_mlp_run"
        )
        is not True
        or record.get(
            "unknown_or_test_labels_used_for_fitting_selection_or_corruption"
        )
        is not False
    ):
        raise ValueError("invalid preconfirmation task record")
    reports = record.get("classic_main_reports", {})
    if list(reports) != protocol["classic_main_gate"]["methods"]:
        raise ValueError("classic baseline record coverage drifted")
    conditions = record.get("conditions", [])
    if (
        len(conditions) != 5
        or [item.get("family") for item in conditions]
        != protocol["corruption"]["families"]
    ):
        raise ValueError("corruption condition coverage drifted")
    for report in [record["candidate_clean_report"], *reports.values()]:
        if any(
            metric not in report
            or not np.isfinite(float(report[metric]))
            for metric in METRICS
        ):
            raise ValueError("clean metric report is incomplete")
    for condition in conditions:
        for key in (
            "candidate_degradation",
            "opendetect_degradation",
            "candidate_robustness_advantage",
        ):
            values = condition.get(key, {})
            if any(
                metric not in values
                or not np.isfinite(float(values[metric]))
                for metric in COMPARATIVE_METRICS
            ):
                raise ValueError("corruption metric record is incomplete")


def aggregate_clean(
    records: list[dict[str, Any]], protocol: dict[str, Any]
) -> dict[str, Any]:
    methods = protocol["classic_main_gate"]["methods"]
    selective = protocol["selective_sota_claim_ladder"][
        "unknown_detection"
    ]
    selective_metrics = list(selective["metrics"])
    known_tolerance = float(
        selective["known_macro_f1_maximum_degradation"]
    )
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        source = record["source"]
        grouped[(source["suite"], source["scenario"])].append(record)
    scenario_blocks = []
    suite_candidate: dict[str, list[dict[str, float]]] = defaultdict(list)
    suite_methods: dict[
        str, dict[str, list[dict[str, float]]]
    ] = defaultdict(lambda: defaultdict(list))
    scenario_deltas: dict[str, dict[str, list[float]]] = {
        method: {metric: [] for metric in METRICS} for method in methods
    }
    for (suite, scenario), values in sorted(grouped.items()):
        seeds = sorted(int(value["source"]["training_seed"]) for value in values)
        if seeds != protocol["training_seeds"]:
            raise ValueError("clean scenario seed coverage drifted")
        candidate = mean_report(
            [value["candidate_clean_report"] for value in values]
        )
        references = {
            method: mean_report(
                [value["classic_main_reports"][method] for value in values]
            )
            for method in methods
        }
        suite_candidate[suite].append(candidate)
        for method, report in references.items():
            suite_methods[suite][method].append(report)
            for metric in METRICS:
                scenario_deltas[method][metric].append(
                    oriented_delta(candidate[metric], report[metric], metric)
                )
        scenario_blocks.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed_count": 3,
                "candidate": candidate,
                "classic_main": references,
            }
        )
    if len(scenario_blocks) != 102 or len(suite_candidate) != 7:
        raise ValueError("clean scenario or suite coverage drifted")
    by_suite = {}
    for suite in sorted(suite_candidate):
        by_suite[suite] = {
            "scenario_count": len(suite_candidate[suite]),
            "candidate": mean_report(suite_candidate[suite]),
            "classic_main": {
                method: mean_report(suite_methods[suite][method])
                for method in methods
            },
        }
    overall_candidate = mean_report(
        [value["candidate"] for value in by_suite.values()]
    )
    overall_methods = {
        method: mean_report(
            [value["classic_main"][method] for value in by_suite.values()]
        )
        for method in methods
    }
    comparisons = {}
    base_seed = int(protocol["aggregation"]["bootstrap_seed"])
    repetitions = int(protocol["aggregation"]["bootstrap_repetitions"])
    for method_index, method in enumerate(methods):
        metrics = {}
        for metric_index, metric in enumerate(METRICS):
            delta = oriented_delta(
                overall_candidate[metric], overall_methods[method][metric], metric
            )
            inference = mean_ci(
                scenario_deltas[method][metric],
                base_seed + method_index * 100 + metric_index,
                repetitions,
            )
            metrics[metric] = {
                "candidate": overall_candidate[metric],
                "reference": overall_methods[method][metric],
                "oriented_delta": delta,
                "strict_win": delta > 0.0,
                "scenario_block_inference": inference,
            }
        comparisons[method] = {
            "metrics": metrics,
            "strictly_dominates_all_five_metrics": all(
                value["strict_win"] for value in metrics.values()
            ),
            "selective_unknown_detection_gate": {
                "all_three_unknown_metrics_strictly_better": all(
                    metrics[metric]["strict_win"]
                    for metric in selective_metrics
                ),
                "all_three_bootstrap_lower_bounds_strictly_positive": all(
                    metrics[metric]["scenario_block_inference"][
                        "bootstrap_95ci"
                    ][0]
                    > 0.0
                    for metric in selective_metrics
                ),
                "all_seven_suites_nonnegative_on_all_three_metrics": all(
                    oriented_delta(
                        by_suite[suite]["candidate"][metric],
                        by_suite[suite]["classic_main"][method][metric],
                        metric,
                    )
                    >= 0.0
                    for suite in by_suite
                    for metric in selective_metrics
                ),
                "known_macro_f1_within_one_point_overall_and_all_suites": (
                    metrics["known_macro_f1"]["oriented_delta"]
                    >= -known_tolerance
                    and all(
                        oriented_delta(
                            by_suite[suite]["candidate"]["known_macro_f1"],
                            by_suite[suite]["classic_main"][method][
                                "known_macro_f1"
                            ],
                            "known_macro_f1",
                        )
                        >= -known_tolerance
                        for suite in by_suite
                    )
                ),
            },
        }
        selective_checks = comparisons[method][
            "selective_unknown_detection_gate"
        ]
        selective_checks["passes"] = all(selective_checks.values())
    return {
        "scenario_blocks": scenario_blocks,
        "by_suite": by_suite,
        "seven_suite_equal_weight": {
            "candidate": overall_candidate,
            "classic_main": overall_methods,
        },
        "comparisons": comparisons,
        "strict_five_metric_dominance_count": sum(
            value["strictly_dominates_all_five_metrics"]
            for value in comparisons.values()
        ),
        "selective_unknown_detection_sota_comparator_count": sum(
            value["selective_unknown_detection_gate"]["passes"]
            for value in comparisons.values()
        ),
        "selective_unknown_detection_sota_passes": all(
            value["selective_unknown_detection_gate"]["passes"]
            for value in comparisons.values()
        ),
        "passes": all(
            value["strictly_dominates_all_five_metrics"]
            for value in comparisons.values()
        ),
    }


def aggregate_corruption(
    records: list[dict[str, Any]], protocol: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    families = protocol["corruption"]["families"]
    absolute_values: dict[
        str, dict[str, dict[str, dict[int, dict[str, float]]]]
    ] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    comparative_values: dict[
        str, dict[str, dict[str, dict[int, float]]]
    ] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    for record in records:
        source = record["source"]
        key = f"{source['suite']}/{source['scenario']}"
        seed = int(source["training_seed"])
        for condition in record["conditions"]:
            family = condition["family"]
            absolute_values[family][source["suite"]][
                source["scenario"]
            ][seed] = {
                metric: float(condition["candidate_degradation"][metric])
                for metric in METRICS
            }
            for metric in COMPARATIVE_METRICS:
                comparative_values[family][metric][key][seed] = float(
                    condition["candidate_robustness_advantage"][metric]
                )

    thresholds = protocol["corruption"][
        "absolute_maximum_mean_degradation"
    ]
    absolute_by_family = {}
    absolute_checks = []
    for family in families:
        suites = {}
        for suite, scenarios in sorted(absolute_values[family].items()):
            scenario_means = []
            for scenario, seeds in sorted(scenarios.items()):
                if sorted(seeds) != protocol["training_seeds"]:
                    raise ValueError("absolute corruption seed coverage drifted")
                scenario_means.append(
                    {
                        metric: float(
                            np.mean(
                                [value[metric] for value in seeds.values()]
                            )
                        )
                        for metric in METRICS
                    }
                )
            suite_means = mean_report(scenario_means)
            metrics = {}
            for metric in METRICS:
                limit = float(thresholds[metric])
                passes = suite_means[metric] <= limit
                absolute_checks.append(passes)
                metrics[metric] = {
                    "mean_degradation": suite_means[metric],
                    "maximum_mean_degradation": limit,
                    "passes": passes,
                }
            suites[suite] = {
                "scenario_count": len(scenario_means),
                "metrics": metrics,
            }
        if len(suites) != 7:
            raise ValueError("absolute corruption suite coverage drifted")
        absolute_by_family[family] = suites
    absolute = {
        "by_family_and_suite": absolute_by_family,
        "suite_threshold_check_count": len(absolute_checks),
        "all_175_suite_threshold_checks_pass": (
            len(absolute_checks) == 175 and all(absolute_checks)
        ),
        "passes": len(absolute_checks) == 175 and all(absolute_checks),
    }

    base_seed = int(protocol["aggregation"]["bootstrap_seed"])
    repetitions = int(protocol["aggregation"]["bootstrap_repetitions"])
    comparative_by_family = {}
    family_passes = []
    for family_index, family in enumerate(families):
        metric_summaries = {}
        scenario_by_metric: dict[str, dict[str, float]] = {}
        for metric_index, metric in enumerate(COMPARATIVE_METRICS):
            scenario_values = {}
            for key, seeds in comparative_values[family][metric].items():
                if sorted(seeds) != protocol["training_seeds"]:
                    raise ValueError("comparative corruption seed coverage drifted")
                scenario_values[key] = float(np.mean(list(seeds.values())))
            if len(scenario_values) != 102:
                raise ValueError("comparative scenario coverage drifted")
            scenario_by_metric[metric] = scenario_values
            metric_summaries[metric] = mean_ci(
                [scenario_values[key] for key in sorted(scenario_values)],
                base_seed + 1000 + family_index * 100 + metric_index,
                repetitions,
            )
        adjusted = holm_adjust(
            {
                metric: metric_summaries[metric]["wilcoxon_one_sided_p"]
                for metric in COMPARATIVE_METRICS
            }
        )
        for metric in COMPARATIVE_METRICS:
            metric_summaries[metric]["holm_adjusted_p"] = adjusted[metric]
        suites = sorted(
            {key.split("/", 1)[0] for key in scenario_by_metric[METRICS[0]]}
        )
        suite_means = {
            suite: {
                metric: float(
                    np.mean(
                        [
                            value
                            for key, value in scenario_by_metric[metric].items()
                            if key.startswith(f"{suite}/")
                        ]
                    )
                )
                for metric in COMPARATIVE_METRICS
            }
            for suite in suites
        }
        checks = {
            "all_six_metric_mean_advantages_strictly_positive": all(
                metric_summaries[metric]["mean_advantage"] > 0.0
                for metric in COMPARATIVE_METRICS
            ),
            "all_six_metric_bootstrap_lower_bounds_strictly_positive": all(
                metric_summaries[metric]["bootstrap_95ci"][0] > 0.0
                for metric in COMPARATIVE_METRICS
            ),
            "all_six_metric_holm_adjusted_p_below_0_05": all(
                metric_summaries[metric]["holm_adjusted_p"] < 0.05
                for metric in COMPARATIVE_METRICS
            ),
            "all_suite_metric_mean_advantages_nonnegative": all(
                value >= -1e-12
                for metrics in suite_means.values()
                for value in metrics.values()
            ),
        }
        passes = all(checks.values())
        family_passes.append(passes)
        comparative_by_family[family] = {
            "metrics": metric_summaries,
            "suite_mean_advantages": suite_means,
            "checks": checks,
            "passes": passes,
        }
    comparative = {
        "by_family": comparative_by_family,
        "all_five_families_pass": all(family_passes),
        "passes": all(family_passes),
    }
    return absolute, comparative


def summarize_records(
    records: list[dict[str, Any]], protocol: dict[str, Any]
) -> dict[str, Any]:
    require_canonical(protocol, PROTOCOL_SCHEMA, "preconfirmation protocol")
    if len(records) != 306:
        raise ValueError("exactly 306 preconfirmation records required")
    identities = {
        (
            record["source"]["suite"],
            record["source"]["scenario"],
            int(record["source"]["training_seed"]),
        )
        for record in records
    }
    expected = {
        (
            source["suite"],
            source["scenario"],
            int(source["training_seed"]),
        )
        for source in protocol["sources"]
    }
    if identities != expected or len(identities) != 306:
        raise ValueError("preconfirmation record identity coverage drifted")
    clean = aggregate_clean(records, protocol)
    absolute, comparative = aggregate_corruption(records, protocol)
    unknown_selective = bool(
        clean["selective_unknown_detection_sota_passes"]
    )
    robustness_selective = bool(
        absolute["passes"] and comparative["passes"]
    )
    return {
        "validation": {
            "task_record_count": len(records),
            "scenario_count": 102,
            "suite_count": 7,
            "training_seeds": protocol["training_seeds"],
            "paired_corruption_condition_count": len(records) * 5,
            "all_records_canonical_and_bound": True,
            "passes": True,
        },
        "classic_main_gate": clean,
        "absolute_corruption_gate": absolute,
        "comparative_corruption_gate": comparative,
        "selective_sota_claims": {
            "unknown_detection": {
                "scope": "seven_suite_strict_v4_unknown_detection",
                "metrics": protocol["selective_sota_claim_ladder"][
                    "unknown_detection"
                ]["metrics"],
                "comparators": protocol["selective_sota_claim_ladder"][
                    "unknown_detection"
                ]["comparators"],
                "passes": unknown_selective,
            },
            "corruption_robustness_vs_opendetect": {
                "scope": "five_frozen_corruption_families",
                "comparators": ["opendetect"],
                "passes": robustness_selective,
            },
            "any_selective_sota_authorized": (
                unknown_selective or robustness_selective
            ),
            "comprehensive_sota_authorized": bool(
                clean["passes"]
                and absolute["passes"]
                and comparative["passes"]
            ),
        },
    }


def build_summary(
    *,
    protocol: dict[str, Any],
    run_root: Path,
) -> dict[str, Any]:
    records = []
    registry = []
    for source in protocol["sources"]:
        path = block_path(run_root, source) / "preconfirmation.json"
        if not path.is_file():
            raise FileNotFoundError(path)
        record = load(path)
        validate_record(record, protocol, source)
        records.append(record)
        registry.append(
            {
                "suite": source["suite"],
                "scenario": source["scenario"],
                "training_seed": int(source["training_seed"]),
                "record_file_sha256": file_hash(path),
            }
        )
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": protocol["selected_algorithm"],
        **summarize_records(records, protocol),
        "record_file_registry": registry,
        "claim_boundary": protocol["claim_boundary"],
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def render(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Strict-v4 selected-system preconfirmation",
            "",
            f"Selected algorithm: `{summary['selected_algorithm']}`.",
            (
                "Classic seven-baseline strict five-metric gate: "
                f"**{'PASS' if summary['classic_main_gate']['passes'] else 'FAIL'}**."
            ),
            (
                "Absolute five-family suite gate: "
                f"**{'PASS' if summary['absolute_corruption_gate']['passes'] else 'FAIL'}**."
            ),
            (
                "Comparative five-family OpenDetect gate: "
                f"**{'PASS' if summary['comparative_corruption_gate']['passes'] else 'FAIL'}**."
            ),
            (
                "Selective unknown-detection SOTA gate: "
                f"**{'PASS' if summary['selective_sota_claims']['unknown_detection']['passes'] else 'FAIL'}**."
            ),
            (
                "Selective corruption-robustness SOTA gate: "
                f"**{'PASS' if summary['selective_sota_claims']['corruption_robustness_vs_opendetect']['passes'] else 'FAIL'}**."
            ),
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--output-md", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol = load(args.protocol)
    if protocol["implementation_sha256"].get(Path(__file__).name) != file_hash(
        Path(__file__).resolve()
    ):
        raise ValueError("active preconfirmation summarizer SHA drifted")
    value = build_summary(protocol=protocol, run_root=args.run_root.resolve())
    write_json(args.output, value)
    if args.output_md is not None:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        with args.output_md.open(
            "w", encoding="utf-8", newline="\n"
        ) as handle:
            handle.write(render(value))
    print(render(value), end="")


if __name__ == "__main__":
    main()
