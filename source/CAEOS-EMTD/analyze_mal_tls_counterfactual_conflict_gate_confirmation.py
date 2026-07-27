from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash


OPEN_METRICS = ("unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr")


def oriented_gain(candidate: float, reference: float, metric: str) -> float:
    return reference - candidate if metric == "unknown_fpr95" else candidate - reference


def bootstrap_summary(values: list[float], seed: int, repetitions: int) -> dict[str, Any]:
    array = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    means = array[rng.integers(0, len(array), size=(repetitions, len(array)))].mean(axis=1)
    return {
        "n": len(values),
        "mean": float(array.mean()),
        "bootstrap_95ci": [
            float(np.quantile(means, 0.025)),
            float(np.quantile(means, 0.975)),
        ],
    }


def analyze(protocol: dict[str, Any], run_root: Path) -> dict[str, Any]:
    if protocol.get("schema_version") != (
        "mal_tls_counterfactual_conflict_gate_confirmation_protocol_v1"
    ):
        raise ValueError("unexpected counterfactual confirmation protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("counterfactual confirmation protocol SHA mismatch")
    reference_method = protocol["reference"]
    candidate_method = protocol["candidate"]
    seeds = protocol["training"]["confirmation_seeds"]
    invariant_names = protocol["hard_invariants"]["invariant_metrics"]
    tolerance = float(
        protocol["hard_invariants"]["distance_and_conflict_metric_absolute_tolerance"]
    )
    frozen_training = protocol["known_only_counterfactual_training"]
    blocks = []
    for scenario in protocol["dataset"]["scenarios"]:
        for seed in seeds:
            loaded = {}
            for role, method in (
                ("reference", reference_method),
                ("candidate", candidate_method),
            ):
                root = run_root / method["encoder_profile"] / f"{scenario}_seed{seed}"
                metrics = json.loads((root / "metrics.json").read_text(encoding="utf-8"))
                metadata = json.loads((root / "data_metadata.json").read_text(encoding="utf-8"))
                if metrics.get("encoder_profile") != method["encoder_profile"]:
                    raise ValueError(f"profile mismatch: {root}")
                if metrics.get("encoder_kinds") != method["encoder_kinds"]:
                    raise ValueError(f"encoder mismatch: {root}")
                if metrics.get("evidence_adapter_kinds") != method["evidence_adapter_kinds"]:
                    raise ValueError(f"adapter mismatch: {root}")
                if metrics.get("evidence_temperature_calibration") is not True:
                    raise ValueError(f"temperature calibration missing: {root}")
                loaded[role] = (metrics, metadata, root)
            reference, reference_meta, _ = loaded["reference"]
            candidate, candidate_meta, candidate_root = loaded["candidate"]
            expected_settings = {
                "known_only_consistency_weight": frozen_training["consistency_weight"],
                "known_only_counterfactual_weight": frozen_training[
                    "counterfactual_weight"
                ],
                "counterfactual_margin": frozen_training["uncertainty_margin"],
                "counterfactual_gate_max_log_attenuation": frozen_training[
                    "maximum_absolute_log_attenuation"
                ],
                "prefer_last_epoch_on_known_f1_tie": True,
            }
            for name, expected in expected_settings.items():
                if candidate.get(name) != expected:
                    raise ValueError(f"frozen setting mismatch: {scenario}/seed{seed}/{name}")
            reference_fp = reference_meta["split_metadata"]["split_fingerprint"]["combined"]
            candidate_fp = candidate_meta["split_metadata"]["split_fingerprint"]["combined"]
            if not reference_fp or reference_fp != candidate_fp:
                raise ValueError(f"paired split mismatch: {scenario}/seed{seed}")
            audit = json.loads(
                (candidate_root / "base_equivalence.json").read_text(encoding="utf-8")
            )
            diagnostic = candidate.get("known_validation_counterfactual_gate", {})
            if diagnostic.get("unknown_or_test_labels_used") is not False:
                raise ValueError(f"diagnostic leakage declaration failed: {scenario}/seed{seed}")
            if int(diagnostic.get("valid_samples", 0)) <= 0:
                raise ValueError(f"counterfactual diagnostic is empty: {scenario}/seed{seed}")
            differences = {
                name: float(abs(candidate[name] - reference[name])) for name in invariant_names
            }
            blocks.append(
                {
                    "scenario": scenario,
                    "seed": seed,
                    "oriented_gains": {
                        name: oriented_gain(candidate[name], reference[name], name)
                        for name in OPEN_METRICS
                    },
                    "known_macro_f1_gain": float(
                        candidate["known_macro_f1"] - reference["known_macro_f1"]
                    ),
                    "ece_gain": float(reference["ece"] - candidate["ece"]),
                    "counterfactual_diagnostic": diagnostic,
                    "geometry_invariants_pass": audit.get("passes") is True
                    and max(differences.values()) <= tolerance,
                    "invariant_absolute_differences": differences,
                }
            )
    if len(blocks) * 2 != int(protocol["training"]["expected_confirmation_runs"]):
        raise ValueError("counterfactual confirmation matrix is incomplete")
    gate = protocol["confirmatory_analysis"]
    repetitions = int(gate["bootstrap_repetitions"])
    base_seed = int(gate["bootstrap_seed"])
    metrics = {
        name: bootstrap_summary(
            [block["oriented_gains"][name] for block in blocks],
            base_seed + index,
            repetitions,
        )
        for index, name in enumerate(OPEN_METRICS)
    }
    scenario_means = {
        scenario: {
            name: float(
                np.mean(
                    [
                        block["oriented_gains"][name]
                        for block in blocks
                        if block["scenario"] == scenario
                    ]
                )
            )
            for name in OPEN_METRICS
        }
        for scenario in protocol["dataset"]["scenarios"]
    }
    seed_means = {
        str(seed): {
            name: float(
                np.mean(
                    [
                        block["oriented_gains"][name]
                        for block in blocks
                        if block["seed"] == seed
                    ]
                )
            )
            for name in OPEN_METRICS
        }
        for seed in seeds
    }
    minimum_scenario_mean = min(
        value for scenario in scenario_means.values() for value in scenario.values()
    )
    nonregressing_scenarios = sum(
        all(value >= 0.0 for value in scenario.values())
        for scenario in scenario_means.values()
    )
    mean_known = float(np.mean([block["known_macro_f1_gain"] for block in blocks]))
    mean_ece = float(np.mean([block["ece_gain"] for block in blocks]))
    mean_uncertainty_gain = float(
        np.mean(
            [
                block["counterfactual_diagnostic"][
                    "mean_counterfactual_uncertainty_gain"
                ]
                for block in blocks
            ]
        )
    )
    mean_margin_fraction = float(
        np.mean(
            [
                block["counterfactual_diagnostic"]["margin_satisfaction_fraction"]
                for block in blocks
            ]
        )
    )
    mean_attenuation_gain = float(
        np.mean(
            [
                block["counterfactual_diagnostic"][
                    "mean_counterfactual_log_attenuation_gain"
                ]
                for block in blocks
            ]
        )
    )
    checks = {
        "all_four_mean_oriented_gains_positive": all(
            summary["mean"] > 0.0 for summary in metrics.values()
        ),
        "all_four_bootstrap_95ci_lower_bounds_positive": all(
            summary["bootstrap_95ci"][0] > 0.0 for summary in metrics.values()
        ),
        "minimum_scenario_mean_metric_gain": minimum_scenario_mean
        >= float(gate["minimum_scenario_mean_metric_gain"]),
        "minimum_all_metric_nonregressing_scenarios": nonregressing_scenarios
        >= int(gate["minimum_all_metric_nonregressing_scenarios"]),
        "every_seed_all_four_mean_oriented_gains_positive": all(
            all(value > 0.0 for value in summary.values())
            for summary in seed_means.values()
        ),
        "minimum_mean_known_macro_f1_gain": mean_known
        >= float(gate["minimum_mean_known_macro_f1_gain"]),
        "minimum_mean_ece_gain": mean_ece >= float(gate["minimum_mean_ece_gain"]),
        "minimum_mean_known_validation_counterfactual_uncertainty_gain": (
            mean_uncertainty_gain
            >= float(gate["minimum_mean_known_validation_counterfactual_uncertainty_gain"])
        ),
        "minimum_mean_margin_satisfaction_fraction": mean_margin_fraction
        >= float(gate["minimum_mean_margin_satisfaction_fraction"]),
        "positive_mean_counterfactual_log_attenuation_gain": mean_attenuation_gain > 0.0,
        "all_geometry_invariants_pass": all(
            block["geometry_invariants_pass"] for block in blocks
        ),
    }
    passes = all(checks.values())
    return {
        "schema_version": "mal_tls_counterfactual_conflict_gate_confirmation_analysis_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "paired_unit_count": len(blocks),
        "metrics": metrics,
        "scenario_mean_oriented_gains": scenario_means,
        "seed_mean_oriented_gains": seed_means,
        "minimum_scenario_mean_metric_gain": float(minimum_scenario_mean),
        "all_metric_nonregressing_scenario_count": int(nonregressing_scenarios),
        "mean_known_macro_f1_gain": mean_known,
        "mean_ece_gain": mean_ece,
        "mean_known_validation_counterfactual_uncertainty_gain": mean_uncertainty_gain,
        "mean_margin_satisfaction_fraction": mean_margin_fraction,
        "mean_counterfactual_log_attenuation_gain": mean_attenuation_gain,
        "checks": checks,
        "passes": passes,
        "decision": (
            "promote_counterfactual_conflict_gate_as_confirmed_mal_tls_component"
            if passes
            else "retain_caeos_pairwise_and_reject_counterfactual_gate_after_confirmation"
        ),
        "blocks": blocks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(json.loads(args.protocol.read_text(encoding="utf-8")), args.run_root)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
