"""Grouped PCAP-level quality probe for a budget-scheduled feature candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from hft_mgbs import AdaptiveExtractionPipeline, PcapFileReader
from hft_mgbs.quality import expected_calibration_error, minimum_metric


def is_key_flow(flow_key, ratio):
    if ratio <= 0:
        return False
    digest = hashlib.sha256(repr(flow_key).encode("utf-8")).digest()
    value = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
    return value < ratio


def packet_batches(iterator, batch_size, max_packets):
    batch = []
    emitted = 0
    for packet in iterator:
        if max_packets and emitted >= max_packets:
            break
        batch.append(packet)
        emitted += 1
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def extract_capture(sample, args):
    pipeline = AdaptiveExtractionPipeline()
    records = {}
    tier_rank = {"base": 0, "flow": 1, "deep": 2}
    with PcapFileReader(sample["path"], max_payload_bytes=args.max_payload_bytes) as reader:
        for packet_batch in packet_batches(reader, args.batch_size, args.max_packets_per_capture):
            flow_keys = {pipeline.extractor.canonical_key(packet) for packet in packet_batch}
            key_flows = {key for key in flow_keys if is_key_flow(key, args.key_flow_ratio)}
            for result in pipeline.process_batch(
                packet_batch,
                budget_us=args.budget_us,
                allow_deep=not args.disable_deep,
                key_flows=key_flows,
            ):
                record = records.setdefault(result.flow_key, {})
                record.update(result.features)
                rank = tier_rank[result.tier]
                record["quality_seen_flow_tier"] = max(
                    record.get("quality_seen_flow_tier", 0.0), float(rank >= 1)
                )
                record["quality_seen_deep_tier"] = max(
                    record.get("quality_seen_deep_tier", 0.0), float(rank >= 2)
                )
        stats = reader.stats
    selected = sorted(
        records.items(),
        key=lambda item: hashlib.sha256(
            (sample["group"] + repr(item[0])).encode("utf-8")
        ).digest(),
    )[: args.max_flows_per_capture]
    return [record for _, record in selected], {
        "group": sample["group"],
        "label": sample["label"],
        "path": sample["path"],
        "parsed_packets": stats.parsed_packets,
        "flow_records": len(records),
        "selected_flows": len(selected),
    }


def grouped_probe(feature_rows, labels, groups, seeds, folds, estimators, n_jobs):
    import numpy as np
    from sklearn.ensemble import ExtraTreesClassifier
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.metrics import (
        average_precision_score,
        balanced_accuracy_score,
        f1_score,
        roc_auc_score,
    )
    from sklearn.model_selection import StratifiedGroupKFold

    vectorizer = DictVectorizer(sparse=False)
    matrix = vectorizer.fit_transform(feature_rows).astype(np.float32, copy=False)
    y = np.asarray(labels, dtype=np.int8)
    group_array = np.asarray(groups)
    group_counts = Counter(groups)
    sample_weight = np.asarray([1.0 / group_counts[group] for group in groups])
    sample_weight *= len(sample_weight) / sample_weight.sum()
    seed_results = []
    for seed in seeds:
        probabilities = np.zeros(len(y), dtype=np.float64)
        splitter = StratifiedGroupKFold(
            n_splits=folds, shuffle=True, random_state=seed
        )
        fold_groups = []
        for train_index, test_index in splitter.split(matrix, y, group_array):
            model = ExtraTreesClassifier(
                n_estimators=estimators,
                class_weight="balanced",
                random_state=seed,
                n_jobs=n_jobs,
                min_samples_leaf=2,
            )
            model.fit(
                matrix[train_index],
                y[train_index],
                sample_weight=sample_weight[train_index],
            )
            positive_index = list(model.classes_).index(1)
            probabilities[test_index] = model.predict_proba(matrix[test_index])[
                :, positive_index
            ]
            fold_groups.append(sorted(set(group_array[test_index].tolist())))
        predictions = (probabilities >= 0.5).astype(np.int8)
        group_accuracies = []
        for group in sorted(set(groups)):
            mask = group_array == group
            group_accuracies.append(float(np.mean(predictions[mask] == y[mask])))
        seed_results.append(
            {
                "seed": seed,
                "macro_f1": float(f1_score(y, predictions, average="macro")),
                "balanced_accuracy": float(balanced_accuracy_score(y, predictions)),
                "auroc": float(roc_auc_score(y, probabilities)),
                "auprc": float(average_precision_score(y, probabilities)),
                "ece": expected_calibration_error(y.tolist(), probabilities.tolist()),
                "capture_balanced_accuracy": sum(group_accuracies)
                / len(group_accuracies),
                "test_groups_by_fold": fold_groups,
            }
        )
    return {
        "classifier": {
            "name": "ExtraTreesClassifier",
            "n_estimators": estimators,
            "min_samples_leaf": 2,
            "class_weight": "balanced",
        },
        "feature_count": len(vectorizer.feature_names_),
        "flow_sample_count": len(feature_rows),
        "seeds": seed_results,
        "conservative": {
            "macro_f1_min": minimum_metric(seed_results, "macro_f1"),
            "balanced_accuracy_min": minimum_metric(
                seed_results, "balanced_accuracy"
            ),
            "auroc_min": minimum_metric(seed_results, "auroc"),
            "auprc_min": minimum_metric(seed_results, "auprc"),
            "capture_balanced_accuracy_min": minimum_metric(
                seed_results, "capture_balanced_accuracy"
            ),
            "ece_max": max(item["ece"] for item in seed_results),
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--budget-us", type=float, default=5000.0)
    parser.add_argument("--disable-deep", action="store_true")
    parser.add_argument("--key-flow-ratio", type=float, default=0.10)
    parser.add_argument("--max-payload-bytes", type=int, default=256)
    parser.add_argument("--max-packets-per-capture", type=int, default=20000)
    parser.add_argument("--max-flows-per-capture", type=int, default=2000)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 11, 19])
    parser.add_argument("--estimators", type=int, default=200)
    parser.add_argument("--n-jobs", type=int, default=8)
    args = parser.parse_args()
    with args.manifest.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    samples = manifest.get("samples", [])
    if not samples or len({sample["label"] for sample in samples}) != 2:
        parser.error("manifest must contain samples from exactly two labels")
    if args.folds < 2:
        parser.error("--folds must be at least 2")

    feature_rows = []
    labels = []
    groups = []
    capture_summaries = []
    for sample in samples:
        rows, summary = extract_capture(sample, args)
        feature_rows.extend(rows)
        labels.extend([int(sample["label"])] * len(rows))
        groups.extend([sample["group"]] * len(rows))
        capture_summaries.append(summary)
    probe = grouped_probe(
        feature_rows,
        labels,
        groups,
        args.seeds,
        args.folds,
        args.estimators,
        args.n_jobs,
    )
    output = {
        "schema_version": 1,
        "scope": "offline_grouped_quality_probe",
        "candidate": {
            "mode": "fallback" if args.disable_deep else "normal",
            "batch_size": args.batch_size,
            "budget_us": args.budget_us,
            "key_flow_ratio": args.key_flow_ratio,
        },
        "protocol": {
            "split_unit": "whole_pcap_capture_group",
            "splitter": "StratifiedGroupKFold",
            "folds": args.folds,
            "seeds": args.seeds,
            "max_packets_per_capture": args.max_packets_per_capture,
            "max_flows_per_capture": args.max_flows_per_capture,
            "leakage_guard": "no capture group appears in both train and test within a fold",
        },
        "captures": capture_summaries,
        "quality": probe,
        "final_quality_eligible": False,
        "missing_final_evidence": [
            "full_corpus_or_frozen_sampling_manifest",
            "frozen_min_primary_metric",
            "independent_holdout_or_temporal_test",
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
