from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from benchmark_pairwise_runtime import load_views
from caeos.data import prepare_tabular_open_set
from caeos.hybrid_open_set import evaluate_hybrid_open_set
from caeos.open_detect_runtime import OpenDetectRuntime
from caeos.pairwise_runtime import PairwiseRuntime
from capture_opendetect_runtime import load_checkpoint
from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from run_strict_v4_postselection_corruption import selected_modality
from train_hybrid_open_set import apply_test_corruption


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON object required: {path}")
    return payload


def risk_ece(risk: np.ndarray, unknown: np.ndarray, bins: int = 10) -> float:
    scores = np.clip(np.asarray(risk, dtype=np.float64), 0.0, 1.0)
    target = np.asarray(unknown, dtype=np.float64)
    if scores.ndim != 1 or target.shape != scores.shape or scores.size == 0:
        raise ValueError("risk ECE inputs are invalid")
    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.clip(np.searchsorted(edges, scores, side="right") - 1, 0, bins - 1)
    result = 0.0
    for index in range(bins):
        mask = assignments == index
        if np.any(mask):
            result += float(mask.mean()) * abs(float(scores[mask].mean()) - float(target[mask].mean()))
    return result


def report(
    labels: np.ndarray,
    unknown: np.ndarray,
    output: dict[str, np.ndarray],
    threshold: float,
) -> dict[str, float]:
    result = evaluate_hybrid_open_set(
        labels,
        unknown,
        np.asarray(output["prediction"]),
        np.asarray(output["risk"]),
        float(threshold),
    )
    result["ece"] = risk_ece(np.asarray(output["risk"]), unknown)
    return {metric: float(result[metric]) for metric in (*METRICS, "ece")}


def degradation(clean: dict[str, float], corrupted: dict[str, float], metric: str) -> float:
    return (
        corrupted[metric] - clean[metric]
        if metric in ("unknown_fpr95", "ece")
        else clean[metric] - corrupted[metric]
    )


def archival_metric_differences(
    observed: dict[str, float], expected: dict[str, Any]
) -> dict[str, float]:
    return {
        metric: abs(observed[metric] - float(expected[metric]))
        for metric in METRICS
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--candidate-capture", type=Path, required=True)
    parser.add_argument("--comparator-capture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_json(args.protocol)
    if protocol.get("schema_version") != "strict_v4_comparative_corruption_protocol_v1" or protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("comparative corruption protocol validation failed")
    expected_evaluator_sha = protocol["implementation_sha256"]["evaluator"]
    if expected_evaluator_sha != file_hash(Path(__file__)):
        raise ValueError("comparative corruption evaluator implementation SHA mismatch")
    matches = [
        item
        for item in protocol["source_registry"]
        if item["suite"] == args.suite and item["scenario"] == args.scenario and int(item["seed"]) == args.seed
    ]
    if len(matches) != 1:
        raise ValueError("comparative corruption source identity is not unique")
    source = matches[0]
    candidate_root, comparator_root = Path(source["candidate_root"]), Path(source["comparator_root"])
    for name, expected in source["candidate_file_sha256"].items():
        if file_hash(candidate_root / name) != expected:
            raise ValueError(f"candidate source artifact SHA mismatch: {name}")
    for name, expected in source["comparator_file_sha256"].items():
        if file_hash(comparator_root / name) != expected:
            raise ValueError(f"comparator source artifact SHA mismatch: {name}")
    candidate_equivalence = load_json(args.candidate_capture / "equivalence.json")
    comparator_equivalence = load_json(args.comparator_capture / "equivalence.json")
    if (
        candidate_equivalence.get("passes") is not True
        or candidate_equivalence.get("equivalence_mode")
        != "source_components_plus_stable_runtime_shadow"
        or comparator_equivalence.get("passes") is not True
        or comparator_equivalence.get("equivalence_mode")
        != "runtime_vs_uninstrumented_same_device_shadow"
        or float(candidate_equivalence.get("risk_max_absolute_difference", 1.0)) > 1e-12
        or float(comparator_equivalence.get("risk_max_absolute_difference", 1.0)) > 1e-12
    ):
        raise ValueError("runtime equivalence gate failed")
    candidate = joblib.load(args.candidate_capture / "pairwise_runtime.joblib")
    comparator = joblib.load(args.comparator_capture / "opendetect_runtime.joblib")
    if not isinstance(candidate, PairwiseRuntime) or not isinstance(comparator, OpenDetectRuntime):
        raise TypeError("comparative corruption runtime types are invalid")
    candidate_views = load_views(args.candidate_capture / "benchmark_inputs.npz")
    comparator_views = load_views(args.comparator_capture / "benchmark_inputs.npz")
    if len(candidate_views) != len(comparator_views) or not all(
        np.array_equal(left, right) for left, right in zip(candidate_views, comparator_views)
    ):
        raise ValueError("candidate and comparator clean input arrays differ")
    comparator_checkpoint = load_checkpoint(comparator_root / "model.pt")
    arguments = comparator_checkpoint["arguments"]
    config_path = Path(str(arguments["config"]))
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path
    config = load_json(config_path)
    unknown_classes = [value.strip() for value in arguments["unknown_classes"].split(",") if value.strip()]
    bundle = prepare_tabular_open_set(
        str(arguments["csv"]),
        config,
        unknown_classes,
        str(arguments["benign_class"]),
        int(arguments["max_per_class"]),
        int(arguments["chunksize"]),
        int(arguments["seed"]),
        str(arguments["split_strategy"]),
    )
    if bundle.split_metadata["split_fingerprint"]["combined"] != source["split_fingerprint"]:
        raise ValueError("reconstructed comparative corruption split differs from source")
    bundle_test_views = [view.numpy() for view in bundle.test.views]
    if not all(np.array_equal(left, right) for left, right in zip(candidate_views, bundle_test_views)):
        raise ValueError("captured and reconstructed clean test arrays differ")
    train_views = [view.numpy() for view in bundle.train.views]
    labels = bundle.test.labels.numpy()
    unknown = bundle.test.unknown.numpy()
    candidate_metrics = load_json(candidate_root / "metrics.json")
    comparator_metrics = load_json(comparator_root / "metrics.json")
    candidate_threshold = float(candidate_metrics["validation_thresholds"][candidate.selected_risk])
    comparator_threshold = float(comparator_metrics["validation_thresholds"]["opendetect"])
    clean_candidate = report(labels, unknown, candidate.predict(candidate_views), candidate_threshold)
    clean_comparator = report(labels, unknown, comparator.predict(candidate_views), comparator_threshold)
    archival_differences = {
        "candidate": archival_metric_differences(
            clean_candidate, candidate_metrics["selected_report"]
        ),
        "comparator": archival_metric_differences(
            clean_comparator, comparator_metrics["reports"]["opendetect"]
        ),
    }
    conditions = []
    corruption = protocol["corruption_conditions"]
    for family in corruption["families"]:
        modality = selected_modality(protocol["coverage_manifest_sha256"], args.suite, args.scenario, family)
        severity = float(corruption["fixed_severity"][family])
        corrupted_views, metadata = apply_test_corruption(
            candidate_views,
            train_views,
            family,
            modality,
            severity,
            int(corruption["corruption_seed"]),
        )
        candidate_report = report(labels, unknown, candidate.predict(corrupted_views), candidate_threshold)
        comparator_report = report(labels, unknown, comparator.predict(corrupted_views), comparator_threshold)
        candidate_degradation = {
            metric: degradation(clean_candidate, candidate_report, metric)
            for metric in (*METRICS, "ece")
        }
        comparator_degradation = {
            metric: degradation(clean_comparator, comparator_report, metric)
            for metric in (*METRICS, "ece")
        }
        conditions.append(
            {
                "family": family,
                "metadata": metadata,
                "candidate_report": candidate_report,
                "comparator_report": comparator_report,
                "candidate_degradation": candidate_degradation,
                "comparator_degradation": comparator_degradation,
                "candidate_robustness_advantage": {
                    metric: comparator_degradation[metric] - candidate_degradation[metric]
                    for metric in (*METRICS, "ece")
                },
            }
        )
    payload = {
        "schema_version": "strict_v4_comparative_corruption_block_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": args.suite,
        "scenario": args.scenario,
        "seed": args.seed,
        "source_split_fingerprint": source["split_fingerprint"],
        "candidate_clean_report": clean_candidate,
        "comparator_clean_report": clean_comparator,
        "archival_clean_metric_absolute_differences_diagnostic_only": archival_differences,
        "degradation_uses_same_device_runtime_clean_anchors": True,
        "conditions": conditions,
        "candidate_comparator_input_arrays_equal": True,
        "test_labels_used_for_final_metrics_only": True,
        "unknown_or_test_labels_used_for_fitting_selection_or_corruption_generation": False,
        "active_evaluator_sha256": expected_evaluator_sha,
    }
    payload["manifest_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"suite": args.suite, "scenario": args.scenario, "seed": args.seed, "conditions": len(conditions)}, sort_keys=True))


if __name__ == "__main__":
    main()
