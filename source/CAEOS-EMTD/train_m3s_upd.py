from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

from caeos.data import TabularViewPreprocessor, row_fingerprint
from caeos.m3s_upd import (
    M3SClassifier,
    align_unlabeled_clusters,
    alignment_threshold,
    class_centroids,
    consistency_selection,
    iter_minibatches,
    standardize_embeddings,
    unknown_risk,
)
from caeos.metrics import fpr_at_95_tpr, open_set_classification_rate


PAPER_URL = "https://arxiv.org/abs/2505.21462"
PAPER_DOI = "10.48550/arXiv.2505.21462"
CLASS_ALIASES = {
    "AUDIO": "Audio",
    "BROWSING": "Browsing",
    "CHAT": "Chat",
    "FILE-TRANSFER": "FILE-Transfer",
    "MAIL": "Mail",
    "P2P": "P2P",
    "VIDEO": "Video",
    "VOIP": "VOIP",
}
SETTINGS = {
    "setting1": ("VOIP", "P2P", "FILE-TRANSFER"),
    "setting2": ("VOIP", "P2P", "FILE-TRANSFER", "VIDEO", "CHAT"),
}
IDENTIFIER_COLUMNS = {
    "Source IP",
    " Source Port",
    " Destination IP",
    " Destination Port",
    " Protocol",
    "label",
}


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonicalize_frame(path: str) -> Tuple[pd.DataFrame, List[str]]:
    frame = pd.read_csv(path, low_memory=False)
    frame.columns = [str(column).strip() for column in frame.columns]
    frame["label"] = frame["label"].astype(str).str.strip().str.upper()
    feature_columns = [
        column
        for column in frame.columns
        if column not in {value.strip() for value in IDENTIFIER_COLUMNS}
        and column != "label"
    ]
    numeric = frame[feature_columns].apply(pd.to_numeric, errors="coerce")
    variable = numeric.nunique(dropna=False) > 1
    feature_columns = list(variable[variable].index)
    return frame, feature_columns


def stratified_split_indices(
    labels: np.ndarray, seed: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    all_indices = np.arange(len(labels))
    train, remaining = train_test_split(
        all_indices, test_size=0.40, random_state=seed, stratify=labels
    )
    validation, test = train_test_split(
        remaining, test_size=0.50, random_state=seed, stratify=labels[remaining]
    )
    return np.sort(train), np.sort(validation), np.sort(test)


def initial_labeled_indices(
    train_indices: np.ndarray,
    labels: np.ndarray,
    known_names: Sequence[str],
    fraction: float,
    seed: int,
) -> np.ndarray:
    rng = np.random.RandomState(seed)
    selected = []
    for name in known_names:
        candidates = train_indices[labels[train_indices] == name].copy()
        rng.shuffle(candidates)
        count = max(1, int(round(len(candidates) * fraction)))
        selected.append(candidates[:count])
    return np.sort(np.concatenate(selected))


def fingerprint_overlap(
    frame: pd.DataFrame,
    feature_columns: Sequence[str],
    splits: Sequence[np.ndarray],
) -> Dict[str, int]:
    fingerprints = row_fingerprint(frame, feature_columns).to_numpy()
    sets = [set(fingerprints[indices].tolist()) for indices in splits]
    return {
        "train_validation": len(sets[0] & sets[1]),
        "train_test": len(sets[0] & sets[2]),
        "validation_test": len(sets[1] & sets[2]),
    }


@torch.no_grad()
def infer(
    model: M3SClassifier,
    values: np.ndarray,
    device: torch.device,
    batch_size: int = 2048,
) -> Tuple[np.ndarray, np.ndarray]:
    model.eval()
    probabilities = []
    embeddings = []
    for start in range(0, len(values), batch_size):
        batch = torch.as_tensor(
            values[start : start + batch_size], dtype=torch.float32, device=device
        )
        output = model(batch)
        probabilities.append(torch.softmax(output["logits"], dim=1).cpu().numpy())
        embeddings.append(output["embedding"].cpu().numpy())
    return np.concatenate(probabilities), np.concatenate(embeddings)


def train_classifier(
    model: M3SClassifier,
    values: np.ndarray,
    labels: np.ndarray,
    train_indices: np.ndarray,
    validation_indices: np.ndarray,
    device: torch.device,
    seed: int,
    epochs: int,
    patience: int,
    batch_size: int,
    learning_rate: float,
) -> Dict[str, float]:
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    rng = np.random.RandomState(seed)
    best_loss = float("inf")
    best_state = None
    stale = 0
    for epoch in range(epochs):
        model.train()
        for indices in iter_minibatches(train_indices, batch_size, rng):
            batch_values = torch.as_tensor(values[indices], dtype=torch.float32, device=device)
            batch_labels = torch.as_tensor(labels[indices], dtype=torch.long, device=device)
            output = model(batch_values)
            loss = F.cross_entropy(output["logits"], batch_labels)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
        validation_probabilities, _ = infer(model, values[validation_indices], device)
        validation_loss = float(
            -np.log(
                validation_probabilities[
                    np.arange(len(validation_indices)), labels[validation_indices]
                ].clip(1e-9)
            ).mean()
        )
        if validation_loss < best_loss - 1e-5:
            best_loss = validation_loss
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
            stale = 0
        else:
            stale += 1
            if stale >= patience:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    return {"best_validation_loss": best_loss, "epochs_ran": epoch + 1}


def macro_false_positive_rate(target: np.ndarray, prediction: np.ndarray, classes: int) -> float:
    matrix = confusion_matrix(target, prediction, labels=np.arange(classes))
    rates = []
    total = matrix.sum()
    for index in range(classes):
        fp = matrix[:, index].sum() - matrix[index, index]
        tn = total - matrix[index, :].sum() - matrix[:, index].sum() + matrix[index, index]
        rates.append(float(fp / max(1, fp + tn)))
    return float(np.mean(rates))


def evaluate(
    true_names: np.ndarray,
    known_names: Sequence[str],
    prediction: np.ndarray,
    risk: np.ndarray,
) -> Dict[str, object]:
    known_map = {name: index for index, name in enumerate(known_names)}
    unknown_index = len(known_names)
    target = np.asarray([known_map.get(name, unknown_index) for name in true_names])
    is_unknown = target == unknown_index
    known = ~is_unknown
    classes = unknown_index + 1
    report = {
        "accuracy": float(accuracy_score(target, prediction)),
        "macro_precision": float(precision_score(target, prediction, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(target, prediction, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(target, prediction, average="macro", zero_division=0)),
        "macro_fpr": macro_false_positive_rate(target, prediction, classes),
        "known_accuracy": float(accuracy_score(target[known], prediction[known])),
        "known_macro_f1": float(f1_score(target[known], prediction[known], average="macro", zero_division=0)),
        "unknown_precision": float(precision_score(is_unknown, prediction == unknown_index, zero_division=0)),
        "unknown_recall": float(recall_score(is_unknown, prediction == unknown_index, zero_division=0)),
        "unknown_f1": float(f1_score(is_unknown, prediction == unknown_index, zero_division=0)),
        "unknown_fpr": float(((prediction == unknown_index) & known).sum() / max(1, known.sum())),
        "unknown_auroc": float(roc_auc_score(is_unknown, risk)),
        "unknown_aupr": float(average_precision_score(is_unknown, risk)),
        "unknown_fpr95": fpr_at_95_tpr(is_unknown.astype(np.int64), risk),
        "oscr": open_set_classification_rate(target, np.minimum(prediction, unknown_index - 1), is_unknown, risk),
        "confusion_matrix": confusion_matrix(target, prediction, labels=np.arange(classes)).tolist(),
        "class_order": [CLASS_ALIASES[name] for name in known_names] + ["Unknown"],
    }
    return report


def transductive_predict(
    probabilities: np.ndarray,
    embeddings: np.ndarray,
    labeled_embeddings: np.ndarray,
    labeled_labels: np.ndarray,
    num_classes: int,
    max_rounds: int,
    min_samples: int,
    eps_quantile: float,
    distance_quantile: float,
    top_fraction: float,
    bottom_fraction: float,
) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, object]]]:
    labeled_standard, values_standard, state = standardize_embeddings(labeled_embeddings, embeddings)
    centroids = class_centroids(labeled_standard, labeled_labels, num_classes)
    threshold = alignment_threshold(labeled_standard, labeled_labels, centroids, distance_quantile)
    prediction = np.full(len(embeddings), -1, dtype=np.int64)
    risk = np.zeros(len(embeddings), dtype=np.float64)
    remaining = np.arange(len(embeddings), dtype=np.int64)
    history = []
    for iteration in range(max_rounds):
        if not len(remaining):
            break
        alignment = align_unlabeled_clusters(
            values_standard[remaining], centroids, threshold, min_samples, eps_quantile
        )
        selection = consistency_selection(
            probabilities[remaining], alignment, top_fraction, bottom_fraction
        )
        selected_known = remaining[selection.known_indices]
        selected_unknown = remaining[selection.unknown_indices]
        prediction[selected_known] = probabilities[selected_known].argmax(axis=1)
        prediction[selected_unknown] = num_classes
        local_risk = unknown_risk(probabilities[remaining], alignment.sample_distance, threshold)
        risk[remaining] = local_risk
        history.append(
            {
                "iteration": iteration + 1,
                "pool": int(len(remaining)),
                "known": int(len(selected_known)),
                "unknown": int(len(selected_unknown)),
                "deferred": int(len(selection.deferred_indices)),
                "clusters": int(len(np.unique(alignment.cluster_labels))),
                "dbscan_eps": float(alignment.eps),
                "distance_threshold": float(threshold),
                "confidence_low": float(selection.confidence_low),
                "confidence_high": float(selection.confidence_high),
            }
        )
        next_remaining = remaining[selection.deferred_indices]
        if len(next_remaining) == len(remaining):
            break
        remaining = next_remaining
    if len(remaining):
        alignment = align_unlabeled_clusters(
            values_standard[remaining], centroids, threshold, min_samples, eps_quantile
        )
        fallback_unknown = alignment.potential_unknown
        prediction[remaining] = probabilities[remaining].argmax(axis=1)
        prediction[remaining[fallback_unknown]] = num_classes
        risk[remaining] = unknown_risk(
            probabilities[remaining], alignment.sample_distance, threshold
        )
        history.append(
            {
                "iteration": "fallback",
                "pool": int(len(remaining)),
                "known": int((~fallback_unknown).sum()),
                "unknown": int(fallback_unknown.sum()),
                "deferred": 0,
            }
        )
    return prediction, risk, history


def run_setting(args: argparse.Namespace, setting: str, seed: int) -> Dict[str, object]:
    set_seed(seed)
    frame, feature_columns = canonicalize_frame(args.csv)
    labels = frame["label"].to_numpy()
    known_names = SETTINGS[setting]
    train_indices, validation_indices, test_indices = stratified_split_indices(labels, seed)
    initial = initial_labeled_indices(
        train_indices, labels, known_names, args.labeled_fraction, seed
    )
    known_map = {name: index for index, name in enumerate(known_names)}
    model_labels = np.full(len(frame), -1, dtype=np.int64)
    for name, index in known_map.items():
        model_labels[labels == name] = index
    validation_known = validation_indices[model_labels[validation_indices] >= 0]

    raw_values = frame[feature_columns].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=np.float32)
    preprocessor = TabularViewPreprocessor()
    preprocessor.fit(raw_values[initial])
    values, quality = preprocessor.transform(raw_values)
    device = torch.device(args.device if args.device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu"))
    model = M3SClassifier(
        values.shape[1], len(known_names), embedding_dim=args.embedding_dim
    ).to(device)
    labeled = initial.copy()
    unlabeled = np.setdiff1d(train_indices, labeled, assume_unique=True)
    discovered_unknown = np.empty(0, dtype=np.int64)
    iteration_history = []
    best_update_validation_loss = float("inf")
    final_training: Dict[str, float] = {}

    for iteration in range(args.update_rounds):
        training = train_classifier(
            model,
            values,
            model_labels,
            labeled,
            validation_known,
            device,
            seed + iteration,
            args.epochs,
            args.patience,
            args.batch_size,
            args.learning_rate,
        )
        final_training = training
        if (
            iteration > 0
            and training["best_validation_loss"]
            > best_update_validation_loss + args.update_validation_tolerance
        ):
            iteration_history.append(
                {
                    "iteration": iteration + 1,
                    "labeled_before": int(len(labeled)),
                    "pool_before": int(len(unlabeled)),
                    "added_known": 0,
                    "discovered_unknown": 0,
                    "deferred": int(len(unlabeled)),
                    "stop_reason": "known_validation_loss_no_longer_improved",
                    "best_previous_validation_loss": float(best_update_validation_loss),
                    **training,
                }
            )
            break
        best_update_validation_loss = min(
            best_update_validation_loss, training["best_validation_loss"]
        )
        _, labeled_embeddings = infer(model, values[labeled], device)
        if not len(unlabeled):
            break
        probabilities, embeddings = infer(model, values[unlabeled], device)
        labeled_standard, unlabeled_standard, _ = standardize_embeddings(
            labeled_embeddings, embeddings
        )
        centroids = class_centroids(
            labeled_standard, model_labels[labeled], len(known_names)
        )
        threshold = alignment_threshold(
            labeled_standard,
            model_labels[labeled],
            centroids,
            args.distance_quantile,
        )
        alignment = align_unlabeled_clusters(
            unlabeled_standard,
            centroids,
            threshold,
            args.dbscan_min_samples,
            args.dbscan_eps_quantile,
        )
        selection = consistency_selection(
            probabilities, alignment, args.top_fraction, args.bottom_fraction
        )
        add = unlabeled[selection.known_indices]
        newly_unknown = unlabeled[selection.unknown_indices]
        model_labels[add] = alignment.auxiliary_labels[selection.known_indices]
        labeled = np.sort(np.concatenate([labeled, add]))
        discovered_unknown = np.sort(np.concatenate([discovered_unknown, newly_unknown]))
        deferred = unlabeled[selection.deferred_indices]
        iteration_history.append(
            {
                "iteration": iteration + 1,
                "labeled_before": int(len(labeled) - len(add)),
                "pool_before": int(len(unlabeled)),
                "added_known": int(len(add)),
                "discovered_unknown": int(len(newly_unknown)),
                "deferred": int(len(deferred)),
                "added_known_precision_audit": float(
                    np.mean(model_labels[add] == np.asarray([known_map.get(name, -1) for name in labels[add]]))
                ) if len(add) else None,
                "unknown_precision_audit": float(
                    np.mean(~np.isin(labels[newly_unknown], known_names))
                ) if len(newly_unknown) else None,
                "clusters": int(len(np.unique(alignment.cluster_labels))),
                "dbscan_eps": float(alignment.eps),
                "distance_threshold": float(threshold),
                "confidence_low": float(selection.confidence_low),
                "confidence_high": float(selection.confidence_high),
                **training,
            }
        )
        if not len(add) and not len(newly_unknown):
            break
        unlabeled = deferred

    _, labeled_embeddings = infer(model, values[labeled], device)
    test_probabilities, test_embeddings = infer(model, values[test_indices], device)
    prediction, risk, inference_history = transductive_predict(
        test_probabilities,
        test_embeddings,
        labeled_embeddings,
        model_labels[labeled],
        len(known_names),
        args.inference_rounds,
        args.dbscan_min_samples,
        args.dbscan_eps_quantile,
        args.distance_quantile,
        args.top_fraction,
        args.bottom_fraction,
    )
    metrics = evaluate(labels[test_indices], known_names, prediction, risk)
    validation_probabilities, validation_embeddings = infer(
        model, values[validation_indices], device
    )
    _, validation_risk, validation_inference_history = transductive_predict(
        validation_probabilities,
        validation_embeddings,
        labeled_embeddings,
        model_labels[labeled],
        len(known_names),
        args.inference_rounds,
        args.dbscan_min_samples,
        args.dbscan_eps_quantile,
        args.distance_quantile,
        args.top_fraction,
        args.bottom_fraction,
    )
    validation_is_known = np.isin(labels[validation_indices], known_names)
    calibrated = {}
    calibrated_predictions = {}
    for target_fpr in (0.05, 0.02):
        threshold = float(
            np.quantile(validation_risk[validation_is_known], 1.0 - target_fpr)
        )
        calibrated_prediction = test_probabilities.argmax(axis=1)
        calibrated_prediction[risk >= threshold] = len(known_names)
        name = "known_validation_fpr_%02d" % int(round(target_fpr * 100))
        calibrated[name] = {
            "target_known_fpr": target_fpr,
            "risk_threshold": threshold,
            "metrics": evaluate(
                labels[test_indices], known_names, calibrated_prediction, risk
            ),
        }
        calibrated_predictions[name] = calibrated_prediction
    counts = {name: int((labels == name).sum()) for name in sorted(np.unique(labels))}
    result = {
        "method": "M3S-UPD paper-formula adapter",
        "setting": setting,
        "seed": seed,
        "metrics": metrics,
        "paper_reference": {"url": PAPER_URL, "doi": PAPER_DOI, "version": "v1"},
        "protocol": {
            "dataset": "ISCXTor2016 Scenario-B 5-second flows",
            "dataset_rows": int(len(frame)),
            "dataset_class_counts": counts,
            "paper_reported_total_typo": 12808,
            "verified_class_count_sum": int(sum(counts.values())),
            "split": [0.6, 0.2, 0.2],
            "initial_labeled_fraction_per_known_class": args.labeled_fraction,
            "known_classes": [CLASS_ALIASES[name] for name in known_names],
            "unknown_classes": [
                CLASS_ALIASES[name] for name in sorted(set(CLASS_ALIASES) - set(known_names))
            ],
            "feature_columns": feature_columns,
            "identifier_columns_excluded": sorted(value.strip() for value in IDENTIFIER_COLUMNS),
            "train_only_preprocessing_fit_rows": int(len(initial)),
            "initial_labeled_rows": int(len(initial)),
            "final_labeled_rows": int(len(labeled)),
            "discovered_unknown_train_rows": int(len(discovered_unknown)),
            "deferred_train_rows": int(len(unlabeled)),
            "split_rows": {
                "train": int(len(train_indices)),
                "validation": int(len(validation_indices)),
                "test": int(len(test_indices)),
            },
            "fingerprint_overlap_audit": fingerprint_overlap(
                frame, feature_columns, (train_indices, validation_indices, test_indices)
            ),
            "quality_mean": float(quality.mean()),
            "test_inference": "transductive cluster alignment without test labels or parameter updates",
        },
        "adapter_parameters": {
            "network": "MLP-128-64-32",
            "network_disclosed_by_paper": False,
            "dbscan_min_samples": args.dbscan_min_samples,
            "dbscan_eps": "train-only adaptive k-distance quantile",
            "dbscan_eps_quantile": args.dbscan_eps_quantile,
            "distance_threshold": "labeled own-centroid distance quantile",
            "distance_quantile": args.distance_quantile,
            "top_fraction": args.top_fraction,
            "bottom_fraction": args.bottom_fraction,
            "update_validation_tolerance": args.update_validation_tolerance,
            "parameters_disclosed_by_paper": False,
            "selection_parameter_labels_used": False,
            "outer_test_labels_used": False,
        },
        "update_history": iteration_history,
        "inference_history": inference_history,
        "validation_inference_history": validation_inference_history,
        "known_validation_operating_points": calibrated,
        "final_training": final_training,
    }
    result["_score_arrays"] = {
        "test_indices": test_indices,
        "true_label": labels[test_indices],
        "known_probability": test_probabilities,
        "strict_prediction": prediction,
        "unknown_risk": risk,
        **{
            "%s_prediction" % name: values
            for name, values in calibrated_predictions.items()
        },
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--settings", nargs="+", choices=sorted(SETTINGS), default=sorted(SETTINGS))
    parser.add_argument("--seeds", nargs="+", type=int, default=[7, 11, 23])
    parser.add_argument("--device", default="auto")
    parser.add_argument("--labeled-fraction", type=float, default=0.30)
    parser.add_argument("--embedding-dim", type=int, default=32)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--patience", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--update-rounds", type=int, default=10)
    parser.add_argument("--update-validation-tolerance", type=float, default=5e-4)
    parser.add_argument("--inference-rounds", type=int, default=20)
    parser.add_argument("--dbscan-min-samples", type=int, default=5)
    parser.add_argument("--dbscan-eps-quantile", type=float, default=0.90)
    parser.add_argument("--distance-quantile", type=float, default=0.95)
    parser.add_argument("--top-fraction", type=float, default=0.10)
    parser.add_argument("--bottom-fraction", type=float, default=0.10)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for setting in args.settings:
        for seed in args.seeds:
            result = run_setting(args, setting, seed)
            score_arrays = result.pop("_score_arrays")
            path = output_dir / ("%s_seed%d.json" % (setting, seed))
            path.write_text(json.dumps(result, ensure_ascii=True, indent=2), encoding="utf-8")
            np.savez_compressed(
                output_dir / ("%s_seed%d_scores.npz" % (setting, seed)),
                **score_arrays,
            )
            results.append(result)
            calibrated = result["known_validation_operating_points"][
                "known_validation_fpr_05"
            ]["metrics"]
            print(
                "%s seed=%d strict_accuracy=%.6f strict_unknown_f1=%.6f "
                "known95_accuracy=%.6f known95_unknown_f1=%.6f oscr=%.6f"
                % (
                    setting,
                    seed,
                    result["metrics"]["accuracy"],
                    result["metrics"]["unknown_f1"],
                    calibrated["accuracy"],
                    calibrated["unknown_f1"],
                    calibrated["oscr"],
                ),
                flush=True,
            )
    summary = {}
    for setting in args.settings:
        selected = [result for result in results if result["setting"] == setting]
        summary[setting] = {"strict_consistency": {
            metric: {
                "mean": float(np.mean([result["metrics"][metric] for result in selected])),
                "std": float(np.std([result["metrics"][metric] for result in selected])),
            }
            for metric in (
                "accuracy",
                "macro_precision",
                "macro_recall",
                "macro_fpr",
                "unknown_auroc",
                "unknown_f1",
                "oscr",
            )
        }}
        for operating_point in ("known_validation_fpr_05", "known_validation_fpr_02"):
            summary[setting][operating_point] = {
                metric: {
                    "mean": float(
                        np.mean(
                            [
                                result["known_validation_operating_points"][operating_point]["metrics"][metric]
                                for result in selected
                            ]
                        )
                    ),
                    "std": float(
                        np.std(
                            [
                                result["known_validation_operating_points"][operating_point]["metrics"][metric]
                                for result in selected
                            ]
                        )
                    ),
                }
                for metric in (
                    "accuracy",
                    "macro_precision",
                    "macro_recall",
                    "macro_fpr",
                    "unknown_auroc",
                    "unknown_f1",
                    "oscr",
                )
            }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "method": "M3S-UPD paper-formula adapter",
                "paper_table_iv": {
                    "setting1": {"accuracy": 0.9469, "precision": 0.9480, "recall": 0.9365, "fpr": 0.0204},
                    "setting2": {"accuracy": 0.8456, "precision": 0.7812, "recall": 0.8619, "fpr": 0.0289},
                },
                "aggregate": summary,
                "runs": len(results),
            },
            ensure_ascii=True,
            indent=2,
        ),
        encoding="utf-8",
    )
    artifact_paths = sorted(
        list(output_dir.glob("setting*_seed*.json"))
        + list(output_dir.glob("setting*_seed*_scores.npz"))
        + [summary_path]
    )
    manifest = {
        "method": "M3S-UPD paper-formula adapter",
        "paper": {"url": PAPER_URL, "doi": PAPER_DOI, "version": "v1"},
        "command_arguments": vars(args),
        "completed_runs": len(results),
        "failed_runs": 0,
        "artifacts": [
            {
                "path": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in artifact_paths
        ],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=True, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
