from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import wilcoxon

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
    "ece",
)
IMPLEMENTATION_PATHS = {
    "candidate_capture": "capture_pairwise_runtime.py",
    "candidate_runtime": "caeos/pairwise_runtime.py",
    "candidate_trainer": "train_hybrid_open_set.py",
    "comparator_capture": "capture_opendetect_runtime.py",
    "comparator_runtime": "caeos/open_detect_runtime.py",
    "evaluator": "evaluate_strict_v4_comparative_corruption.py",
    "protocol_creator": (
        "create_strict_v4_comparative_corruption_protocol.py"
    ),
    "protocol_revision_creator": (
        "create_strict_v4_comparative_corruption_protocol_v2.py"
    ),
    "runner": "run_strict_v4_comparative_corruption.py",
    "summarizer": "summarize_strict_v4_comparative_corruption.py",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def independent_mean_ci(
    values: list[float], *, seed: int, repetitions: int
) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    if array.shape != (102,) or not np.isfinite(array).all():
        raise ValueError("102 finite scenario values required")
    rng = np.random.default_rng(int(seed))
    indices = rng.integers(
        0, len(array), size=(int(repetitions), len(array))
    )
    sampled = array[indices].mean(axis=1)
    p_value = (
        1.0
        if np.all(np.abs(array) <= 1e-15)
        else float(
            wilcoxon(
                array,
                alternative="greater",
                zero_method="wilcox",
            ).pvalue
        )
    )
    return {
        "n_scenarios": 102,
        "mean_advantage": float(array.mean()),
        "bootstrap_95ci": [
            float(np.quantile(sampled, 0.025)),
            float(np.quantile(sampled, 0.975)),
        ],
        "wilcoxon_one_sided_p": p_value,
        "wins": int(np.count_nonzero(array > 1e-12)),
        "ties": int(np.count_nonzero(np.abs(array) <= 1e-12)),
        "losses": int(np.count_nonzero(array < -1e-12)),
    }


def independent_holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values.items(), key=lambda item: (item[1], item[0]))
    running = 0.0
    adjusted = {}
    total = len(ordered)
    for rank, (name, p_value) in enumerate(ordered):
        running = max(running, (total - rank) * float(p_value))
        adjusted[name] = min(1.0, running)
    return adjusted


def recompute(
    protocol: dict[str, Any], run_root: Path
) -> dict[str, Any]:
    values: dict[str, dict[str, dict[str, dict[int, float]]]] = (
        defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    )
    registry = []
    observed = 0
    expected_families = set(
        protocol["corruption_conditions"]["families"]
    )
    for source in protocol["source_registry"]:
        suite = str(source["suite"])
        scenario = str(source["scenario"])
        seed = int(source["seed"])
        path = (
            run_root
            / "blocks"
            / suite
            / scenario
            / f"seed{seed}"
            / "paired_corruption.json"
        )
        payload = load(path)
        conditions = payload.get("conditions", [])
        if (
            payload.get("schema_version")
            != "strict_v4_comparative_corruption_block_v1"
            or payload.get("manifest_sha256") != canonical_hash(payload)
            or payload.get("protocol_manifest_sha256")
            != protocol["manifest_sha256"]
            or payload.get("suite") != suite
            or payload.get("scenario") != scenario
            or int(payload.get("seed", -1)) != seed
            or payload.get("source_split_fingerprint")
            != source["split_fingerprint"]
            or payload.get("candidate_comparator_input_arrays_equal")
            is not True
            or payload.get(
                "degradation_uses_same_device_runtime_clean_anchors"
            )
            is not True
            or payload.get(
                "unknown_or_test_labels_used_for_fitting_selection_or_"
                "corruption_generation"
            )
            is not False
            or len(conditions) != 5
            or {item.get("family") for item in conditions}
            != expected_families
        ):
            raise ValueError(f"invalid comparative block: {path}")
        registry.append(
            {
                "suite": suite,
                "scenario": scenario,
                "seed": seed,
                "block_file_sha256": file_hash(path),
            }
        )
        scenario_key = f"{suite}/{scenario}"
        for condition in conditions:
            family = str(condition["family"])
            advantage = condition["candidate_robustness_advantage"]
            for metric in METRICS:
                metric_value = float(advantage[metric])
                if (
                    not np.isfinite(metric_value)
                    or seed in values[family][metric][scenario_key]
                ):
                    raise ValueError("invalid or duplicate advantage")
                values[family][metric][scenario_key][seed] = metric_value
            observed += 1
    if len(registry) != 306 or observed != 1530:
        raise ValueError("comparative universe coverage mismatch")

    repetitions = int(
        protocol["statistical_analysis"]["bootstrap_repetitions"]
    )
    base_seed = int(protocol["statistical_analysis"]["bootstrap_seed"])
    by_family = {}
    family_passes = []
    for family_index, family in enumerate(
        protocol["corruption_conditions"]["families"]
    ):
        metric_summaries = {}
        scenario_by_metric = {}
        for metric_index, metric in enumerate(METRICS):
            scenario_values = {}
            for scenario_key, seed_values in values[family][metric].items():
                if sorted(seed_values) != list(protocol["seeds"]):
                    raise ValueError("comparative seed coverage mismatch")
                scenario_values[scenario_key] = float(
                    np.mean(list(seed_values.values()))
                )
            if len(scenario_values) != 102:
                raise ValueError("comparative scenario coverage mismatch")
            scenario_by_metric[metric] = scenario_values
            metric_summaries[metric] = independent_mean_ci(
                [
                    scenario_values[key]
                    for key in sorted(scenario_values)
                ],
                seed=base_seed + family_index * 100 + metric_index,
                repetitions=repetitions,
            )
        adjusted = independent_holm(
            {
                metric: metric_summaries[metric][
                    "wilcoxon_one_sided_p"
                ]
                for metric in METRICS
            }
        )
        for metric in METRICS:
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
                            for key, value in scenario_by_metric[
                                metric
                            ].items()
                            if key.startswith(f"{suite}/")
                        ]
                    )
                )
                for metric in METRICS
            }
            for suite in suites
        }
        checks = {
            "all_six_means_strictly_positive": all(
                metric_summaries[metric]["mean_advantage"] > 0.0
                for metric in METRICS
            ),
            "all_six_bootstrap_lower_bounds_strictly_positive": all(
                metric_summaries[metric]["bootstrap_95ci"][0] > 0.0
                for metric in METRICS
            ),
            "all_six_holm_adjusted_p_below_0_05": all(
                metric_summaries[metric]["holm_adjusted_p"] < 0.05
                for metric in METRICS
            ),
            "all_suite_metric_means_nonnegative": all(
                value >= -1e-12
                for metrics in suite_means.values()
                for value in metrics.values()
            ),
        }
        passes = all(checks.values())
        family_passes.append(passes)
        by_family[family] = {
            "metrics": metric_summaries,
            "suite_mean_advantages": suite_means,
            "checks": checks,
            "passes": passes,
        }
    return {
        "block_file_registry": registry,
        "paired_condition_evaluations": observed,
        "by_family": by_family,
        "comparative_robustness_gate": {
            "all_five_families_pass": all(family_passes),
            "passes": all(family_passes),
        },
    }


def audit(
    *,
    protocol: dict[str, Any],
    summary: dict[str, Any],
    project_root: Path,
    run_root: Path,
) -> dict[str, Any]:
    recomputed = recompute(protocol, run_root)
    expected_hashes = protocol.get("implementation_sha256", {})
    implementation_checks = {
        name: (
            name in expected_hashes
            and (project_root / relative).is_file()
            and file_hash(project_root / relative) == expected_hashes[name]
        )
        for name, relative in IMPLEMENTATION_PATHS.items()
    }
    checks = {
        "protocol_is_canonical": (
            protocol.get("schema_version")
            == "strict_v4_comparative_corruption_protocol_v2"
            and protocol.get("manifest_sha256") == canonical_hash(protocol)
        ),
        "summary_is_canonical": (
            summary.get("schema_version")
            == "strict_v4_comparative_corruption_summary_v1"
            and summary.get("manifest_sha256") == canonical_hash(summary)
        ),
        "summary_binds_protocol": (
            summary.get("protocol_manifest_sha256")
            == protocol.get("manifest_sha256")
        ),
        "all_306_blocks_bound_by_file_hash": (
            len(recomputed["block_file_registry"]) == 306
        ),
        "all_1530_conditions_recomputed": (
            recomputed["paired_condition_evaluations"] == 1530
        ),
        "all_frozen_implementation_hashes_match": all(
            implementation_checks.values()
        ),
        "independent_family_statistics_exact": (
            summary.get("by_family") == recomputed["by_family"]
        ),
        "independent_gate_decision_exact": (
            summary.get("comparative_robustness_gate")
            == recomputed["comparative_robustness_gate"]
        ),
        "negative_result_is_not_upgraded": (
            summary.get("comparative_robustness_gate", {}).get("passes")
            is False
        ),
    }
    value = {
        "schema_version": (
            "strict_v4_comparative_corruption_independent_audit_v1"
        ),
        "protocol_manifest_sha256": protocol.get("manifest_sha256"),
        "summary_manifest_sha256": summary.get("manifest_sha256"),
        "checks": checks,
        "implementation_checks": implementation_checks,
        "block_file_registry": recomputed["block_file_registry"],
        "passes": all(checks.values()),
        "comparative_robustness_gate_passes": (
            all(checks.values())
            and recomputed["comparative_robustness_gate"]["passes"]
        ),
        "claim_boundary": {
            "audit_pass_is_integrity_not_positive_effect": True,
            "formal_negative_result_is_preserved": True,
            "no_metric_family_suite_or_component_splicing": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(
        protocol=load(args.protocol),
        summary=load(args.summary),
        project_root=args.project_root.resolve(),
        run_root=args.run_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
