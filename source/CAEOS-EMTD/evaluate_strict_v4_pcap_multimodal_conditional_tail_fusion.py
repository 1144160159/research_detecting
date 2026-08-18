from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_pcap_multimodal_classical_baselines import (
    METRICS,
    aggregate,
    evaluate_risk,
)
from strict_v4_cic_iot2023_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


SCENARIOS = ("DDoS", "DoS", "Mirai")
COMPONENTS = ("uncertainty", "conflict", "distance", "energy")
IDENTITY_METRICS = (
    "known_macro_f1",
    "known_balanced_accuracy",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def class_conditional_percentile(
    reference_values: np.ndarray,
    reference_prediction: np.ndarray,
    query_values: np.ndarray,
    query_prediction: np.ndarray,
    *,
    minimum_class_samples: int = 20,
) -> np.ndarray:
    reference = np.asarray(reference_values, dtype=np.float64)
    reference_class = np.asarray(reference_prediction, dtype=np.int64)
    query = np.asarray(query_values, dtype=np.float64)
    query_class = np.asarray(query_prediction, dtype=np.int64)
    if reference.shape != reference_class.shape:
        raise ValueError("reference values and predictions differ")
    if query.shape != query_class.shape:
        raise ValueError("query values and predictions differ")
    if (
        reference.ndim != 1
        or query.ndim != 1
        or len(reference) == 0
        or not np.isfinite(reference).all()
        or not np.isfinite(query).all()
    ):
        raise ValueError("tail calibration requires finite non-empty vectors")
    if minimum_class_samples < 2:
        raise ValueError("minimum class samples must be at least two")

    global_reference = np.sort(reference)
    percentile = np.empty(len(query), dtype=np.float64)
    for class_index in np.unique(query_class):
        selected_query = query_class == class_index
        selected_reference = reference[reference_class == class_index]
        calibration = (
            np.sort(selected_reference)
            if len(selected_reference) >= minimum_class_samples
            else global_reference
        )
        rank_left = np.searchsorted(
            calibration,
            query[selected_query],
            side="left",
        )
        rank_right = np.searchsorted(
            calibration,
            query[selected_query],
            side="right",
        )
        percentile[selected_query] = (
            rank_left + rank_right
        ) / (2.0 * len(calibration))
    return percentile


def conditional_tail_candidates(
    arrays: dict[str, np.ndarray],
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    validation_belief = arrays["baseline_validation_belief"]
    test_belief = arrays["baseline_test_belief"]
    validation_prediction = validation_belief.argmax(axis=1)
    test_prediction = test_belief.argmax(axis=1)

    validation_tails = []
    test_tails = []
    for component in COMPONENTS:
        validation = arrays[f"self_validation_{component}"]
        test = arrays[f"self_test_{component}"]
        validation_tails.append(
            class_conditional_percentile(
                validation,
                validation_prediction,
                validation,
                validation_prediction,
            )
        )
        test_tails.append(
            class_conditional_percentile(
                validation,
                validation_prediction,
                test,
                test_prediction,
            )
        )
    validation_matrix = np.stack(validation_tails, axis=1)
    test_matrix = np.stack(test_tails, axis=1)

    validation_sorted = np.sort(validation_matrix, axis=1)
    test_sorted = np.sort(test_matrix, axis=1)
    validation_evidential = validation_matrix[:, [0, 3]].mean(axis=1)
    test_evidential = test_matrix[:, [0, 3]].mean(axis=1)
    validation_structural = validation_matrix[:, [1, 2]].mean(axis=1)
    test_structural = test_matrix[:, [1, 2]].mean(axis=1)
    validation_dual = np.maximum(
        validation_evidential,
        validation_structural,
    )
    test_dual = np.maximum(test_evidential, test_structural)

    validation_self = class_conditional_percentile(
        arrays["self_validation_risk"],
        validation_prediction,
        arrays["self_validation_risk"],
        validation_prediction,
    )
    test_self = class_conditional_percentile(
        arrays["self_validation_risk"],
        validation_prediction,
        arrays["self_test_risk"],
        test_prediction,
    )
    return {
        "CAEOS-EMTD": (
            arrays["self_validation_risk"],
            arrays["self_test_risk"],
        ),
        "CCTF-Mean": (
            validation_matrix.mean(axis=1),
            test_matrix.mean(axis=1),
        ),
        "CCTF-Max": (
            validation_matrix.max(axis=1),
            test_matrix.max(axis=1),
        ),
        "CCTF-Top2Mean": (
            validation_sorted[:, -2:].mean(axis=1),
            test_sorted[:, -2:].mean(axis=1),
        ),
        "CCTF-DualPathMax": (validation_dual, test_dual),
        "CCTF-SelfDualMean": (
            0.5 * (validation_self + validation_dual),
            0.5 * (test_self + test_dual),
        ),
        "CCTF-SelfDualMax": (
            np.maximum(validation_self, validation_dual),
            np.maximum(test_self, test_dual),
        ),
    }


def load_diagnostic_arrays(path: Path) -> dict[str, np.ndarray]:
    required = {
        "baseline_validation_belief",
        "baseline_validation_label",
        "baseline_test_belief",
        "baseline_test_label",
        "baseline_test_is_unknown",
        "self_validation_risk",
        "self_test_risk",
    } | {
        f"self_{split}_{component}"
        for split in ("validation", "test")
        for component in COMPONENTS
    }
    with np.load(path, allow_pickle=False) as payload:
        missing = sorted(required - set(payload.files))
        if missing:
            raise ValueError(
                "conditional-tail score arrays are missing: "
                + ", ".join(missing)
            )
        return {name: np.asarray(payload[name]) for name in required}


def scenario_records(
    arrays: dict[str, np.ndarray],
) -> dict[str, dict[str, float]]:
    test_prediction = arrays["baseline_test_belief"].argmax(axis=1)
    return {
        name: evaluate_risk(
            validation_risk=validation_risk,
            test_risk=test_risk,
            test_prediction=test_prediction,
            test_labels=arrays["baseline_test_label"],
            is_unknown=arrays["baseline_test_is_unknown"],
        )
        for name, (validation_risk, test_risk) in (
            conditional_tail_candidates(arrays).items()
        )
    }


def fixed_method_records(
    arrays: dict[str, np.ndarray],
    method: str,
) -> dict[str, dict[str, float]]:
    records = scenario_records(arrays)
    if method == "CAEOS-EMTD" or method not in records:
        raise ValueError(f"invalid fixed conditional-tail method: {method}")
    return {
        "CAEOS-EMTD": records["CAEOS-EMTD"],
        method: records[method],
    }


def build_evaluation(
    protocol_path: Path,
    completion_path: Path,
) -> dict[str, Any]:
    protocol = load_canonical(protocol_path.resolve(), "protocol")
    completion = load_canonical(completion_path.resolve(), "completion")
    if (
        completion.get("state") != "completed"
        or completion.get("task_count") != len(SCENARIOS)
        or completion.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
    ):
        raise ValueError("diagnostic export run is incomplete or mismatched")
    if not protocol["claim_boundary"][
        "frozen_model_calibrator_and_split_reused"
    ]:
        raise ValueError("conditional-tail diagnosis requires frozen reuse")

    run_root = Path(protocol["paths"]["run_root"])
    by_method: dict[str, dict[str, dict[str, float]]] = {}
    artifacts: dict[str, dict[str, str]] = {}
    identity: dict[str, dict[str, float | bool]] = {}
    for scenario in SCENARIOS:
        task_root = run_root / scenario.lower()
        metrics_path = task_root / "metrics.json"
        scores_path = task_root / "scores.npz"
        if (
            file_hash(metrics_path)
            != completion["task_metric_sha256"][scenario]
        ):
            raise ValueError(f"{scenario} metrics differ from completion")
        metrics = load_canonical(metrics_path, f"{scenario} task metrics")
        records = scenario_records(load_diagnostic_arrays(scores_path))
        for method, record in records.items():
            by_method.setdefault(method, {})[scenario] = record
        differences = {
            metric: abs(
                float(records["CAEOS-EMTD"][metric])
                - float(metrics["three_layer_metrics"][metric])
            )
            for metric in IDENTITY_METRICS
        }
        maximum_difference = max(differences.values())
        if maximum_difference > 1e-7:
            raise ValueError(
                f"{scenario} self-risk identity check failed: "
                f"{maximum_difference}"
            )
        frozen = metrics["training"]["frozen_base_task"]
        if not frozen.get("three_layer_metric_identity_pass"):
            raise ValueError(f"{scenario} frozen checkpoint identity failed")
        identity[scenario] = {
            "array_self_risk_metric_max_abs_difference": (
                maximum_difference
            ),
            "frozen_base_metric_max_abs_difference": float(
                frozen["three_layer_metric_max_abs_difference"]
            ),
            "pass": True,
        }
        artifacts[scenario] = {
            "metrics_sha256": file_hash(metrics_path),
            "scores_sha256": file_hash(scores_path),
            "model_sha256": file_hash(task_root / "model.pt"),
        }

    summaries = {
        method: aggregate(records) for method, records in by_method.items()
    }
    candidates = tuple(
        name for name in summaries if name != "CAEOS-EMTD"
    )
    selected = max(
        candidates,
        key=lambda name: (
            summaries[name]["unknown_auroc"]["worst"],
            summaries[name]["unknown_auroc"]["mean"],
            -summaries[name]["unknown_fpr95"]["mean"],
            summaries[name]["oscr"]["mean"],
        ),
    )
    selected_summary = summaries[selected]
    self_summary = summaries["CAEOS-EMTD"]
    comparison = {
        "selected_candidate": selected,
        "selection_uses_current_unknown_test_labels": True,
        "unknown_auroc_mean_delta": (
            selected_summary["unknown_auroc"]["mean"]
            - self_summary["unknown_auroc"]["mean"]
        ),
        "unknown_auroc_worst_delta": (
            selected_summary["unknown_auroc"]["worst"]
            - self_summary["unknown_auroc"]["worst"]
        ),
        "unknown_aupr_mean_delta": (
            selected_summary["unknown_aupr"]["mean"]
            - self_summary["unknown_aupr"]["mean"]
        ),
        "unknown_fpr95_reduction": (
            self_summary["unknown_fpr95"]["mean"]
            - selected_summary["unknown_fpr95"]["mean"]
        ),
        "oscr_mean_delta": (
            selected_summary["oscr"]["mean"]
            - self_summary["oscr"]["mean"]
        ),
    }
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_conditional_tail_fusion_v1"
        ),
        "state": "complete_development_diagnostic",
        "protocol": {
            "path": str(protocol_path.resolve()),
            "file_sha256": file_hash(protocol_path.resolve()),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "completion": {
            "path": str(completion_path.resolve()),
            "file_sha256": file_hash(completion_path.resolve()),
            "manifest_sha256": completion["manifest_sha256"],
        },
        "implementation_sha256": {
            Path(__file__).name: file_hash(Path(__file__).resolve()),
            "classical_baseline_evaluator": file_hash(
                Path(__file__).resolve().parent
                / "evaluate_strict_v4_pcap_multimodal_classical_baselines.py"
            ),
            "caeos/metrics.py": file_hash(
                Path(__file__).resolve().parent / "caeos" / "metrics.py"
            ),
        },
        "component_order": list(COMPONENTS),
        "methods": {
            "CAEOS-EMTD": "frozen fixed-weight composite risk",
            "CCTF-Mean": "mean of four class-conditional tail percentiles",
            "CCTF-Max": "maximum class-conditional tail percentile",
            "CCTF-Top2Mean": "mean of the two largest tail percentiles",
            "CCTF-DualPathMax": (
                "maximum of evidential uncertainty-energy mean and "
                "structural conflict-distance mean"
            ),
            "CCTF-SelfDualMean": (
                "mean of class-conditional self-risk tail and dual-path risk"
            ),
            "CCTF-SelfDualMax": (
                "maximum of class-conditional self-risk tail and "
                "dual-path risk"
            ),
        },
        "per_scenario": by_method,
        "summary": summaries,
        "selected_development_candidate": comparison,
        "identity": identity,
        "artifacts": artifacts,
        "claim_boundary": {
            "same_frozen_native_three_modal_backbone": True,
            "same_capture_grouped_family_held_out_split": True,
            "tail_calibration_uses_known_only_validation": True,
            "thresholds_use_known_only_validation": True,
            "unknown_test_used_to_fit_scores_or_thresholds": False,
            "unknown_test_used_for_candidate_selection": True,
            "development_diagnostic_only": True,
            "confirmation_claim_permitted": False,
            "sota_claim_permitted": False,
            "fresh_unseen_seed_required_if_candidate_is_frozen": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    return report


def build_replication_evaluation(
    replication_protocol_path: Path,
    completion_path: Path,
) -> dict[str, Any]:
    replication = load_canonical(
        replication_protocol_path.resolve(),
        "conditional-tail replication protocol",
    )
    if replication.get("state") != "frozen_before_replication_effects":
        raise ValueError("conditional-tail replication protocol is not frozen")
    method = str(replication["selected_method"])
    target_path = Path(replication["target_training_protocol"]["path"])
    target = load_canonical(target_path, "target training protocol")
    source_path = Path(replication["source_development_diagnostic"]["path"])
    source = load_canonical(source_path, "source development diagnostic")
    if (
        file_hash(target_path)
        != replication["target_training_protocol"]["file_sha256"]
        or target["manifest_sha256"]
        != replication["target_training_protocol"]["manifest_sha256"]
        or file_hash(source_path)
        != replication["source_development_diagnostic"]["file_sha256"]
        or source["manifest_sha256"]
        != replication["source_development_diagnostic"]["manifest_sha256"]
        or source["selected_development_candidate"]["selected_candidate"]
        != method
    ):
        raise ValueError("replication source or target binding differs")
    completion = load_canonical(completion_path.resolve(), "completion")
    if (
        completion.get("state") != "completed"
        or completion.get("task_count") != len(SCENARIOS)
        or completion.get("protocol_manifest_sha256")
        != target["manifest_sha256"]
    ):
        raise ValueError("fresh replication run is incomplete or mismatched")
    if target["protocol"]["development_seed"] != replication["target_seed"]:
        raise ValueError("fresh replication seed differs from frozen protocol")

    run_root = Path(target["paths"]["run_root"])
    by_method: dict[str, dict[str, dict[str, float]]] = {}
    artifacts: dict[str, dict[str, str]] = {}
    for scenario in SCENARIOS:
        task_root = run_root / scenario.lower()
        metrics_path = task_root / "metrics.json"
        scores_path = task_root / "scores.npz"
        if (
            file_hash(metrics_path)
            != completion["task_metric_sha256"][scenario]
        ):
            raise ValueError(f"{scenario} metrics differ from completion")
        records = fixed_method_records(
            load_diagnostic_arrays(scores_path),
            method,
        )
        for name, record in records.items():
            by_method.setdefault(name, {})[scenario] = record
        artifacts[scenario] = {
            "metrics_sha256": file_hash(metrics_path),
            "scores_sha256": file_hash(scores_path),
            "model_sha256": file_hash(task_root / "model.pt"),
        }

    summaries = {
        name: aggregate(records) for name, records in by_method.items()
    }
    candidate = summaries[method]
    incumbent = summaries["CAEOS-EMTD"]
    source_candidate = source["summary"][method]
    comparison = {
        "fixed_method": method,
        "method_reselected_on_target_unknown": False,
        "target_unknown_auroc_mean_delta_vs_incumbent": (
            candidate["unknown_auroc"]["mean"]
            - incumbent["unknown_auroc"]["mean"]
        ),
        "target_unknown_auroc_worst_delta_vs_incumbent": (
            candidate["unknown_auroc"]["worst"]
            - incumbent["unknown_auroc"]["worst"]
        ),
        "target_unknown_fpr95_reduction_vs_incumbent": (
            incumbent["unknown_fpr95"]["mean"]
            - candidate["unknown_fpr95"]["mean"]
        ),
        "target_oscr_mean_delta_vs_incumbent": (
            candidate["oscr"]["mean"] - incumbent["oscr"]["mean"]
        ),
        "candidate_unknown_auroc_mean_delta_vs_source": (
            candidate["unknown_auroc"]["mean"]
            - source_candidate["unknown_auroc"]["mean"]
        ),
        "candidate_unknown_auroc_worst_delta_vs_source": (
            candidate["unknown_auroc"]["worst"]
            - source_candidate["unknown_auroc"]["worst"]
        ),
    }
    report: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pcap_multimodal_conditional_tail_replication_v1"
        ),
        "state": "complete_fresh_development_replication",
        "replication_protocol": {
            "path": str(replication_protocol_path.resolve()),
            "file_sha256": file_hash(replication_protocol_path.resolve()),
            "manifest_sha256": replication["manifest_sha256"],
        },
        "target_training_protocol": {
            "path": str(target_path),
            "file_sha256": file_hash(target_path),
            "manifest_sha256": target["manifest_sha256"],
        },
        "completion": {
            "path": str(completion_path.resolve()),
            "file_sha256": file_hash(completion_path.resolve()),
            "manifest_sha256": completion["manifest_sha256"],
        },
        "implementation_sha256": {
            Path(__file__).name: file_hash(Path(__file__).resolve()),
            "classical_baseline_evaluator": file_hash(
                Path(__file__).resolve().parent
                / "evaluate_strict_v4_pcap_multimodal_classical_baselines.py"
            ),
            "caeos/metrics.py": file_hash(
                Path(__file__).resolve().parent / "caeos" / "metrics.py"
            ),
        },
        "fixed_method": method,
        "per_scenario": by_method,
        "summary": summaries,
        "comparison": comparison,
        "artifacts": artifacts,
        "claim_boundary": {
            "fresh_model_training_seed": True,
            "reserved_confirmation_seed_used": False,
            "method_frozen_before_target_effects": True,
            "method_reselected_on_target_unknown": False,
            "tail_calibration_uses_known_only_validation": True,
            "thresholds_use_known_only_validation": True,
            "target_unknown_used_to_fit_scores_or_thresholds": False,
            "target_unknown_used_for_evaluation_only": True,
            "development_replication_only": True,
            "confirmation_claim_permitted": False,
            "sota_claim_permitted": False,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--protocol", type=Path)
    source.add_argument("--replication-protocol", type=Path)
    parser.add_argument("--completion", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = (
        build_replication_evaluation(
            args.replication_protocol,
            args.completion,
        )
        if args.replication_protocol is not None
        else build_evaluation(args.protocol, args.completion)
    )
    atomic_json(args.output.resolve(), report)
    summary = {
        "output": str(args.output.resolve()),
        "manifest_sha256": report["manifest_sha256"],
    }
    if "selected_development_candidate" in report:
        summary["selected_development_candidate"] = report[
            "selected_development_candidate"
        ]
    if "comparison" in report:
        summary["comparison"] = report["comparison"]
    print(summary)


if __name__ == "__main__":
    main()
