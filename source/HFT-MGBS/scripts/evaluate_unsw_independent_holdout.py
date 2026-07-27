"""Train on grouped USTC captures and evaluate an exact-labeled UNSW holdout."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from hft_mgbs.candidate_dataset import extract_candidate_flow_records
from hft_mgbs.domain_features import (
    FEATURE_PROFILES,
    transform_feature_rows,
)
from hft_mgbs.quality import expected_calibration_error, minimum_metric
from hft_mgbs.unsw import UnswGroundTruth


def _threshold_metrics(labels, probabilities, threshold):
    true_positive = false_positive = true_negative = false_negative = 0
    for label, probability in zip(labels, probabilities):
        predicted = int(probability >= threshold)
        if label == 1 and predicted == 1:
            true_positive += 1
        elif label == 0 and predicted == 1:
            false_positive += 1
        elif label == 0 and predicted == 0:
            true_negative += 1
        else:
            false_negative += 1
    attack_denominator = 2 * true_positive + false_positive + false_negative
    benign_denominator = 2 * true_negative + false_positive + false_negative
    attack_f1 = (
        0.0
        if attack_denominator == 0
        else 2.0 * true_positive / attack_denominator
    )
    benign_f1 = (
        0.0
        if benign_denominator == 0
        else 2.0 * true_negative / benign_denominator
    )
    attack_total = true_positive + false_negative
    benign_total = true_negative + false_positive
    attack_recall = (
        0.0 if attack_total == 0 else true_positive / attack_total
    )
    benign_recall = (
        0.0 if benign_total == 0 else true_negative / benign_total
    )
    return {
        "threshold": float(threshold),
        "macro_f1": (attack_f1 + benign_f1) / 2.0,
        "balanced_accuracy": (attack_recall + benign_recall) / 2.0,
        "attack_recall": attack_recall,
        "benign_recall": benign_recall,
        "predicted_attack_ratio": (
            (true_positive + false_positive) / len(labels)
        ),
    }


def select_macro_f1_threshold(
    labels, probabilities, min_attack_recall=0.0
):
    """Select a threshold only from a labeled calibration partition."""

    if len(labels) != len(probabilities) or not labels:
        raise ValueError("calibration labels/probabilities must align")
    if not 0 < sum(labels) < len(labels):
        raise ValueError("calibration partition must contain both classes")
    if not 0.0 <= min_attack_recall <= 1.0:
        raise ValueError("minimum calibration attack recall must be in [0, 1]")
    thresholds = sorted(set(float(value) for value in probabilities))
    thresholds.append(max(thresholds) + 1e-12)
    candidates = [
        _threshold_metrics(labels, probabilities, threshold)
        for threshold in thresholds
    ]
    feasible = [
        item
        for item in candidates
        if item["attack_recall"] >= min_attack_recall
    ]
    selected = max(
        feasible,
        key=lambda item: (
            item["macro_f1"],
            item["balanced_accuracy"],
            -abs(item["threshold"] - 0.5),
        ),
    )
    selected["minimum_attack_recall_constraint"] = (
        min_attack_recall
    )
    return selected


def load_input_hash_evidence(path, required_paths):
    if path is None:
        return None
    with path.open("rb") as handle:
        raw = handle.read()
    payload = json.loads(raw.decode("utf-8"))
    entries = {
        str(Path(item["path"]).resolve()): item
        for item in payload.get("entries", [])
    }
    required = {str(Path(item).resolve()) for item in required_paths}
    missing = sorted(required - set(entries))
    if missing:
        raise ValueError(
            "input hash manifest is missing required paths: {}".format(
                ", ".join(missing)
            )
        )
    return {
        "path": str(path.resolve()),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "entry_count": len(entries),
        "required_path_count": len(required),
        "all_required_paths_frozen": True,
    }


def constraint_audit(summaries):
    key_total = sum(item["key_flow_total"] for item in summaries)
    return {
        "budget_overrun_count": sum(
            item["budget_overrun_count"] for item in summaries
        ),
        "key_flow_coverage": 1.0
        if key_total == 0
        else sum(item["key_flow_covered"] for item in summaries) / key_total,
        "key_flow_coverage_min": min(
            item["key_flow_coverage_min"] for item in summaries
        ),
        "max_actual_optional_cost_us": max(
            item["max_actual_optional_cost_us"] for item in summaries
        ),
    }


def train_and_score(
    train_rows,
    train_labels,
    train_groups,
    test_rows,
    test_labels,
    seeds,
    estimators,
    n_jobs,
    test_groups=None,
    calibration_groups=(),
    adaptation_groups=(),
    adaptation_policy="none",
    adaptation_weight_multiplier=1.0,
    threshold_policy="fixed",
    calibration_attack_recall_floor=0.0,
    feature_profile="raw",
    classifier="extra_trees",
):
    import numpy as np
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (
        average_precision_score,
        balanced_accuracy_score,
        f1_score,
        recall_score,
        roc_auc_score,
    )

    projected_train_rows = transform_feature_rows(
        train_rows, feature_profile
    )
    projected_test_rows = transform_feature_rows(
        test_rows, feature_profile
    )
    vectorizer = DictVectorizer(sparse=False)
    train_matrix = vectorizer.fit_transform(
        projected_train_rows
    ).astype(
        np.float32, copy=False
    )
    test_matrix = vectorizer.transform(projected_test_rows).astype(
        np.float32, copy=False
    )
    y_train = np.asarray(train_labels, dtype=np.int8)
    y_test = np.asarray(test_labels, dtype=np.int8)
    test_groups = list(test_groups or ["holdout"] * len(test_labels))
    if len(test_groups) != len(test_labels):
        raise ValueError("test groups must align with test labels")
    calibration_group_set = set(calibration_groups)
    adaptation_group_set = set(adaptation_groups)
    if calibration_group_set & adaptation_group_set:
        raise ValueError(
            "adaptation and calibration groups must be disjoint"
        )
    if adaptation_policy == "none" and adaptation_group_set:
        raise ValueError(
            "adaptation groups require a non-none adaptation policy"
        )
    if (
        adaptation_policy == "calibration_weighted"
        and not adaptation_group_set
    ):
        raise ValueError(
            "calibration_weighted adaptation requires adaptation groups"
        )
    if adaptation_policy not in {"none", "calibration_weighted"}:
        raise ValueError("unsupported adaptation policy")
    if adaptation_weight_multiplier <= 0:
        raise ValueError("adaptation weight multiplier must be positive")
    adaptation_indices = np.asarray(
        [
            index
            for index, group in enumerate(test_groups)
            if group in adaptation_group_set
        ],
        dtype=np.int64,
    )
    excluded_from_evaluation = (
        calibration_group_set | adaptation_group_set
    )
    if threshold_policy == "calibration_macro_f1":
        calibration_indices = np.asarray(
            [
                index
                for index, group in enumerate(test_groups)
                if group in calibration_group_set
            ],
            dtype=np.int64,
        )
        evaluation_indices = np.asarray(
            [
                index
                for index, group in enumerate(test_groups)
                if group not in excluded_from_evaluation
            ],
            dtype=np.int64,
        )
        if not len(calibration_indices) or not len(evaluation_indices):
            raise ValueError(
                "calibration and evaluation partitions must both be non-empty"
            )
        if not 0 < int(y_test[calibration_indices].sum()) < len(
            calibration_indices
        ):
            raise ValueError("calibration partition must contain both classes")
        if not 0 < int(y_test[evaluation_indices].sum()) < len(
            evaluation_indices
        ):
            raise ValueError("evaluation partition must contain both classes")
    elif threshold_policy == "fixed":
        calibration_indices = np.asarray(
            [
                index
                for index, group in enumerate(test_groups)
                if group in calibration_group_set
            ],
            dtype=np.int64,
        )
        evaluation_indices = np.asarray(
            [
                index
                for index, group in enumerate(test_groups)
                if group not in excluded_from_evaluation
            ],
            dtype=np.int64,
        )
        if not len(evaluation_indices):
            raise ValueError("evaluation partition must be non-empty")
        if not 0 < int(y_test[evaluation_indices].sum()) < len(
            evaluation_indices
        ):
            raise ValueError("evaluation partition must contain both classes")
    else:
        raise ValueError("unsupported threshold policy")
    if len(adaptation_indices) and not (
        0 < int(y_test[adaptation_indices].sum()) < len(adaptation_indices)
    ):
        raise ValueError("adaptation partition must contain both classes")
    fit_matrix = train_matrix
    fit_labels = y_train
    fit_groups = list(train_groups)
    adaptation_row_mask = np.zeros(len(train_rows), dtype=np.int8)
    if adaptation_policy == "calibration_weighted":
        fit_matrix = np.concatenate(
            (train_matrix, test_matrix[adaptation_indices]), axis=0
        )
        fit_labels = np.concatenate(
            (y_train, y_test[adaptation_indices]), axis=0
        )
        fit_groups.extend(test_groups[index] for index in adaptation_indices)
        adaptation_row_mask = np.concatenate(
            (
                adaptation_row_mask,
                np.ones(len(adaptation_indices), dtype=np.int8),
            )
        )
    if classifier == "logistic":
        from sklearn.preprocessing import StandardScaler

        scaler = StandardScaler()
        fit_matrix = scaler.fit_transform(fit_matrix)
        test_matrix = scaler.transform(test_matrix)
    group_counts = Counter(fit_groups)
    sample_weight = np.asarray(
        [1.0 / group_counts[group] for group in fit_groups]
    )
    sample_weight *= np.where(
        adaptation_row_mask == 1, adaptation_weight_multiplier, 1.0
    )
    sample_weight *= len(sample_weight) / sample_weight.sum()
    results = []
    for seed in seeds:
        if classifier == "extra_trees":
            model = ExtraTreesClassifier(
                n_estimators=estimators,
                class_weight="balanced",
                random_state=seed,
                n_jobs=n_jobs,
                min_samples_leaf=2,
            )
            classifier_metadata = {
                "name": "ExtraTreesClassifier",
                "n_estimators": estimators,
                "min_samples_leaf": 2,
                "class_weight": "balanced",
            }
        elif classifier == "logistic":
            model = LogisticRegression(
                class_weight="balanced",
                random_state=seed,
                max_iter=2000,
                solver="liblinear",
            )
            classifier_metadata = {
                "name": "LogisticRegression",
                "solver": "liblinear",
                "max_iter": 2000,
                "class_weight": "balanced",
                "standard_scaler": True,
            }
        else:
            raise ValueError("unsupported classifier")
        model.fit(fit_matrix, fit_labels, sample_weight=sample_weight)
        positive_index = list(model.classes_).index(1)
        probabilities = model.predict_proba(test_matrix)[:, positive_index]
        calibration_selection = None
        threshold = 0.5
        if threshold_policy == "calibration_macro_f1":
            calibration_selection = select_macro_f1_threshold(
                y_test[calibration_indices].tolist(),
                probabilities[calibration_indices].tolist(),
                min_attack_recall=calibration_attack_recall_floor,
            )
            threshold = calibration_selection["threshold"]
        evaluation_labels = y_test[evaluation_indices]
        evaluation_probabilities = probabilities[evaluation_indices]
        predictions = (
            evaluation_probabilities >= threshold
        ).astype(np.int8)
        result = {
                "seed": seed,
                "decision_threshold": float(threshold),
                "macro_f1": float(
                    f1_score(
                        evaluation_labels, predictions, average="macro"
                    )
                ),
                "balanced_accuracy": float(
                    balanced_accuracy_score(
                        evaluation_labels, predictions
                    )
                ),
                "auroc": float(
                    roc_auc_score(
                        evaluation_labels, evaluation_probabilities
                    )
                ),
                "auprc": float(
                    average_precision_score(
                        evaluation_labels, evaluation_probabilities
                    )
                ),
                "ece": expected_calibration_error(
                    evaluation_labels.tolist(),
                    evaluation_probabilities.tolist(),
                ),
                "benign_recall": float(
                    recall_score(
                        evaluation_labels, predictions, pos_label=0
                    )
                ),
                "attack_recall": float(
                    recall_score(
                        evaluation_labels, predictions, pos_label=1
                    )
                ),
                "predicted_attack_ratio": float(predictions.mean()),
            }
        if calibration_selection is not None:
            result["calibration_selection"] = calibration_selection
        results.append(result)
    return {
        "classifier": classifier_metadata,
        "feature_profile": feature_profile,
        "threshold_policy": threshold_policy,
        "calibration_used_for_threshold": (
            threshold_policy == "calibration_macro_f1"
        ),
        "calibration_attack_recall_floor": (
            calibration_attack_recall_floor
        ),
        "calibration_groups": sorted(calibration_group_set),
        "adaptation_policy": adaptation_policy,
        "adaptation_groups": sorted(adaptation_group_set),
        "adaptation_weight_multiplier": adaptation_weight_multiplier,
        "evaluation_groups": sorted(
            set(test_groups) - excluded_from_evaluation
        ),
        "feature_count": len(vectorizer.feature_names_),
        "train_flow_count": len(train_rows),
        "adaptation_flow_count": len(adaptation_indices),
        "fit_flow_count": len(fit_labels),
        "calibration_flow_count": len(calibration_indices),
        "test_flow_count": len(evaluation_indices),
        "test_attack_count": int(y_test[evaluation_indices].sum()),
        "test_benign_count": (
            len(evaluation_indices)
            - int(y_test[evaluation_indices].sum())
        ),
        "seeds": results,
        "conservative": {
            "macro_f1_min": minimum_metric(results, "macro_f1"),
            "balanced_accuracy_min": minimum_metric(
                results, "balanced_accuracy"
            ),
            "auroc_min": minimum_metric(results, "auroc"),
            "auprc_min": minimum_metric(results, "auprc"),
            "benign_recall_min": minimum_metric(results, "benign_recall"),
            "attack_recall_min": minimum_metric(results, "attack_recall"),
            "ece_max": max(item["ece"] for item in results),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("training_manifest", type=Path)
    parser.add_argument("holdout_manifest", type=Path)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--budget-us", type=float, default=5000.0)
    parser.add_argument(
        "--execution-budget-safety-ratio", type=float, default=0.75
    )
    parser.add_argument("--disable-deep", action="store_true")
    parser.add_argument("--key-flow-ratio", type=float, default=0.10)
    parser.add_argument("--max-payload-bytes", type=int, default=256)
    parser.add_argument("--max-train-packets-per-capture", type=int, default=20000)
    parser.add_argument("--max-train-flows-per-capture", type=int, default=2000)
    parser.add_argument("--max-test-packets-per-capture", type=int, default=50000)
    parser.add_argument("--max-test-flows-per-capture", type=int, default=5000)
    parser.add_argument("--tolerance-s", type=float, default=0.0)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 11, 19])
    parser.add_argument("--estimators", type=int, default=200)
    parser.add_argument("--n-jobs", type=int, default=8)
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help=(
            "Omit per-capture records while retaining aggregate constraints "
            "and quality metrics."
        ),
    )
    parser.add_argument("--input-hash-manifest", type=Path)
    parser.add_argument(
        "--threshold-policy",
        choices=("fixed", "calibration_macro_f1"),
        default="fixed",
    )
    parser.add_argument("--calibration-groups", nargs="*", default=[])
    parser.add_argument("--adaptation-groups", nargs="*", default=[])
    parser.add_argument(
        "--adaptation-policy",
        choices=("none", "calibration_weighted"),
        default="none",
    )
    parser.add_argument(
        "--adaptation-weight-multiplier", type=float, default=1.0
    )
    parser.add_argument(
        "--calibration-attack-recall-floor", type=float, default=0.0
    )
    parser.add_argument(
        "--feature-profile",
        choices=FEATURE_PROFILES,
        default="raw",
    )
    parser.add_argument(
        "--classifier",
        choices=("extra_trees", "logistic"),
        default="extra_trees",
    )
    args = parser.parse_args()
    if not 0 < args.execution_budget_safety_ratio <= 1:
        parser.error("--execution-budget-safety-ratio must be in (0, 1]")
    if not 0 <= args.calibration_attack_recall_floor <= 1:
        parser.error(
            "--calibration-attack-recall-floor must be in [0, 1]"
        )
    if args.adaptation_weight_multiplier <= 0:
        parser.error("--adaptation-weight-multiplier must be positive")
    with args.training_manifest.open("r", encoding="utf-8") as handle:
        training_manifest = json.load(handle)
    with args.holdout_manifest.open("r", encoding="utf-8") as handle:
        holdout_manifest = json.load(handle)
    available_holdout_groups = {
        sample["group"] for sample in holdout_manifest["samples"]
    }
    unknown_calibration_groups = (
        set(args.calibration_groups) - available_holdout_groups
    )
    unknown_adaptation_groups = (
        set(args.adaptation_groups) - available_holdout_groups
    )
    if unknown_calibration_groups:
        parser.error(
            "unknown calibration groups: {}".format(
                ", ".join(sorted(unknown_calibration_groups))
            )
        )
    if unknown_adaptation_groups:
        parser.error(
            "unknown adaptation groups: {}".format(
                ", ".join(sorted(unknown_adaptation_groups))
            )
        )
    if set(args.calibration_groups) & set(args.adaptation_groups):
        parser.error(
            "--calibration-groups and --adaptation-groups must be disjoint"
        )
    if args.adaptation_policy == "none" and args.adaptation_groups:
        parser.error(
            "--adaptation-groups requires --adaptation-policy "
            "calibration_weighted"
        )
    if (
        args.adaptation_policy == "calibration_weighted"
        and not args.adaptation_groups
    ):
        parser.error(
            "--adaptation-policy calibration_weighted requires "
            "--adaptation-groups"
        )
    if (
        args.threshold_policy == "calibration_macro_f1"
        and not args.calibration_groups
    ):
        parser.error(
            "--calibration-groups is required for calibration policy"
        )
    required_input_paths = [
        args.training_manifest,
        args.holdout_manifest,
        holdout_manifest["ground_truth_csv"],
    ]
    required_input_paths.extend(
        sample["path"] for sample in training_manifest["samples"]
    )
    required_input_paths.extend(
        sample["path"] for sample in holdout_manifest["samples"]
    )
    try:
        input_hash_evidence = load_input_hash_evidence(
            args.input_hash_manifest, required_input_paths
        )
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    truth = UnswGroundTruth.from_csv(
        Path(holdout_manifest["ground_truth_csv"])
    )

    train_rows = []
    train_labels = []
    train_groups = []
    train_summaries = []
    for sample in training_manifest["samples"]:
        records, summary = extract_candidate_flow_records(
            sample["path"],
            sample["group"],
            batch_size=args.batch_size,
            budget_us=args.budget_us,
            allow_deep=not args.disable_deep,
            key_flow_ratio=args.key_flow_ratio,
            max_payload_bytes=args.max_payload_bytes,
            max_packets=args.max_train_packets_per_capture,
            max_flows=args.max_train_flows_per_capture,
            execution_budget_safety_ratio=(
                args.execution_budget_safety_ratio
            ),
        )
        train_rows.extend(item["features"] for item in records)
        train_labels.extend([int(sample["label"])] * len(records))
        train_groups.extend([sample["group"]] * len(records))
        train_summaries.append(summary)

    test_rows = []
    test_labels = []
    test_groups = []
    test_summaries = []
    eligible_event_ids = set()
    matched_event_ids = set()
    eligible_event_ids_by_group = defaultdict(set)
    matched_event_ids_by_group = defaultdict(set)
    for sample in holdout_manifest["samples"]:
        def observe_flow(record):
            for interval in truth.matching_intervals(
                tuple(record["forward_key"]),
                float(record["start_timestamp"]),
                float(record["last_timestamp"]),
                tolerance_s=args.tolerance_s,
            ):
                if interval.event_id >= 0:
                    matched_event_ids.add(interval.event_id)
                    matched_event_ids_by_group[sample["group"]].add(
                        interval.event_id
                    )

        records, summary = extract_candidate_flow_records(
            sample["path"],
            sample["group"],
            batch_size=args.batch_size,
            budget_us=args.budget_us,
            allow_deep=not args.disable_deep,
            key_flow_ratio=args.key_flow_ratio,
            max_payload_bytes=args.max_payload_bytes,
            max_packets=args.max_test_packets_per_capture,
            max_flows=args.max_test_flows_per_capture,
            execution_budget_safety_ratio=(
                args.execution_budget_safety_ratio
            ),
            flow_record_observer=observe_flow,
        )
        if (
            summary["packet_start_timestamp"] is not None
            and summary["packet_last_timestamp"] is not None
        ):
            group_event_ids = truth.event_ids_overlapping(
                    summary["packet_start_timestamp"],
                    summary["packet_last_timestamp"],
                    tolerance_s=args.tolerance_s,
                )
            eligible_event_ids.update(group_event_ids)
            eligible_event_ids_by_group[sample["group"]].update(
                group_event_ids
            )
        labels = [
            truth.label_flow_record(
                record, tolerance_s=args.tolerance_s
            )
            for record in records
        ]
        test_rows.extend(item["features"] for item in records)
        test_labels.extend(labels)
        test_groups.extend([sample["group"]] * len(records))
        summary = dict(summary)
        summary["attack_flows"] = sum(labels)
        summary["benign_flows"] = len(labels) - sum(labels)
        test_summaries.append(summary)
    if not test_labels or not 0 < sum(test_labels) < len(test_labels):
        parser.error("holdout extraction must contain both attack and benign flows")

    quality = train_and_score(
        train_rows,
        train_labels,
        train_groups,
        test_rows,
        test_labels,
        args.seeds,
        args.estimators,
        args.n_jobs,
        test_groups=test_groups,
        calibration_groups=args.calibration_groups,
        adaptation_groups=args.adaptation_groups,
        adaptation_policy=args.adaptation_policy,
        adaptation_weight_multiplier=(
            args.adaptation_weight_multiplier
        ),
        threshold_policy=args.threshold_policy,
        calibration_attack_recall_floor=(
            args.calibration_attack_recall_floor
        ),
        feature_profile=args.feature_profile,
        classifier=args.classifier,
    )
    calibration_group_set = set(args.calibration_groups)
    adaptation_group_set = set(args.adaptation_groups)
    evaluation_group_set = (
        available_holdout_groups
        - calibration_group_set
        - adaptation_group_set
    )
    evaluation_eligible_event_ids = set().union(
        *(
            eligible_event_ids_by_group[group]
            for group in evaluation_group_set
        )
    )
    evaluation_matched_event_ids = set().union(
        *(
            matched_event_ids_by_group[group]
            for group in evaluation_group_set
        )
    )
    event_recall = (
        1.0
        if not evaluation_eligible_event_ids
        else len(
            evaluation_matched_event_ids
            & evaluation_eligible_event_ids
        )
        / len(evaluation_eligible_event_ids)
    )
    calibration_eligible_event_ids = set().union(
        *(
            eligible_event_ids_by_group[group]
            for group in calibration_group_set
        )
    )
    calibration_matched_event_ids = set().union(
        *(
            matched_event_ids_by_group[group]
            for group in calibration_group_set
        )
    )
    evaluation_test_summaries = [
        summary
        for summary in test_summaries
        if summary["group"] in evaluation_group_set
    ]
    calibration_test_summaries = [
        summary
        for summary in test_summaries
        if summary["group"] in calibration_group_set
    ]
    adaptation_test_summaries = [
        summary
        for summary in test_summaries
        if summary["group"] in adaptation_group_set
    ]
    missing_final_evidence = ["frozen_min_primary_metric"]
    if input_hash_evidence is None:
        missing_final_evidence.insert(0, "frozen_input_sha256")
    output = {
        "schema_version": 1,
        "scope": "independent_cross_dataset_holdout",
        "candidate": {
            "mode": "fallback" if args.disable_deep else "normal",
            "batch_size": args.batch_size,
            "budget_us": args.budget_us,
            "execution_budget_safety_ratio": (
                args.execution_budget_safety_ratio
            ),
        },
        "protocol": {
            "training_dataset": "USTC-TFC2016",
            "holdout_dataset": "UNSW-NB15",
            "dataset_overlap": (
                "no_capture_overlap_between_fit_calibration_evaluation"
                if adaptation_group_set
                else "none"
            ),
            "holdout_label_alignment": (
                "bidirectional_5tuple_and_flow_attack_time_overlap"
            ),
            "alignment_tolerance_s": args.tolerance_s,
            "seeds": args.seeds,
            "threshold_policy": args.threshold_policy,
            "calibration_used_for_threshold": (
                args.threshold_policy == "calibration_macro_f1"
            ),
            "calibration_attack_recall_floor": (
                args.calibration_attack_recall_floor
            ),
            "feature_profile": args.feature_profile,
            "classifier": args.classifier,
            "calibration_groups": sorted(args.calibration_groups),
            "adaptation_policy": args.adaptation_policy,
            "adaptation_groups": sorted(args.adaptation_groups),
            "adaptation_weight_multiplier": (
                args.adaptation_weight_multiplier
            ),
            "evaluation_groups": sorted(
                evaluation_group_set
            ),
        },
        "ground_truth": {
            **truth.parse_stats,
            "indexed_key_count": truth.indexed_key_count,
        },
        "input_hash_evidence": input_hash_evidence,
        "capture_counts": {
            "training": len(train_summaries),
            "calibration": len(calibration_test_summaries),
            "adaptation": len(adaptation_test_summaries),
            "holdout": len(evaluation_test_summaries),
        },
        "training_constraint_audit": constraint_audit(train_summaries),
        "holdout_constraint_audit": constraint_audit(
            evaluation_test_summaries
        ),
        "ground_truth_event_recall_audit": {
            "scope": (
                "indexed_tcp_udp_events_overlapping_processed_packet_time"
            ),
            "eligible_event_count": len(
                evaluation_eligible_event_ids
            ),
            "matched_event_count": len(
                evaluation_matched_event_ids
                & evaluation_eligible_event_ids
            ),
            "event_recall": event_recall,
            "computed_before_flow_sampling": True,
        },
        "quality": quality,
        "final_quality_eligible": False,
        "missing_final_evidence": missing_final_evidence,
    }
    if calibration_test_summaries:
        output["calibration_constraint_audit"] = constraint_audit(
            calibration_test_summaries
        )
        output["calibration_ground_truth_event_recall_audit"] = {
            "eligible_event_count": len(
                calibration_eligible_event_ids
            ),
            "matched_event_count": len(
                calibration_matched_event_ids
                & calibration_eligible_event_ids
            ),
            "event_recall": (
                1.0
                if not calibration_eligible_event_ids
                else len(
                    calibration_matched_event_ids
                    & calibration_eligible_event_ids
                )
                / len(calibration_eligible_event_ids)
            ),
            "used_for_final_evaluation": False,
        }
    if adaptation_test_summaries:
        output["adaptation_constraint_audit"] = constraint_audit(
            adaptation_test_summaries
        )
    if not args.summary_only:
        output["training_captures"] = train_summaries
        output["holdout_captures"] = evaluation_test_summaries
        if calibration_test_summaries:
            output["calibration_captures"] = (
                calibration_test_summaries
            )
        if adaptation_test_summaries:
            output["adaptation_captures"] = adaptation_test_summaries
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
