from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from benchmark_strict_v4_vgrf_selected_system import (
    equal_views,
    load_views,
)
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_postselection_corruption import selected_modality
from run_strict_v4_vgrf_selected_system_seed317 import load


METRICS = (
    "known_macro_f1",
    "unknown_auroc",
    "unknown_aupr",
    "unknown_fpr95",
    "oscr",
)


def source_roots(record: dict[str, Any]) -> dict[str, Path]:
    roots = (
        record["source_roots"]
        if record["source_mode"] == "frozen_selection_artifacts"
        else record["run_output_roots"]
    )
    return {name: Path(value) for name, value in roots.items()}


def risk_ece(
    risk: np.ndarray, unknown: np.ndarray, bins: int = 10
) -> float:
    scores = np.clip(np.asarray(risk, dtype=np.float64), 0.0, 1.0)
    target = np.asarray(unknown, dtype=np.float64)
    if scores.ndim != 1 or target.shape != scores.shape or not scores.size:
        raise ValueError("risk ECE inputs are invalid")
    edges = np.linspace(0.0, 1.0, bins + 1)
    assignments = np.clip(
        np.searchsorted(edges, scores, side="right") - 1,
        0,
        bins - 1,
    )
    result = 0.0
    for index in range(bins):
        mask = assignments == index
        if np.any(mask):
            result += float(mask.mean()) * abs(
                float(scores[mask].mean()) - float(target[mask].mean())
            )
    return result


def degradation(
    clean: dict[str, float],
    corrupted: dict[str, float],
    metric: str,
) -> float:
    return (
        corrupted[metric] - clean[metric]
        if metric in ("unknown_fpr95", "ece")
        else clean[metric] - corrupted[metric]
    )


def report(
    labels: np.ndarray,
    unknown: np.ndarray,
    output: dict[str, np.ndarray],
    threshold: float,
) -> dict[str, float]:
    from caeos.hybrid_open_set import evaluate_hybrid_open_set

    result = evaluate_hybrid_open_set(
        labels,
        unknown,
        np.asarray(output["closed_set_index"]),
        np.asarray(output["risk"]),
        float(threshold),
    )
    result["ece"] = risk_ece(np.asarray(output["risk"]), unknown)
    return {
        metric: float(result[metric]) for metric in (*METRICS, "ece")
    }


def reconstruct_data(
    source_opendetect: Path,
) -> tuple[
    list[np.ndarray],
    list[np.ndarray],
    np.ndarray,
    np.ndarray,
    str,
]:
    import torch

    from caeos.data import prepare_tabular_open_set

    try:
        checkpoint = torch.load(
            source_opendetect / "model.pt",
            map_location="cpu",
            weights_only=False,
        )
    except TypeError:
        checkpoint = torch.load(
            source_opendetect / "model.pt", map_location="cpu"
        )
    arguments = checkpoint["arguments"]
    config_path = Path(str(arguments["config"]))
    if not config_path.is_absolute():
        config_path = Path.cwd() / config_path
    config = load(config_path)
    unknown_classes = [
        value.strip()
        for value in str(arguments["unknown_classes"]).split(",")
        if value.strip()
    ]
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
    return (
        [view.numpy() for view in bundle.train.views],
        [view.numpy() for view in bundle.test.views],
        bundle.test.labels.numpy(),
        bundle.test.is_unknown.numpy(),
        bundle.split_metadata["split_fingerprint"]["combined"],
    )


def evaluate_record(
    *,
    record: dict[str, Any],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    import joblib

    from train_hybrid_open_set import apply_test_corruption

    source = source_roots(record)
    deployment = {
        name: Path(value)
        for name, value in record["deployment_output_roots"].items()
    }
    capture_roots = {
        "vgrf": deployment["vgrf_capture"],
        "opendetect": deployment["opendetect_capture"],
    }
    manifests = {
        name: load(root / "capture_manifest.json")
        for name, root in capture_roots.items()
    }
    bundles = {
        name: joblib.load(root / manifests[name]["deployment_artifact"])
        for name, root in capture_roots.items()
    }
    input_views = {
        name: load_views(
            root / manifests[name]["processed_benchmark_inputs"]
        )
        for name, root in capture_roots.items()
    }
    if not equal_views(input_views["vgrf"], input_views["opendetect"]):
        raise ValueError("corruption clean input arrays differ")
    clean_views = input_views["vgrf"]
    (
        train_views,
        reconstructed_test_views,
        labels,
        unknown,
        split_fingerprint,
    ) = reconstruct_data(source["opendetect"])
    if not equal_views(clean_views, reconstructed_test_views):
        raise ValueError("captured and reconstructed test inputs differ")
    source_pairwise_metrics = load(source["pairwise"] / "metrics.json")
    expected_split = source_pairwise_metrics["split_metadata"][
        "split_fingerprint"
    ]["combined"]
    if split_fingerprint != expected_split:
        raise ValueError("reconstructed corruption split differs")
    clean_outputs = {
        name: bundle.predict_views(clean_views)
        for name, bundle in bundles.items()
    }
    thresholds = {
        name: float(bundle.selected_threshold)
        for name, bundle in bundles.items()
    }
    clean_reports = {
        name: report(labels, unknown, clean_outputs[name], thresholds[name])
        for name in bundles
    }
    conditions = []
    corruption = protocol["comparative_corruption"]
    for family in corruption["families"]:
        modality = selected_modality(
            protocol["coverage_manifest_sha256"],
            record["suite"],
            record["scenario"],
            family,
        )
        severity = float(corruption["fixed_severity"][family])
        corrupted_views, metadata = apply_test_corruption(
            clean_views,
            train_views,
            family,
            modality,
            severity,
            int(corruption["corruption_seed"]),
        )
        reports = {
            name: report(
                labels,
                unknown,
                bundle.predict_views(corrupted_views),
                thresholds[name],
            )
            for name, bundle in bundles.items()
        }
        degradations = {
            name: {
                metric: degradation(
                    clean_reports[name], reports[name], metric
                )
                for metric in (*METRICS, "ece")
            }
            for name in bundles
        }
        conditions.append(
            {
                "family": family,
                "metadata": metadata,
                "vgrf_report": reports["vgrf"],
                "opendetect_report": reports["opendetect"],
                "vgrf_degradation": degradations["vgrf"],
                "opendetect_degradation": degradations["opendetect"],
                "vgrf_robustness_advantage": {
                    metric: (
                        degradations["opendetect"][metric]
                        - degradations["vgrf"][metric]
                    )
                    for metric in (*METRICS, "ece")
                },
            }
        )
    value = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_corruption_block_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": record["suite"],
        "scenario": record["scenario"],
        "seed": int(record["seed"]),
        "source_split_fingerprint": split_fingerprint,
        "vgrf_clean_report": clean_reports["vgrf"],
        "opendetect_clean_report": clean_reports["opendetect"],
        "conditions": conditions,
        "vgrf_opendetect_input_arrays_equal": True,
        "degradation_uses_same_deployment_runtime_clean_anchors": True,
        "test_labels_used_for_final_metrics_only": True,
        "unknown_or_test_labels_used_for_fitting_selection_or_corruption_generation": False,
        "source_capture_manifest_sha256": {
            name: file_hash(root / "capture_manifest.json")
            for name, root in capture_roots.items()
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    if (
        protocol.get("schema_version")
        != "strict_v4_vgrf_selected_system_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("invalid selected-system execution protocol")
    active = Path(__file__).resolve()
    if protocol.get("implementation_sha256", {}).get(
        active.name
    ) != file_hash(active):
        raise ValueError("active corruption evaluator SHA mismatch")
    matches = [
        item
        for item in protocol["source_registry"]
        if item["suite"] == args.suite
        and item["scenario"] == args.scenario
        and int(item["seed"]) == args.seed
    ]
    if len(matches) != 1:
        raise ValueError("corruption source identity is not unique")
    result = evaluate_record(record=matches[0], protocol=protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "suite": args.suite,
                "scenario": args.scenario,
                "seed": args.seed,
                "conditions": len(result["conditions"]),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
