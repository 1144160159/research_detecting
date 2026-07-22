from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


SCENARIOS = {
    "cic_iot2023": ["ddos_udp_flood", "mirai_greeth_flood"],
    "cic_ton_iot": ["ddos", "scanning"],
    "cicids2017": ["web_bruteforce", "web_xss"],
    "edge_iiot": ["ransomware", "uploading"],
    "nf_cse": ["ddos_hoic", "sql_injection"],
    "nf_unsw": ["dos", "reconnaissance"],
    "ustc_tfc2016": ["cridex", "tinba"],
}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_manifest(project_root: Path, source_root: Path) -> list[dict[str, Any]]:
    records = []
    for suite, scenarios in SCENARIOS.items():
        for scenario in scenarios:
            run_root = source_root / suite / f"{scenario}_seed7"
            files = {
                name: run_root / name
                for name in ("metrics.json", "scores.npz", "evidence_package.npz")
            }
            missing = [str(path) for path in files.values() if not path.is_file()]
            if missing:
                raise FileNotFoundError(f"missing source evidence: {missing}")
            metrics = json.loads(files["metrics.json"].read_text(encoding="utf-8"))
            if metrics.get("seed") != 7:
                raise ValueError("source evidence is not the frozen seed7 run")
            records.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "seed": 7,
                    "run_root": str(run_root.relative_to(project_root)).replace("\\", "/"),
                    "selected_risk": metrics["selected_risk"],
                    "sha256": {name: file_hash(path) for name, path in files.items()},
                }
            )
    return records


def create_protocol(
    *,
    inputs: list[dict[str, Any]],
    implementation_sha256: dict[str, str],
    observed_metrics: int,
) -> dict[str, Any]:
    if observed_metrics != 0:
        raise ValueError("conflict-topology copula protocol must freeze before results")
    if len(inputs) != 14:
        raise ValueError("conflict-topology copula pilot requires 14 source runs")
    expected = {(suite, scenario) for suite, values in SCENARIOS.items() for scenario in values}
    observed = {(record["suite"], record["scenario"]) for record in inputs}
    if observed != expected:
        raise ValueError("conflict-topology copula source scenario set is incomplete")
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_conflict_topology_copula_protocol_v1",
        "status": "frozen_before_pilot",
        "paper_incumbent": "caeos_pairwise",
        "candidate": {
            "name": "caeos_conflict_topology_copula",
            "hypothesis": (
                "unknown traffic perturbs the joint topology of modality disagreement, "
                "reliability and global-versus-view consensus even when every marginal "
                "tail component remains individually plausible"
            ),
            "feature_names": [
                "reliability_weighted_view_js",
                "maximum_view_to_consensus_js",
                "pairwise_conflict_laplacian_radius",
                "conflict_reliability_coupling",
                "global_to_view_fused_js",
            ],
            "joint_model": "known_validation_empirical_gaussian_copula_ledoit_wolf",
            "risk_blend": "0.75 * frozen_pairwise_risk + 0.25 * topology_tail_risk",
            "prediction_policy": "frozen_pairwise_prediction_unchanged",
        },
        "known_only_fit": {
            "source": "known_validation_only",
            "stratified_fit_calibration_fraction": 0.4,
            "split_seed": 229,
            "known_rejection_quantile": 0.95,
            "unknown_or_test_labels_used_for_fit_threshold_or_selection": False,
        },
        "pilot": {
            "source_seed": 7,
            "scenario_count": 14,
            "suite_count": 7,
            "inputs": inputs,
            "test_labels_used_for_development_metrics_only": True,
            "gate": {
                "all_four_overall_oriented_means_strictly_positive": True,
                "minimum_suite_metric_gain": -0.01,
                "minimum_fully_nonregressing_suite_count": 6,
                "minimum_positive_scenario_four_metric_mean_count": 8,
                "prediction_array_equal_in_all_scenarios": True,
                "known_macro_f1_absolute_tolerance": 1e-12,
            },
        },
        "reserved_confirmation": {
            "seeds": [233, 239, 241],
            "scenario_scope": "all_102_strict_v4_scenarios",
            "expected_run_count": 306,
            "must_freeze_only_after_positive_pilot": True,
            "replacement_requires_bootstrap_holm_suite_and_efficiency_gates": True,
        },
        "novelty_boundary": {
            "not_another_encoder_candidate": True,
            "not_a_marginal_tail_reweighting": True,
            "does_not_use_unknown_labels_to_fit_copula": True,
            "development_success_does_not_establish_sota": True,
        },
        "metrics_observed_at_freeze": observed_metrics,
        "implementation_sha256": implementation_sha256,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("runs/strict_v4_full103_pairwise_caeos_seed7"),
    )
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    source_root = (
        args.source_root
        if args.source_root.is_absolute()
        else project_root / args.source_root
    ).resolve()
    names = (
        "caeos/conflict_topology_copula.py",
        "evaluate_conflict_topology_copula.py",
        "run_strict_v4_conflict_topology_copula_matrix.py",
        "summarize_strict_v4_conflict_topology_copula.py",
        "scripts/run_strict_v4_conflict_topology_copula_pilot.sh",
    )
    protocol = create_protocol(
        inputs=input_manifest(project_root, source_root),
        implementation_sha256={name: file_hash(project_root / name) for name in names},
        observed_metrics=(
            len(list(args.run_root.rglob("metrics.json"))) if args.run_root.exists() else 0
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
