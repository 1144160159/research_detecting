from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from create_strict_v4_external_training_pilot_protocol import SELECTED_SCENARIOS


IMPLEMENTATIONS = (
    "caeos/vos.py",
    "train_vos_open_set.py",
    "run_strict_v4_vos_matrix.py",
    "summarize_strict_v4_vos_pilot.py",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def source_record(
    mlp_root: Path, comparator_root: Path, suite: str, scenario: str
) -> dict[str, Any]:
    mlp_path = mlp_root / suite / f"{scenario}_seed7_mlp" / "metrics.json"
    comparator_path = (
        comparator_root / suite / f"{scenario}_seed7_opendetect" / "metrics.json"
    )
    if not mlp_path.is_file() or not comparator_path.is_file():
        raise FileNotFoundError(f"VOS source baseline is missing: {suite}/{scenario}")
    mlp = load_json(mlp_path)
    comparator = load_json(comparator_path)
    mlp_fingerprint = mlp["split_metadata"]["split_fingerprint"]["combined"]
    comparator_fingerprint = comparator["split_metadata"]["split_fingerprint"]["combined"]
    if mlp_fingerprint != comparator_fingerprint:
        raise ValueError(f"VOS source split mismatch: {suite}/{scenario}")
    if int(mlp.get("seed", -1)) != 7 or int(comparator.get("seed", -1)) != 7:
        raise ValueError(f"VOS source seed mismatch: {suite}/{scenario}")
    if mlp.get("model") != "mlp" or "energy" not in mlp.get("reports", {}):
        raise ValueError(f"VOS MLP energy reference is missing: {suite}/{scenario}")
    if comparator.get("model") != "opendetect" or set(comparator.get("reports", {})) != {
        "opendetect"
    }:
        raise ValueError(f"VOS comparator identity mismatch: {suite}/{scenario}")
    for payload, label in ((mlp, "MLP"), (comparator, "OpenDetect")):
        if payload.get("selection_evidence", {}).get(
            "unknown_or_test_labels_used_for_fitting_or_selection"
        ) is not False:
            raise ValueError(f"VOS {label} source leakage declaration failed")
    arguments = comparator["arguments"]
    return {
        "suite": suite,
        "scenario": scenario,
        "seed": 7,
        "split_fingerprint": mlp_fingerprint,
        "mlp_metrics": str(mlp_path.resolve()),
        "mlp_metrics_sha256": file_hash(mlp_path),
        "comparator_metrics": str(comparator_path.resolve()),
        "comparator_metrics_sha256": file_hash(comparator_path),
        "training_source": {
            name: arguments[name]
            for name in (
                "csv",
                "config",
                "unknown_classes",
                "benign_class",
                "split_strategy",
                "max_per_class",
                "chunksize",
            )
        },
    }


def create_protocol(
    coverage: dict[str, Any],
    project_root: Path,
    mlp_root: Path,
    comparator_root: Path,
    observed_metrics: int,
) -> dict[str, Any]:
    if (
        coverage.get("schema_version") != "strict_v4_coverage_manifest_v2"
        or coverage.get("manifest_sha256") != canonical_hash(coverage)
    ):
        raise ValueError("VOS coverage manifest validation failed")
    if observed_metrics != 0:
        raise ValueError("VOS pilot protocol must be frozen before pilot results")
    registry = coverage.get("scenario_registry", {})
    for suite, scenarios in SELECTED_SCENARIOS.items():
        if not set(scenarios) <= set(registry.get(suite, {}).get("scenarios", [])):
            raise ValueError(f"VOS pilot scenario is outside coverage: {suite}")
    sources = [
        source_record(mlp_root, comparator_root, suite, scenario)
        for suite in sorted(SELECTED_SCENARIOS)
        for scenario in SELECTED_SCENARIOS[suite]
    ]
    protocol = {
        "schema_version": "strict_v4_vos_pilot_protocol_v1",
        "status": "frozen_before_vos_pilot_results",
        "scope": "development_budget_screen_not_confirmatory_inference",
        "coverage_manifest_sha256": coverage["manifest_sha256"],
        "selection_rule": (
            "the existing frozen external-training pilot registry; independent of all "
            "VOS results"
        ),
        "selected_scenarios": SELECTED_SCENARIOS,
        "source_registry": sources,
        "source_registry_count": 14,
        "seed": 7,
        "method": "vos_energy",
        "reference_methods": ["opendetect", "mlp_energy"],
        "expected_runs": 14,
        "official_source": {
            "paper": "https://openreview.net/forum?id=TW7d65uYu5M",
            "code": "https://github.com/deeplearning-wisc/vos",
            "classification_trainer": (
                "https://github.com/deeplearning-wisc/vos/blob/main/"
                "classification/CIFAR/train_virtual.py"
            ),
            "venue": "ICLR 2022",
        },
        "frozen_hyperparameters": {
            "epochs": 35,
            "start_epoch": 10,
            "batch_size": 128,
            "hidden_dim": 256,
            "embedding_dim": 128,
            "dropout": 0.1,
            "learning_rate": 0.001,
            "weight_decay": 0.0001,
            "queue_size": 128,
            "sample_from": 1000,
            "select": 1,
            "covariance_ridge": 0.0001,
            "outlier_loss_weight": 0.1,
            "known_acceptance": 0.95,
            "sampling": "natural",
        },
        "method_definition": {
            "class_conditional_model": "per-class mean with tied covariance",
            "virtual_outliers": "lowest-likelihood Gaussian samples per known class",
            "training_regularizer": "weighted-energy ID-versus-virtual-OOD classifier",
            "primary_detector": "plain negative logsumexp energy",
        },
        "adaptation_disclosure": {
            "shared_backbone": "two-layer tabular MLP on concatenated side-channel views",
            "official_components_retained": [
                "per-class feature queues",
                "class means and tied covariance",
                "low-likelihood Gaussian virtual outliers",
                "weighted-energy binary regularization",
                "plain energy primary detector",
            ],
            "scaled_for_tabular_pilot": [
                "queue size 128 instead of 1000",
                "candidate samples 1000 instead of 10000",
                "35-epoch fixed budget and epoch-10 regularizer start",
                "AdamW optimizer matched to the shared tabular backbone",
            ],
            "not_author_checkpoint_reproduction": True,
            "distinct_from_npos": (
                "parametric tied-Gaussian low-likelihood sampling, not KNN boundary "
                "selection and perturbation"
            ),
        },
        "fit_data": "known_training_only",
        "threshold_data": "known_validation_only",
        "test_labels": "final_development_metrics_and_prefrozen_expansion_gate_only",
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "ood_parameter_sweep": False,
        "implementation_sha256": {
            name: file_hash(project_root / name) for name in IMPLEMENTATIONS
        },
        "pilot_metrics_observed_at_freeze": 0,
    }
    protocol["implementation_sha256"]["protocol_creator"] = file_hash(Path(__file__))
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def create_gate(protocol: dict[str, Any]) -> dict[str, Any]:
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("VOS pilot protocol SHA mismatch")
    gate = {
        "schema_version": "strict_v4_vos_pilot_expansion_gate_v1",
        "status": "frozen_before_vos_pilot_results",
        "pilot_protocol_manifest_sha256": protocol["manifest_sha256"],
        "pilot_metrics_observed_at_freeze": 0,
        "candidate": "vos_energy",
        "references": ["opendetect", "mlp_energy"],
        "required_checks": {
            "pilot_runs_complete": "14/14 and zero failures",
            "split_and_leakage_integrity": (
                "all source splits match and no unknown/test fitting"
            ),
            "known_f1_tolerance": (
                "mean VOS-OpenDetect >= -0.03 and worst >= -0.10"
            ),
            "top_two_rank": (
                "four-unknown-metric mean rank among three methods <= 2.0"
            ),
            "metric_breadth": (
                "positive mean gain over OpenDetect on at least two of four metrics"
            ),
            "overall_gain": (
                "four-metric oriented mean gain over OpenDetect is positive"
            ),
            "suite_robustness": (
                "at least four suites nonnegative and worst suite >= -0.05"
            ),
        },
        "pass_action": "freeze and implement VOS full102 protocol before expansion",
        "failure_action": "retain as negative strong-baseline evidence",
        "test_labels_used_for_development_gate": True,
    }
    gate["manifest_sha256"] = canonical_hash(gate)
    return gate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--mlp-root", type=Path, required=True)
    parser.add_argument("--comparator-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    observed = (
        len(list(args.run_root.glob("*/*_seed7_vos/metrics.json")))
        if args.run_root.exists()
        else 0
    )
    protocol = create_protocol(
        load_json(args.coverage),
        args.project_root.resolve(),
        args.mlp_root.resolve(),
        args.comparator_root.resolve(),
        observed,
    )
    gate = create_gate(protocol)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in (
        ("protocol_manifest.json", protocol),
        ("expansion_gate.json", gate),
    ):
        path = args.output_dir / name
        if path.is_file() and load_json(path) != payload:
            raise ValueError(f"existing frozen VOS artifact differs: {path}")
        if not path.is_file():
            path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    (args.output_dir / "protocol_complete").touch()
    print(json.dumps({"protocol": protocol["manifest_sha256"], "runs": 14}, sort_keys=True))


if __name__ == "__main__":
    main()
