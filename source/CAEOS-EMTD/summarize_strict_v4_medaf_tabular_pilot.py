from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_medaf_tabular_pilot_protocol import load
from run_strict_v4_medaf_tabular_pilot import (
    REPORT_KEYS,
    SCHEMA as RUN_SCHEMA,
    score_diagnostics,
    selection_is_clean,
)


SCHEMA = "strict_v4_medaf_tabular_pilot_summary_v1"
UNKNOWN_METRICS = (
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)
LOWER_IS_BETTER = {"unknown_fpr95"}


def oriented(value: float, metric: str) -> float:
    return -float(value) if metric in LOWER_IS_BETTER else float(value)


def mean(values: Iterable[float]) -> float:
    array = np.asarray(list(values), dtype=np.float64)
    if array.size == 0:
        raise ValueError("empty MEDAF aggregation")
    return float(array.mean())


def rank_of_candidate(
    values: Dict[str, float],
    candidate: str,
    metric: str,
) -> float:
    target = oriented(values[candidate], metric)
    better = 0
    ties = 0
    for method, value in values.items():
        if method == candidate:
            continue
        score = oriented(value, metric)
        if score > target + 1e-12:
            better += 1
        elif abs(score - target) <= 1e-12:
            ties += 1
    return float(1 + better + 0.5 * ties)


def load_runs(
    design: Dict[str, Any],
    protocol: Dict[str, Any],
    run_root: Path,
) -> Tuple[
    Dict[Tuple[str, str, str], Dict[str, Any]],
    Dict[str, str],
]:
    expected = {
        (suite, scenario, method)
        for suite, scenarios in design["pilot"]["scenario_selection"][
            "scenarios"
        ].items()
        for scenario in scenarios
        for method in design["pilot"]["methods"]
    }
    runs: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    hashes: Dict[str, str] = {}
    for path in sorted(run_root.rglob("run_manifest.json")):
        manifest = load(path)
        if (
            manifest.get("schema_version") != RUN_SCHEMA
            or manifest.get("manifest_sha256") != canonical_hash(manifest)
            or manifest.get("state") != "complete"
            or manifest.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or manifest.get("design_manifest_sha256")
            != design["manifest_sha256"]
        ):
            raise ValueError(f"invalid MEDAF run manifest: {path}")
        task = manifest["task"]
        identity = (
            task["suite"],
            task["scenario"],
            task["method"],
        )
        if identity in runs:
            raise ValueError(f"duplicate MEDAF run: {identity}")
        metrics_path = path.parent / "metrics.json"
        if file_hash(metrics_path) != manifest["metrics_file_sha256"]:
            raise ValueError(f"MEDAF metrics hash mismatch: {identity}")
        metrics = load(metrics_path)
        if not selection_is_clean(metrics):
            raise ValueError(f"MEDAF selection violation: {identity}")
        split_fingerprint = canonical_hash(metrics["split_metadata"])
        if split_fingerprint != manifest["split_fingerprint"]:
            raise ValueError(f"MEDAF split mismatch: {identity}")
        method = identity[2]
        report = metrics.get("reports", {}).get(REPORT_KEYS[method])
        if not isinstance(report, dict):
            raise ValueError(f"MEDAF report missing: {identity}")
        diagnostics = {}
        if method == "medaf_tabular_adapter":
            diagnostics = score_diagnostics(path.parent / "scores.npz")
            if diagnostics != manifest.get("score_diagnostics"):
                raise ValueError(
                    f"MEDAF score diagnostics mismatch: {identity}"
                )
        runs[identity] = {
            "manifest": manifest,
            "report": report,
            "split_fingerprint": split_fingerprint,
            "score_diagnostics": diagnostics,
        }
        hashes["/".join(identity)] = file_hash(path)
    if set(runs) != expected:
        raise ValueError(
            "MEDAF run universe mismatch: "
            f"missing={len(expected-set(runs))} "
            f"extra={len(set(runs)-expected)}"
        )
    return runs, hashes


def summarize(
    design: Dict[str, Any],
    protocol: Dict[str, Any],
    run_root: Path,
) -> Dict[str, Any]:
    if (
        design.get("manifest_sha256") != canonical_hash(design)
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("design_manifest_sha256")
        != design["manifest_sha256"]
    ):
        raise ValueError("invalid MEDAF protocol/design binding")
    runs, manifest_hashes = load_runs(design, protocol, run_root)
    scenarios = design["pilot"]["scenario_selection"]["scenarios"]
    task_records = {}
    gains_by_metric = defaultdict(list)
    ranks = []
    known_degradations = []
    suite_gains = defaultdict(list)
    split_match_count = 0
    nondegenerate_count = 0
    selection_violation_count = 0
    for suite, suite_scenarios in sorted(scenarios.items()):
        for scenario in suite_scenarios:
            task = (suite, scenario)
            records = {
                method: runs[(suite, scenario, method)]
                for method in design["pilot"]["methods"]
            }
            fingerprints = {
                record["split_fingerprint"]
                for record in records.values()
            }
            split_matches = len(fingerprints) == 1
            split_match_count += int(split_matches)
            diagnostics = records["medaf_tabular_adapter"][
                "score_diagnostics"
            ]
            nondegenerate = bool(
                diagnostics["risk_non_degenerate"]
                and diagnostics["gate_non_degenerate"]
            )
            nondegenerate_count += int(nondegenerate)
            selection_clean = all(
                record["manifest"]["known_only_selection_verified"]
                is True
                for record in records.values()
            )
            selection_violation_count += int(not selection_clean)
            reports = {
                method: record["report"]
                for method, record in records.items()
            }
            metric_gains = {}
            metric_ranks = {}
            for metric in UNKNOWN_METRICS:
                medaf_value = float(
                    reports["medaf_tabular_adapter"][metric]
                )
                energy_value = float(reports["mlp_energy"][metric])
                gain = oriented(medaf_value, metric) - oriented(
                    energy_value, metric
                )
                metric_gains[metric] = gain
                gains_by_metric[metric].append(gain)
                suite_gains[suite].append(gain)
                values = {
                    method: float(report[metric])
                    for method, report in reports.items()
                }
                rank = rank_of_candidate(
                    values, "medaf_tabular_adapter", metric
                )
                metric_ranks[metric] = rank
                ranks.append(rank)
            known_degradation = float(
                reports["opendetect"]["known_macro_f1"]
                - reports["medaf_tabular_adapter"]["known_macro_f1"]
            )
            known_degradations.append(known_degradation)
            task_records["/".join(task)] = {
                "split_fingerprint_matches": split_matches,
                "known_only_selection": selection_clean,
                "risk_and_gate_non_degenerate": nondegenerate,
                "oriented_unknown_gain_vs_mlp_energy": metric_gains,
                "unknown_metric_rank": metric_ranks,
                "known_macro_f1_degradation_vs_opendetect": (
                    known_degradation
                ),
            }
    mean_gain_by_metric = {
        metric: mean(values) for metric, values in gains_by_metric.items()
    }
    improved_metric_count = sum(
        value > 0.0 for value in mean_gain_by_metric.values()
    )
    suite_mean_gain = {
        suite: mean(values) for suite, values in suite_gains.items()
    }
    nonnegative_suite_count = sum(
        value >= 0.0 for value in suite_mean_gain.values()
    )
    failed_runs = sum(1 for _ in run_root.rglob("failure.json"))
    gate = design["pilot"]["expansion_gate"]
    checks = {
        "complete_reports": (
            len(runs) == int(gate["complete_reports_required"])
        ),
        "failed_runs": failed_runs <= int(gate["failed_runs_maximum"]),
        "split_fingerprint_match": (
            split_match_count == design["pilot"]["scenario_count"]
        ),
        "unknown_or_test_selection": (
            selection_violation_count
            <= int(gate["unknown_or_test_selection_count_maximum"])
        ),
        "risk_and_gate_non_degenerate": (
            nondegenerate_count == design["pilot"]["scenario_count"]
        ),
        "unknown_metrics_improved_vs_mlp_energy": (
            improved_metric_count
            >= int(
                gate[
                    "unknown_metrics_improved_vs_mlp_energy_minimum"
                ]
            )
        ),
        "mean_oriented_unknown_gain_vs_mlp_energy": (
            mean(
                value
                for values in gains_by_metric.values()
                for value in values
            )
            >= float(
                gate[
                    "mean_oriented_unknown_gain_vs_mlp_energy_minimum"
                ]
            )
        ),
        "mean_unknown_metric_rank": (
            mean(ranks)
            <= float(gate["mean_unknown_metric_rank_maximum"])
        ),
        "known_macro_f1_mean_degradation_vs_opendetect": (
            mean(known_degradations)
            <= float(
                gate[
                    "known_macro_f1_mean_degradation_vs_opendetect_maximum"
                ]
            )
        ),
        "nonnegative_suite_gain_vs_mlp_energy": (
            nonnegative_suite_count
            >= int(
                gate[
                    "nonnegative_suite_gain_vs_mlp_energy_minimum"
                ]
            )
        ),
        "worst_suite_gain_vs_mlp_energy": (
            min(suite_mean_gain.values())
            >= float(
                gate["worst_suite_gain_vs_mlp_energy_minimum"]
            )
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "complete",
        "method": "medaf_tabular_adapter",
        "design_manifest_sha256": design["manifest_sha256"],
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "validation": {
            "run_manifest_count": len(runs),
            "failure_count": failed_runs,
            "split_match_task_count": split_match_count,
            "known_only_selection_violation_count": (
                selection_violation_count
            ),
            "nondegenerate_task_count": nondegenerate_count,
            "run_manifest_file_sha256": manifest_hashes,
            "passes": True,
        },
        "aggregate": {
            "mean_oriented_unknown_gain_vs_mlp_energy_by_metric": (
                mean_gain_by_metric
            ),
            "unknown_metrics_improved_vs_mlp_energy_count": (
                improved_metric_count
            ),
            "mean_oriented_unknown_gain_vs_mlp_energy": mean(
                value
                for values in gains_by_metric.values()
                for value in values
            ),
            "mean_unknown_metric_rank": mean(ranks),
            "known_macro_f1_mean_degradation_vs_opendetect": mean(
                known_degradations
            ),
            "suite_mean_oriented_gain_vs_mlp_energy": suite_mean_gain,
            "nonnegative_suite_gain_count": nonnegative_suite_count,
            "worst_suite_gain_vs_mlp_energy": min(
                suite_mean_gain.values()
            ),
        },
        "task_records": task_records,
        "expansion_checks": checks,
        "decision": {
            "expand_to_full102_confirmation": all(checks.values())
        },
        "claim_boundary": {
            "adapter_is_not_native_medaf_reproduction": True,
            "pilot_is_development_only": True,
            "pilot_success_does_not_establish_sota": True,
            "full102_not_started_by_summarizer": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(
        load(args.design),
        load(args.protocol),
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
