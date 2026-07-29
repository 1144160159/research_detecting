from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from evaluate_strict_v4_benign_calibrated_warning import calibrate_threshold
from evaluate_strict_v4_hybrid_self_algorithm_development import (
    gates,
    operational_metrics,
    upper_tail_threshold,
)
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)
from train_strict_v4_packet_sequence_fusion_task_cuda import (
    stratified_open_set_split,
)


BENIGN_FPR_BUDGET = 0.049
OPEN_BUDGET = 0.04
EXPANSION_UNKNOWN_ALERT_RECALL = 0.6036585365853659


def noisy_or(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return 1.0 - (1.0 - left) * (1.0 - right)


def fusion_candidates(
    psf_alert: np.ndarray,
    dmc_alert: np.ndarray,
) -> list[tuple[str, np.ndarray]]:
    return [
        ("psf_only", psf_alert),
        ("dmc_only", dmc_alert),
        ("convex_psf_0p25", 0.25 * psf_alert + 0.75 * dmc_alert),
        ("convex_psf_0p50", 0.50 * psf_alert + 0.50 * dmc_alert),
        ("convex_psf_0p75", 0.75 * psf_alert + 0.25 * dmc_alert),
        ("maximum", np.maximum(psf_alert, dmc_alert)),
        ("noisy_or", noisy_or(psf_alert, dmc_alert)),
    ]


def validation_summary(
    score: np.ndarray,
    labels: np.ndarray,
    benign_index: int,
) -> dict[str, Any]:
    calibration = calibrate_threshold(
        score,
        np.full(labels.shape, benign_index, dtype=np.int64),
        labels,
        benign_index,
        BENIGN_FPR_BUDGET,
    )
    if not calibration["feasible"]:
        raise ValueError("validation alert calibration is infeasible")
    predicted = score >= float(calibration["threshold"])
    attack = labels != benign_index
    benign = ~attack
    return {
        "calibration": calibration,
        "known_attack_recall": float(predicted[attack].mean()),
        "alert_accuracy": float((predicted == attack).mean()),
        "benign_fpr": float(predicted[benign].mean()),
    }


def select_by_validation(
    candidates: list[tuple[str, np.ndarray]],
    labels: np.ndarray,
    benign_index: int,
) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    summaries = []
    for priority, (name, score) in enumerate(candidates):
        summary = validation_summary(score, labels, benign_index)
        summaries.append(
            {
                "name": name,
                "priority": priority,
                **summary,
            }
        )
    selected = max(
        summaries,
        key=lambda value: (
            value["known_attack_recall"],
            value["alert_accuracy"],
            -value["benign_fpr"],
            -value["priority"],
        ),
    )
    return selected["name"], selected, summaries


def load_task(
    task_dir: Path,
    dataset_path: Path,
    unknown_family: str,
    seed: int,
) -> dict[str, Any]:
    task_dir = task_dir.resolve()
    dataset_path = dataset_path.resolve()
    metrics = load_canonical(task_dir / "metrics.json", "CUDA task metrics")
    if metrics.get("state") != "complete":
        raise ValueError(f"task is not complete: {task_dir}")
    if not metrics.get("gpu_execution", {}).get("passes"):
        raise ValueError(f"task lacks passing CUDA evidence: {task_dir}")
    if metrics.get("task") != {
        "unknown_family": unknown_family,
        "seed": seed,
    }:
        raise ValueError(f"task identity mismatch: {task_dir}")
    if metrics["source"]["sequence_dataset_sha256"] != file_hash(dataset_path):
        raise ValueError(f"dataset hash mismatch: {dataset_path}")
    scores_path = task_dir / metrics["artifacts"]["scores"]["file"]
    if metrics["artifacts"]["scores"]["sha256"] != file_hash(scores_path):
        raise ValueError(f"score hash mismatch: {scores_path}")
    with np.load(scores_path, allow_pickle=False) as source:
        arrays = {name: np.asarray(source[name]) for name in source.files}
    with np.load(dataset_path, allow_pickle=False) as source:
        flow_ids = np.asarray(source["flow_ids"]).astype(str)
        capture_ids = np.asarray(source["capture_ids"]).astype(str)
        fine_labels = np.asarray(source["fine_labels"]).astype(str)
        families = np.asarray(source["families"]).astype(str)
        packet_lengths = np.asarray(source["packet_lengths"])
        interarrival_us = np.asarray(source["interarrival_us"])
        mask = np.asarray(source["mask"])
    signatures = []
    for index in range(flow_ids.size):
        digest = hashlib.sha256()
        for value in (
            capture_ids[index],
            flow_ids[index],
            fine_labels[index],
            families[index],
        ):
            digest.update(value.encode("utf-8"))
            digest.update(b"\0")
        digest.update(np.ascontiguousarray(packet_lengths[index]).tobytes())
        digest.update(np.ascontiguousarray(interarrival_us[index]).tobytes())
        digest.update(np.ascontiguousarray(mask[index]).tobytes())
        signatures.append(digest.hexdigest())
    splits = stratified_open_set_split(
        flow_ids,
        families,
        unknown_family=unknown_family,
        seed=seed,
    )
    known_class_names = np.asarray(arrays["known_class_names"]).astype(str)
    class_to_index = {
        family: index for index, family in enumerate(known_class_names.tolist())
    }
    for split in ("validation", "test"):
        indices = splits[split]
        labels = np.asarray(arrays[f"{split}_labels"], dtype=np.int64)
        if labels.size != indices.size:
            raise ValueError(f"{split} score rows do not match reconstructed split")
        expected = np.asarray(
            [class_to_index.get(families[index], -1) for index in indices],
            dtype=np.int64,
        )
        if not np.array_equal(labels, expected):
            raise ValueError(f"{split} labels do not match reconstructed split")
        if split == "test":
            expected_unknown = families[indices] == unknown_family
            if not np.array_equal(
                np.asarray(arrays["test_unknown"], dtype=bool),
                expected_unknown,
            ):
                raise ValueError("test unknown mask does not match dataset")
    return {
        "task_dir": task_dir,
        "dataset_path": dataset_path,
        "metrics": metrics,
        "arrays": arrays,
        "flow_ids": flow_ids,
        "signatures": np.asarray(signatures),
        "families": families,
        "splits": splits,
        "known_class_names": known_class_names,
    }


def paired_signature_rows(
    left_signatures: np.ndarray,
    right_signatures: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    left_groups: dict[str, list[int]] = defaultdict(list)
    right_groups: dict[str, list[int]] = defaultdict(list)
    for position, signature in enumerate(left_signatures.astype(str)):
        left_groups[signature].append(position)
    for position, signature in enumerate(right_signatures.astype(str)):
        right_groups[signature].append(position)
    left_rows = []
    right_rows = []
    identities = []
    for signature in sorted(set(left_groups) & set(right_groups)):
        pair_count = min(
            len(left_groups[signature]),
            len(right_groups[signature]),
        )
        for occurrence in range(pair_count):
            left_rows.append(left_groups[signature][occurrence])
            right_rows.append(right_groups[signature][occurrence])
            identities.append(f"{signature}:{occurrence}")
    return (
        np.asarray(left_rows, dtype=np.int64),
        np.asarray(right_rows, dtype=np.int64),
        identities,
    )


def align_split(
    left: dict[str, Any],
    right: dict[str, Any],
    split: str,
) -> dict[str, Any]:
    left_indices = left["splits"][split]
    right_indices = right["splits"][split]
    left_signatures = left["signatures"][left_indices]
    right_signatures = right["signatures"][right_indices]
    left_rows, right_rows, common = paired_signature_rows(
        left_signatures,
        right_signatures,
    )
    if not common:
        raise ValueError(f"{split} has no common content signatures")
    left_labels = np.asarray(left["arrays"][f"{split}_labels"])[left_rows]
    right_labels = np.asarray(right["arrays"][f"{split}_labels"])[right_rows]
    if not np.array_equal(left_labels, right_labels):
        raise ValueError(f"{split} labels differ after flow-ID alignment")
    if split == "test":
        left_unknown = np.asarray(left["arrays"]["test_unknown"])[left_rows]
        right_unknown = np.asarray(right["arrays"]["test_unknown"])[right_rows]
        if not np.array_equal(left_unknown, right_unknown):
            raise ValueError("test unknown masks differ after flow-ID alignment")
    return {
        "content_identities": np.asarray(common),
        "left_rows": left_rows,
        "right_rows": right_rows,
        "labels": right_labels.astype(np.int64),
        "unknown": (
            np.asarray(right["arrays"]["test_unknown"])[right_rows].astype(bool)
            if split == "test"
            else np.zeros(len(common), dtype=bool)
        ),
        "left_original_count": int(left_indices.size),
        "right_original_count": int(right_indices.size),
        "common_count": len(common),
    }


def take(task: dict[str, Any], split: str, name: str, rows: np.ndarray) -> np.ndarray:
    return np.asarray(task["arrays"][f"{split}_{name}"], dtype=np.float64)[rows]


def system_alerts(
    psf: dict[str, Any],
    dmc: dict[str, Any],
    alignment: dict[str, Any],
    split: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    psf_rows = alignment["left_rows"]
    dmc_rows = alignment["right_rows"]
    psf_alert = noisy_or(
        take(psf, split, "attack_probability", psf_rows),
        take(psf, split, "family_uncertainty_tail", psf_rows),
    )
    dmc_alert = np.maximum(
        take(dmc, split, "attack_probability", dmc_rows),
        take(dmc, split, "benign_distance_tail", dmc_rows),
    )
    open_fusion = noisy_or(
        take(psf, split, "open_noisy_or", psf_rows),
        take(dmc, split, "benign_distance_tail", dmc_rows),
    )
    return psf_alert, dmc_alert, open_fusion


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    psf = load_task(
        args.psf_task_dir,
        args.psf_dataset,
        args.unknown_family,
        args.seed,
    )
    dmc = load_task(
        args.dmc_task_dir,
        args.dmc_dataset,
        args.unknown_family,
        args.seed,
    )
    if not np.array_equal(psf["known_class_names"], dmc["known_class_names"]):
        raise ValueError("known class names differ between tasks")
    benign_index = int(dmc["metrics"]["benign_index"])
    validation = align_split(psf, dmc, "validation")
    test = align_split(psf, dmc, "test")
    validation_psf, validation_dmc, validation_open = system_alerts(
        psf, dmc, validation, "validation"
    )
    test_psf, test_dmc, test_open = system_alerts(psf, dmc, test, "test")
    validation_candidates = fusion_candidates(validation_psf, validation_dmc)
    selected_name, selected_validation, validation_summaries = (
        select_by_validation(
            validation_candidates,
            validation["labels"],
            benign_index,
        )
    )
    test_candidates = dict(fusion_candidates(test_psf, test_dmc))
    threshold = float(selected_validation["calibration"]["threshold"])
    predicted_alert = test_candidates[selected_name] >= threshold
    validation_known_attack = validation["labels"] != benign_index
    open_threshold = upper_tail_threshold(
        validation_open[validation_known_attack],
        OPEN_BUDGET,
    )
    predicted_unknown = predicted_alert & (test_open >= open_threshold)
    dmc_type_prediction = np.asarray(
        dmc["arrays"]["test_type_prediction"], dtype=np.int64
    )[test["right_rows"]]
    metrics = operational_metrics(
        predicted_alert=predicted_alert,
        predicted_unknown=predicted_unknown,
        type_prediction=dmc_type_prediction,
        test_labels=test["labels"],
        test_unknown=test["unknown"],
        benign_index=benign_index,
    )
    expansion = {
        "benign_fpr_below_5_percent": metrics["benign_fpr"] < 0.05,
        "known_attack_type_accuracy_at_least_95_percent": (
            metrics["known_attack_type_accuracy"] >= 0.95
        ),
        "unknown_attack_alert_recall_at_least_preregistered_threshold": (
            metrics["unknown_attack_alert_recall"]
            >= EXPANSION_UNKNOWN_ALERT_RECALL
        ),
    }
    expansion["expand_to_seven_scenarios"] = all(expansion.values())
    result: dict[str, Any] = {
        "schema_version": "strict_v4_psf_dmc_complementarity_v1",
        "state": (
            "pilot_expansion_gate_passed"
            if expansion["expand_to_seven_scenarios"]
            else "pilot_expansion_gate_not_met"
        ),
        "task": {
            "unknown_family": args.unknown_family,
            "seed": args.seed,
        },
        "selection_policy": {
            "uses_validation_known_labels_only": True,
            "uses_true_unknown_for_candidate_selection": False,
            "alert_budget": BENIGN_FPR_BUDGET,
            "open_budget": OPEN_BUDGET,
            "type_prediction_source": "DMC corrected sequence control",
        },
        "alignment": {
            split: {
                key: value
                for key, value in aligned.items()
                if key.endswith("_count")
            }
            for split, aligned in (
                ("validation", validation),
                ("test", test),
            )
        },
        "selected_candidate": selected_name,
        "selected_validation": selected_validation,
        "validation_candidates": validation_summaries,
        "test": {
            "metrics": metrics,
            "gates": gates(metrics),
            "open_threshold": float(open_threshold),
            "expansion_gate": expansion,
        },
        "sources": {
            "psf": {
                "task_dir": str(psf["task_dir"]),
                "dataset": str(psf["dataset_path"]),
                "metrics_sha256": file_hash(psf["task_dir"] / "metrics.json"),
                "scores_sha256": file_hash(psf["task_dir"] / "scores.npz"),
                "gpu_execution_sha256": file_hash(
                    psf["task_dir"] / "gpu_execution.json"
                ),
            },
            "dmc": {
                "task_dir": str(dmc["task_dir"]),
                "dataset": str(dmc["dataset_path"]),
                "metrics_sha256": file_hash(dmc["task_dir"] / "metrics.json"),
                "scores_sha256": file_hash(dmc["task_dir"] / "scores.npz"),
                "gpu_execution_sha256": file_hash(
                    dmc["task_dir"] / "gpu_execution.json"
                ),
            },
        },
        "claim_boundary": {
            "evidence_reuse_only_no_model_training": True,
            "source_model_training_cuda_evidence_passed": True,
            "development_seed_only": True,
            "not_formal_confirmation": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    atomic_json(args.output.resolve(), result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--psf-task-dir", type=Path, required=True)
    parser.add_argument("--psf-dataset", type=Path, required=True)
    parser.add_argument("--dmc-task-dir", type=Path, required=True)
    parser.add_argument("--dmc-dataset", type=Path, required=True)
    parser.add_argument("--unknown-family", default="Botnet")
    parser.add_argument("--seed", type=int, default=29)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    result = evaluate(parse_arguments())
    print(
        json.dumps(
            {
                "manifest_sha256": result["manifest_sha256"],
                "selected_candidate": result["selected_candidate"],
                "state": result["state"],
                "test": result["test"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
