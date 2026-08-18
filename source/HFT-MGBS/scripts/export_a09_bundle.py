"""Train and export a frozen three-seed A09/A10 inference bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from hft_mgbs.candidate_dataset import extract_candidate_flow_records
from hft_mgbs.domain_features import transform_feature_rows
from hft_mgbs.unsw import UnswGroundTruth
from scripts.evaluate_unsw_independent_holdout import (
    select_macro_f1_threshold,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


PROMOTED_CANDIDATE_FLOORS = {"A09": 0.8, "A10": 0.9}


def validate_candidate_policy(candidate_id: str, recall_floor: float) -> None:
    expected = PROMOTED_CANDIDATE_FLOORS.get(candidate_id)
    if expected is None:
        raise ValueError("bundle exporter only supports A09 or A10")
    if abs(float(recall_floor) - expected) > 1e-12:
        raise ValueError(
            "{} requires calibration attack-recall floor {}".format(
                candidate_id, expected
            )
        )


def extract_training(manifest, args):
    rows = []
    labels = []
    groups = []
    for sample in manifest["samples"]:
        records, _ = extract_candidate_flow_records(
            sample["path"],
            sample["group"],
            batch_size=512,
            budget_us=5000.0,
            allow_deep=not args.disable_deep,
            key_flow_ratio=0.10,
            max_payload_bytes=256,
            max_packets=args.max_train_packets_per_capture,
            max_flows=args.max_train_flows_per_capture,
            execution_budget_safety_ratio=0.50,
        )
        rows.extend(record["features"] for record in records)
        labels.extend([int(sample["label"])] * len(records))
        groups.extend([sample["group"]] * len(records))
    return rows, labels, groups


def extract_unsw(manifest, truth, selected_groups, args):
    rows = []
    labels = []
    groups = []
    for sample in manifest["samples"]:
        if sample["group"] not in selected_groups:
            continue
        records, _ = extract_candidate_flow_records(
            sample["path"],
            sample["group"],
            batch_size=512,
            budget_us=5000.0,
            allow_deep=not args.disable_deep,
            key_flow_ratio=0.10,
            max_payload_bytes=256,
            max_packets=args.max_holdout_packets_per_capture,
            max_flows=args.max_holdout_flows_per_capture,
            execution_budget_safety_ratio=0.50,
        )
        sample_labels = [truth.label_flow_record(record) for record in records]
        rows.extend(record["features"] for record in records)
        labels.extend(sample_labels)
        groups.extend([sample["group"]] * len(records))
    return rows, labels, groups


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("training_manifest", type=Path)
    parser.add_argument("holdout_manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate-id", choices=sorted(PROMOTED_CANDIDATE_FLOORS), default="A09")
    parser.add_argument("--release-id", default="hft-mgbs-rc1")
    parser.add_argument(
        "--adaptation-groups",
        nargs="+",
        default=["unsw_2015-01-22_shard1", "unsw_2015-01-22_shard2"],
    )
    parser.add_argument(
        "--calibration-groups",
        nargs="+",
        default=["unsw_2015-01-22_shard3"],
    )
    parser.add_argument("--adaptation-weight-multiplier", type=float, default=5.0)
    parser.add_argument("--calibration-attack-recall-floor", type=float, default=0.8)
    parser.add_argument("--max-train-packets-per-capture", type=int, default=20000)
    parser.add_argument("--max-train-flows-per-capture", type=int, default=2000)
    parser.add_argument("--max-holdout-packets-per-capture", type=int, default=50000)
    parser.add_argument("--max-holdout-flows-per-capture", type=int, default=5000)
    parser.add_argument("--estimators", type=int, default=200)
    parser.add_argument("--n-jobs", type=int, default=8)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 11, 19])
    parser.add_argument(
        "--disable-deep",
        action="store_true",
        help="Export the fallback feature path with deep extraction disabled.",
    )
    parser.add_argument("--input-hash-manifest", type=Path)
    args = parser.parse_args()
    try:
        validate_candidate_policy(
            args.candidate_id, args.calibration_attack_recall_floor
        )
    except ValueError as error:
        parser.error(str(error))

    import joblib
    import numpy as np
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.feature_extraction import DictVectorizer

    with args.training_manifest.open("r", encoding="utf-8") as handle:
        training_manifest = json.load(handle)
    with args.holdout_manifest.open("r", encoding="utf-8") as handle:
        holdout_manifest = json.load(handle)
    if set(args.adaptation_groups) & set(args.calibration_groups):
        parser.error("adaptation and calibration groups must be disjoint")
    truth = UnswGroundTruth.from_csv(Path(holdout_manifest["ground_truth_csv"]))
    train_rows, train_labels, train_groups = extract_training(
        training_manifest, args
    )
    selected = set(args.adaptation_groups) | set(args.calibration_groups)
    holdout_rows, holdout_labels, holdout_groups = extract_unsw(
        holdout_manifest, truth, selected, args
    )
    if not train_rows or not holdout_rows:
        parser.error("training and selected UNSW partitions must be non-empty")

    vectorizer = DictVectorizer(sparse=False)
    train_matrix = vectorizer.fit_transform(
        transform_feature_rows(train_rows, "invariant_no_ports_v1")
    ).astype(np.float32, copy=False)
    holdout_matrix = vectorizer.transform(
        transform_feature_rows(holdout_rows, "invariant_no_ports_v1")
    ).astype(np.float32, copy=False)
    train_labels_array = np.asarray(train_labels, dtype=np.int8)
    holdout_labels_array = np.asarray(holdout_labels, dtype=np.int8)
    adaptation_indices = np.asarray(
        [
            index
            for index, group in enumerate(holdout_groups)
            if group in set(args.adaptation_groups)
        ],
        dtype=np.int64,
    )
    calibration_indices = np.asarray(
        [
            index
            for index, group in enumerate(holdout_groups)
            if group in set(args.calibration_groups)
        ],
        dtype=np.int64,
    )
    fit_matrix = np.concatenate(
        (train_matrix, holdout_matrix[adaptation_indices]), axis=0
    )
    fit_labels = np.concatenate(
        (train_labels_array, holdout_labels_array[adaptation_indices]), axis=0
    )
    fit_groups = list(train_groups) + [
        holdout_groups[index] for index in adaptation_indices
    ]
    adaptation_mask = np.concatenate(
        (
            np.zeros(len(train_rows), dtype=np.int8),
            np.ones(len(adaptation_indices), dtype=np.int8),
        )
    )
    group_counts = Counter(fit_groups)
    sample_weight = np.asarray(
        [1.0 / group_counts[group] for group in fit_groups]
    )
    sample_weight *= np.where(
        adaptation_mask == 1, args.adaptation_weight_multiplier, 1.0
    )
    sample_weight *= len(sample_weight) / sample_weight.sum()

    models = []
    thresholds = []
    positive_indices = []
    calibration_labels = holdout_labels_array[calibration_indices]
    for seed in args.seeds:
        model = ExtraTreesClassifier(
            n_estimators=args.estimators,
            class_weight="balanced",
            random_state=seed,
            n_jobs=args.n_jobs,
            min_samples_leaf=2,
        )
        model.fit(fit_matrix, fit_labels, sample_weight=sample_weight)
        positive_index = list(model.classes_).index(1)
        probabilities = model.predict_proba(
            holdout_matrix[calibration_indices]
        )[:, positive_index]
        selection = select_macro_f1_threshold(
            calibration_labels.tolist(),
            probabilities.tolist(),
            min_attack_recall=args.calibration_attack_recall_floor,
        )
        models.append(model)
        thresholds.append(float(selection["threshold"]))
        positive_indices.append(int(positive_index))

    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "release_id": args.release_id,
        "candidate_id": args.candidate_id,
        "execution_mode": "fallback" if args.disable_deep else "normal",
        "deep_features_enabled": not args.disable_deep,
        "search_candidates": 10,
        "adaptation_groups": sorted(args.adaptation_groups),
        "calibration_groups": sorted(args.calibration_groups),
        "adaptation_weight_multiplier": args.adaptation_weight_multiplier,
        "calibration_attack_recall_floor": args.calibration_attack_recall_floor,
        "training_manifest_sha256": sha256(args.training_manifest),
        "holdout_manifest_sha256": sha256(args.holdout_manifest),
        "input_hash_manifest": (
            None
            if args.input_hash_manifest is None
            else str(args.input_hash_manifest)
        ),
        "input_hash_manifest_sha256": (
            None
            if args.input_hash_manifest is None
            else sha256(args.input_hash_manifest)
        ),
        "train_flows": len(train_rows),
        "adaptation_flows": len(adaptation_indices),
        "calibration_flows": len(calibration_indices),
        "feature_count": len(vectorizer.feature_names_),
        "seeds": args.seeds,
        "estimators_per_seed": args.estimators,
    }
    bundle = {
        "schema_version": 1,
        "candidate_id": args.candidate_id,
        "execution_mode": "fallback" if args.disable_deep else "normal",
        "feature_profile": "invariant_no_ports_v1",
        "classifier": "extra_trees",
        "vectorizer": vectorizer,
        "models": models,
        "thresholds": thresholds,
        "positive_indices": positive_indices,
        "metadata": metadata,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, args.output, compress=3)
    manifest_path = args.output.with_suffix(".manifest.json")
    manifest = dict(metadata)
    manifest.update(
        {
            "candidate_id": args.candidate_id,
            "feature_profile": "invariant_no_ports_v1",
            "classifier": "extra_trees",
            "thresholds": thresholds,
            "bundle": str(args.output),
            "bundle_sha256": sha256(args.output),
        }
    )
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
