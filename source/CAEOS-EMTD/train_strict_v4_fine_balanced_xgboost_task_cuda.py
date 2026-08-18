from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from caeos.data import prepare_tabular_open_set
from strict_v4_cicids2017_attack_family import (
    FINE_TO_FAMILY as CICIDS2017_FINE_TO_FAMILY,
    atomic_json,
    canonical_hash,
    file_hash,
)
from strict_v4_cic_iot2023_attack_family import (
    FINE_TO_FAMILY as CIC_IOT2023_FINE_TO_FAMILY,
)
from train_strict_v4_flow_statistic_xgboost_task_cuda import booster_uses_cuda
from train_strict_v4_packet_sequence_fusion_task_cuda import (
    GPUSampler,
    benign_prototype_distance,
    class_weights,
    prototype_distance,
    query_gpu,
    tail_percentile,
)


BENIGN_CLASS = "Benign"
TAXONOMIES = {
    "cicids2017": CICIDS2017_FINE_TO_FAMILY,
    "cic_iot2023": CIC_IOT2023_FINE_TO_FAMILY,
}


def fine_classes_for_family(
    family: str,
    taxonomy: str = "cicids2017",
) -> list[str]:
    if taxonomy not in TAXONOMIES:
        raise ValueError(f"unsupported attack taxonomy: {taxonomy}")
    mapping = TAXONOMIES[taxonomy]
    values = sorted(
        fine_class
        for fine_class, mapped_family in mapping.items()
        if mapped_family == family and fine_class != BENIGN_CLASS
    )
    if not values:
        raise ValueError(f"unknown {taxonomy} attack family: {family}")
    return values


def features(dataset: Any) -> np.ndarray:
    return np.concatenate([view.numpy() for view in dataset.views], axis=1)


def labels(dataset: Any) -> np.ndarray:
    return np.asarray(dataset.labels.numpy(), dtype=np.int64)


def unknown_flags(dataset: Any) -> np.ndarray:
    return np.asarray(dataset.is_unknown.numpy(), dtype=bool)


def family_labels(
    labels_value: np.ndarray,
    fine_class_names: list[str],
    mapping: dict[str, str],
) -> tuple[np.ndarray, list[str], int]:
    missing = sorted(set(fine_class_names) - set(mapping))
    if missing:
        raise ValueError(f"fine classes are missing taxonomy entries: {missing}")
    family_class_names = sorted(
        {mapping[name] for name in fine_class_names},
        key=lambda name: (name != BENIGN_CLASS, name),
    )
    family_index = {
        name: index for index, name in enumerate(family_class_names)
    }
    lookup = np.asarray(
        [family_index[mapping[name]] for name in fine_class_names],
        dtype=np.int64,
    )
    source = np.asarray(labels_value, dtype=np.int64)
    remapped = source.copy()
    known = source >= 0
    remapped[known] = lookup[source[known]]
    return remapped, family_class_names, family_index[BENIGN_CLASS]


def attack_probability_variants(
    family_probability: np.ndarray,
    binary_probability: np.ndarray,
    benign_index: int,
) -> dict[str, np.ndarray]:
    family_attack = 1.0 - np.asarray(
        family_probability[:, benign_index], dtype=np.float64
    )
    binary_attack = np.asarray(binary_probability, dtype=np.float64)
    return {
        "family": family_attack,
        "binary": binary_attack,
        "maximum": np.maximum(family_attack, binary_attack),
        "noisy_or": 1.0 - (1.0 - family_attack) * (1.0 - binary_attack),
    }


def split_counts(
    split_labels: np.ndarray,
    split_unknown: np.ndarray,
    class_names: list[str],
    unknown_family: str,
) -> dict[str, int]:
    identities = [
        unknown_family if is_unknown else class_names[int(label)]
        for label, is_unknown in zip(
            split_labels.tolist(), split_unknown.tolist()
        )
    ]
    return dict(sorted(Counter(identities).items()))


def train_task(args: argparse.Namespace) -> dict[str, Any]:
    if str(args.xgboost_root.resolve()) not in sys.path:
        sys.path.insert(0, str(args.xgboost_root.resolve()))
    from xgboost import XGBClassifier

    random.seed(args.seed)
    np.random.seed(args.seed)
    cache_csv = args.cache_csv.resolve()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    taxonomy_mapping = TAXONOMIES[args.taxonomy]
    unknown_fine_classes = fine_classes_for_family(
        args.unknown_family,
        args.taxonomy,
    )
    bundle = prepare_tabular_open_set(
        csv_path=str(cache_csv),
        config=config,
        unknown_classes=unknown_fine_classes,
        benign_class=BENIGN_CLASS,
        max_per_class=args.max_per_class,
        chunksize=args.chunksize,
        seed=args.seed,
        split_strategy="capture_grouped",
    )
    fine_class_names = [str(value) for value in bundle.class_names]
    x_train = features(bundle.train)
    x_validation = features(bundle.validation)
    x_test = features(bundle.test)
    y_train = labels(bundle.train)
    y_validation = labels(bundle.validation)
    test_labels = labels(bundle.test)
    if args.classification_level == "family":
        y_train, known_class_names, benign_index = family_labels(
            y_train,
            fine_class_names,
            taxonomy_mapping,
        )
        y_validation, validation_class_names, validation_benign_index = (
            family_labels(
                y_validation,
                fine_class_names,
                taxonomy_mapping,
            )
        )
        test_labels, test_class_names, test_benign_index = family_labels(
            test_labels,
            fine_class_names,
            taxonomy_mapping,
        )
        if (
            validation_class_names != known_class_names
            or test_class_names != known_class_names
            or validation_benign_index != benign_index
            or test_benign_index != benign_index
        ):
            raise ValueError("family label remapping drifted across splits")
    else:
        known_class_names = fine_class_names
        benign_index = int(bundle.benign_index)
    validation_unknown = unknown_flags(bundle.validation)
    test_unknown = unknown_flags(bundle.test)
    if validation_unknown.any() or (test_labels[test_unknown] != -1).any():
        raise ValueError("open-set label isolation invariant failed")
    binary_train = (y_train != benign_index).astype(np.int64)
    binary_validation = (y_validation != benign_index).astype(np.int64)
    family_weight = class_weights(y_train, len(known_class_names))[y_train]
    binary_weight = class_weights(binary_train, 2)[binary_train]
    common = {
        "n_estimators": args.estimators,
        "max_depth": args.max_depth,
        "learning_rate": args.learning_rate,
        "subsample": args.subsample,
        "colsample_bytree": args.colsample_bytree,
        "tree_method": "hist",
        "device": "cuda",
        "early_stopping_rounds": args.early_stopping_rounds,
        "n_jobs": args.jobs,
        "random_state": args.seed,
    }
    family_model = XGBClassifier(
        objective="multi:softprob",
        eval_metric="mlogloss",
        **common,
    )
    attack_model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        **common,
    )
    initial_gpu = query_gpu()
    if initial_gpu["uuid"] != args.required_gpu_uuid:
        raise RuntimeError("requested A6000 UUID is not visible")
    sampler = GPUSampler(args.gpu_sample_interval_seconds)
    sampler.start()
    started = time.perf_counter()
    try:
        family_model.fit(
            x_train,
            y_train,
            sample_weight=family_weight,
            eval_set=[(x_validation, y_validation)],
            verbose=False,
        )
        attack_model.fit(
            x_train,
            binary_train,
            sample_weight=binary_weight,
            eval_set=[(x_validation, binary_validation)],
            verbose=False,
        )
        validation_family_probability = np.asarray(
            family_model.predict_proba(x_validation), dtype=np.float64
        )
        test_family_probability = np.asarray(
            family_model.predict_proba(x_test), dtype=np.float64
        )
        validation_binary_probability = np.asarray(
            attack_model.predict_proba(x_validation)[:, 1], dtype=np.float64
        )
        test_binary_probability = np.asarray(
            attack_model.predict_proba(x_test)[:, 1], dtype=np.float64
        )
    finally:
        sampler.stop()
    elapsed_seconds = time.perf_counter() - started
    family_configuration = family_model.get_booster().save_config()
    attack_configuration = attack_model.get_booster().save_config()
    configurations_verified = booster_uses_cuda(
        family_configuration
    ) and booster_uses_cuda(attack_configuration)
    validation_attack_variants = attack_probability_variants(
        validation_family_probability,
        validation_binary_probability,
        benign_index,
    )
    test_attack_variants = attack_probability_variants(
        test_family_probability,
        test_binary_probability,
        benign_index,
    )
    validation_prototype, prototype_report = prototype_distance(
        x_train,
        y_train,
        x_validation,
        len(known_class_names),
    )
    test_prototype, _ = prototype_distance(
        x_train,
        y_train,
        x_test,
        len(known_class_names),
    )
    validation_benign_distance, benign_report = benign_prototype_distance(
        x_train,
        y_train,
        x_validation,
        benign_index,
    )
    test_benign_distance, _ = benign_prototype_distance(
        x_train,
        y_train,
        x_test,
        benign_index,
    )
    validation_components = {
        "family_uncertainty": 1.0
        - validation_family_probability.max(axis=1),
        "knownness_uncertainty": 1.0
        - validation_family_probability.max(axis=1),
        "prototype_distance": validation_prototype,
        "benign_distance": validation_benign_distance,
    }
    test_components = {
        "family_uncertainty": 1.0 - test_family_probability.max(axis=1),
        "knownness_uncertainty": 1.0 - test_family_probability.max(axis=1),
        "prototype_distance": test_prototype,
        "benign_distance": test_benign_distance,
    }
    validation_tail = {
        name: tail_percentile(values, values)
        for name, values in validation_components.items()
    }
    test_tail = {
        name: tail_percentile(validation_components[name], values)
        for name, values in test_components.items()
    }
    validation_open_max = np.maximum.reduce(list(validation_tail.values()))
    test_open_max = np.maximum.reduce(list(test_tail.values()))
    validation_open_noisy_or = 1.0 - np.prod(
        [1.0 - values for values in validation_tail.values()], axis=0
    )
    test_open_noisy_or = 1.0 - np.prod(
        [1.0 - values for values in test_tail.values()], axis=0
    )
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    family_model_path = output_dir / "family_model.ubj"
    attack_model_path = output_dir / "attack_model.ubj"
    scores_path = output_dir / "scores.npz"
    family_model.save_model(family_model_path)
    attack_model.save_model(attack_model_path)
    score_arrays: dict[str, Any] = {
        "validation_attack_probability": validation_attack_variants["family"],
        "test_attack_probability": test_attack_variants["family"],
        "validation_open_max": validation_open_max,
        "validation_open_noisy_or": validation_open_noisy_or,
        "validation_family_uncertainty_tail": validation_tail[
            "family_uncertainty"
        ],
        "validation_knownness_uncertainty_tail": validation_tail[
            "knownness_uncertainty"
        ],
        "validation_prototype_distance_tail": validation_tail[
            "prototype_distance"
        ],
        "validation_benign_distance_tail": validation_tail["benign_distance"],
        "validation_type_prediction": validation_family_probability.argmax(
            axis=1
        ),
        "validation_labels": y_validation,
        "test_open_max": test_open_max,
        "test_open_noisy_or": test_open_noisy_or,
        "test_family_uncertainty_tail": test_tail["family_uncertainty"],
        "test_knownness_uncertainty_tail": test_tail["knownness_uncertainty"],
        "test_prototype_distance_tail": test_tail["prototype_distance"],
        "test_benign_distance_tail": test_tail["benign_distance"],
        "test_type_prediction": test_family_probability.argmax(axis=1),
        "test_labels": test_labels,
        "test_unknown": test_unknown,
        "known_class_names": np.asarray(known_class_names),
    }
    for variant, values in validation_attack_variants.items():
        score_arrays[f"validation_{variant}_attack_probability"] = values
    for variant, values in test_attack_variants.items():
        score_arrays[f"test_{variant}_attack_probability"] = values
    np.savez_compressed(scores_path, **score_arrays)
    peak_utilization = max(
        (sample["utilization_percent"] for sample in sampler.samples),
        default=0.0,
    )
    peak_memory = max(
        (sample["memory_used_mib"] for sample in sampler.samples), default=0.0
    )
    compute_process_observed = any(
        sample["compute_processes"] for sample in sampler.samples
    )
    gpu_passes = (
        configurations_verified
        and initial_gpu["uuid"] == args.required_gpu_uuid
        and compute_process_observed
        and peak_utilization > 0.0
        and peak_memory > 1.0
        and not sampler.errors
    )
    gpu_evidence: dict[str, Any] = {
        "schema_version": "strict_v4_fine_balanced_xgboost_cuda_evidence_v1",
        "state": "complete",
        "gpu_identity": {
            key: initial_gpu[key] for key in ("index", "name", "uuid")
        },
        "xgboost_version": __import__("xgboost").__version__,
        "family_booster_cuda_config_verified": booster_uses_cuda(
            family_configuration
        ),
        "attack_booster_cuda_config_verified": booster_uses_cuda(
            attack_configuration
        ),
        "xgboost_cuda_model_configs_verified": configurations_verified,
        "compute_process_observed_by_nvidia_smi": compute_process_observed,
        "sample_count": len(sampler.samples),
        "samples": sampler.samples,
        "sample_errors": sampler.errors,
        "peak_gpu_utilization_percent": peak_utilization,
        "peak_gpu_memory_mib": peak_memory,
        "passes": gpu_passes,
    }
    gpu_evidence["manifest_sha256"] = canonical_hash(gpu_evidence)
    atomic_json(output_dir / "gpu_execution.json", gpu_evidence)
    feature_names = [
        str(column)
        for modality_columns in config["modalities"].values()
        for column in modality_columns
    ]
    report: dict[str, Any] = {
        "schema_version": "strict_v4_fine_balanced_xgboost_cuda_task_v1",
        "state": "complete",
        "task": {
            "taxonomy": args.taxonomy,
            "classification_level": args.classification_level,
            "unknown_family": args.unknown_family,
            "unknown_fine_classes": unknown_fine_classes,
            "seed": args.seed,
        },
        "known_class_names": known_class_names,
        "fine_class_names": fine_class_names,
        "benign_index": benign_index,
        "split_counts": {
            "train": split_counts(
                y_train,
                unknown_flags(bundle.train),
                known_class_names,
                args.unknown_family,
            ),
            "validation": split_counts(
                y_validation,
                validation_unknown,
                known_class_names,
                args.unknown_family,
            ),
            "test": split_counts(
                test_labels,
                test_unknown,
                known_class_names,
                args.unknown_family,
            ),
        },
        "model": {
            "name": "FB-FSX-CAEOS fine-balanced CUDA XGBoost branch",
            "architecture": "fine_grained_dual_xgboost_cuda_v1",
            "flow_statistic_dimension": int(x_train.shape[1]),
            "flow_statistic_names": feature_names,
            "preprocessing": {
                "fit_scope": "training_split_only",
                "implementation": "caeos.data.TabularViewPreprocessor",
                "modality_names": bundle.modality_names,
                "input_dimensions": bundle.input_dims,
            },
            "family_best_iteration": int(family_model.best_iteration),
            "attack_best_iteration": int(attack_model.best_iteration),
            "prototype": prototype_report,
            "benign_prototype": benign_report,
            "primary_saved_attack_probability": "family_non_benign",
            "development_attack_probability_variants": sorted(
                validation_attack_variants
            ),
        },
        "data_partition": {
            "sample_counts": bundle.sample_counts,
            "split_metadata": bundle.split_metadata,
            "taxonomy": args.taxonomy,
            "classification_level": args.classification_level,
            "fine_to_family_mapping": taxonomy_mapping,
        },
        "training": {
            "elapsed_seconds": elapsed_seconds,
            "estimators": args.estimators,
            "max_depth": args.max_depth,
            "learning_rate": args.learning_rate,
            "subsample": args.subsample,
            "colsample_bytree": args.colsample_bytree,
            "early_stopping_rounds": args.early_stopping_rounds,
        },
        "gpu_execution": {
            "file": "gpu_execution.json",
            "file_sha256": file_hash(output_dir / "gpu_execution.json"),
            "manifest_sha256": gpu_evidence["manifest_sha256"],
            "passes": gpu_passes,
        },
        "artifacts": {
            "family_model": {
                "file": family_model_path.name,
                "sha256": file_hash(family_model_path),
            },
            "attack_model": {
                "file": attack_model_path.name,
                "sha256": file_hash(attack_model_path),
            },
            "scores": {
                "file": scores_path.name,
                "sha256": file_hash(scores_path),
            },
        },
        "source": {
            "cache_csv": str(cache_csv),
            "cache_csv_sha256": file_hash(cache_csv),
            "config": str(config_path),
            "config_sha256": file_hash(config_path),
        },
        "claim_boundary": {
            "development_seed_only": True,
            "unknown_family_fine_classes_excluded_from_train_and_validation": True,
            "unknown_or_test_labels_used_for_fitting_or_early_stopping": False,
            "true_unknown_used_for_final_configuration_selection": False,
            "formal_model_training_uses_xgboost_cuda": True,
            "numpy_input_requires_host_to_device_transfer": True,
            "preprocessing_fit_on_training_split_only": True,
            "capture_grouped_split": True,
        },
    }
    report["manifest_sha256"] = canonical_hash(report)
    atomic_json(output_dir / "metrics.json", report)
    if not gpu_passes:
        raise RuntimeError("fine-balanced XGBoost CUDA evidence did not pass")
    if not math.isfinite(elapsed_seconds):
        raise RuntimeError("XGBoost training duration was not finite")
    return report


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--taxonomy",
        choices=tuple(TAXONOMIES),
        default="cicids2017",
    )
    parser.add_argument(
        "--classification-level",
        choices=("fine", "family"),
        default="fine",
    )
    parser.add_argument("--unknown-family", required=True)
    parser.add_argument("--seed", type=int, default=29)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--required-gpu-uuid", required=True)
    parser.add_argument("--xgboost-root", type=Path, required=True)
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--estimators", type=int, default=1200)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--subsample", type=float, default=0.9)
    parser.add_argument("--colsample-bytree", type=float, default=0.9)
    parser.add_argument("--early-stopping-rounds", type=int, default=40)
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--gpu-sample-interval-seconds", type=float, default=0.2)
    return parser.parse_args()


def main() -> None:
    report = train_task(parse_arguments())
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
