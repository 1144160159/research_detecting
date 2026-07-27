from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from torch.utils.data import DataLoader

from caeos.cadref_posthoc import cadref_score_batch, evidence, fit_cadref
from caeos.data import prepare_tabular_open_set
from caeos.multiclass import ConcatMLPClassifier
from evaluate_mlp_posthoc_ood import load_checkpoint, sha256_file, validate_source
from train_neural_open_set import choose_device, collect, report_for


METHODS = ("caref", "cadref_energy_fixed")


def score_in_batches(
    embeddings: np.ndarray,
    logits: np.ndarray,
    state,
    *,
    batch_size: int,
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    scores = {method: [] for method in METHODS}
    diagnostics = []
    for start in range(0, len(embeddings), batch_size):
        items, detail = cadref_score_batch(
            embeddings[start : start + batch_size],
            logits[start : start + batch_size],
            state,
        )
        for method in METHODS:
            scores[method].append(items[method])
        diagnostics.append(detail)
    combined = {method: np.concatenate(items) for method, items in scores.items()}
    return combined, {
        "batch_count": len(diagnostics),
        "sample_count": int(len(embeddings)),
        "all_scores_finite": all(
            bool(np.isfinite(item).all()) for item in combined.values()
        ),
        "caref_score_standard_deviation": float(np.std(combined["caref"])),
        "cadref_score_standard_deviation": float(
            np.std(combined["cadref_energy_fixed"])
        ),
        "minimum_absolute_feature_l1": float(
            min(item["minimum_absolute_feature_l1"] for item in diagnostics)
        ),
        "minimum_energy": float(min(item["minimum_energy"] for item in diagnostics)),
        "maximum_energy": float(max(item["maximum_energy"] for item in diagnostics)),
        "minimum_absolute_energy": float(
            min(item["minimum_absolute_energy"] for item in diagnostics)
        ),
        "queried_predicted_class_count": int(
            max(item["queried_predicted_class_count"] for item in diagnostics)
        ),
        "zero_weight_coordinate_count": int(
            max(item["zero_weight_coordinate_count"] for item in diagnostics)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate CVPR 2025 CARef/CADRef from a frozen strict MLP run"
    )
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--num-workers", type=int, default=0)
    args = parser.parse_args()

    source_run = args.source_run.resolve()
    source_paths = {
        name: source_run / name for name in ("metrics.json", "scores.npz", "model.pt")
    }
    missing = [str(path) for path in source_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing source artifacts: " + ", ".join(missing))
    metrics = json.loads(source_paths["metrics.json"].read_text(encoding="utf-8"))
    checkpoint = load_checkpoint(source_paths["model.pt"])
    with np.load(source_paths["scores.npz"], allow_pickle=False) as source_scores:
        arguments = validate_source(metrics, checkpoint, source_scores)
        if arguments.get("dataset") != "tabular":
            raise ValueError("strict CADRef matrix only accepts tabular runs")
        config_path = Path(str(arguments["config"]))
        if not config_path.is_absolute():
            config_path = Path.cwd() / config_path
        config = json.loads(config_path.read_text(encoding="utf-8"))
        unknown_classes = [
            item.strip()
            for item in str(arguments["unknown_classes"]).split(",")
            if item.strip()
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
        if bundle.class_names != list(checkpoint["class_names"]):
            raise ValueError("reconstructed data and checkpoint class names differ")
        if list(bundle.input_dims) != list(checkpoint["input_dims"]):
            raise ValueError("reconstructed data and checkpoint input dimensions differ")
        reconstructed_split = json.loads(
            json.dumps(bundle.split_metadata, ensure_ascii=False, sort_keys=True)
        )
        if reconstructed_split != metrics.get("split_metadata"):
            raise ValueError("reconstructed split metadata differs from frozen source")

        device = choose_device(args.device)
        options = {
            "batch_size": args.batch_size,
            "num_workers": args.num_workers,
            "pin_memory": device.type == "cuda",
        }
        train_loader = DataLoader(bundle.train, shuffle=False, **options)
        validation_loader = DataLoader(bundle.validation, shuffle=False, **options)
        test_loader = DataLoader(bundle.test, shuffle=False, **options)
        model = ConcatMLPClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            int(arguments["hidden_dim"]),
            int(arguments["embedding_dim"]),
            float(arguments["dropout"]),
        ).to(device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        model.eval()
        train = collect(model, train_loader, device)
        validation = collect(model, validation_loader, device)
        test = collect(model, test_loader, device)
        np.testing.assert_array_equal(
            validation["labels"], source_scores["validation_labels"]
        )
        np.testing.assert_array_equal(test["labels"], source_scores["test_labels"])
        np.testing.assert_array_equal(
            test["unknown"].astype(bool), source_scores["test_unknown"]
        )
        prediction = test["logits"].argmax(axis=1)
        if "test_prediction" in source_scores.files:
            np.testing.assert_array_equal(prediction, source_scores["test_prediction"])
        classifier_weight = model.classifier.weight.detach().cpu().numpy()
        classifier_bias = model.classifier.bias.detach().cpu().numpy()

    state = fit_cadref(
        classifier_weight,
        classifier_bias,
        train["embedding"],
        train["logits"],
    )
    validation_scores, validation_diagnostics = score_in_batches(
        validation["embedding"],
        validation["logits"],
        state,
        batch_size=args.batch_size,
    )
    test_scores, test_diagnostics = score_in_batches(
        test["embedding"],
        test["logits"],
        state,
        batch_size=args.batch_size,
    )
    acceptance = float(arguments.get("known_acceptance", 0.95))
    thresholds = {}
    reports = {}
    for method in METHODS:
        validation_risk = -validation_scores[method]
        test_risk = -test_scores[method]
        threshold, report = report_for(
            test["labels"],
            test["unknown"].astype(bool),
            prediction,
            validation_risk,
            test_risk,
            acceptance,
        )
        thresholds[method] = threshold
        reports[method] = report

    source_sha256 = {name: sha256_file(path) for name, path in source_paths.items()}
    postprocessor = evidence()
    supported = np.flatnonzero(state.predicted_class_support).tolist()
    selection = {
        "protocol": "strict_frozen_checkpoint_CARef_CADRef_official_Energy",
        "source_run": str(source_run),
        "source_artifact_sha256": source_sha256,
        "postprocessor": postprocessor,
        "fit_diagnostics": {
            "known_training_sample_count": state.train_sample_count,
            "classifier_class_count": int(len(state.predicted_class_counts)),
            "supported_predicted_class_count": int(len(supported)),
            "supported_predicted_classes": supported,
            "predicted_class_counts": state.predicted_class_counts.tolist(),
            "global_mean_energy": state.global_mean_energy,
        },
        "validation_diagnostics": validation_diagnostics,
        "test_diagnostics": test_diagnostics,
        "prediction_uses_unmodified_frozen_model": True,
        "deployment_thresholds": {
            method: {
                "split": "known_only_validation",
                "known_acceptance_quantile": acceptance,
                "value": thresholds[method],
            }
            for method in METHODS
        },
        "unknown_or_test_labels_used_for_fitting_or_selection": False,
        "test_labels_used_for_final_metrics_only": True,
    }
    result = {
        "schema_version": "strict_v4_mlp_cadref_family_v1",
        "model": "mlp_cadref_family",
        "methods": list(METHODS),
        "unknown_classes": unknown_classes,
        "seed": int(arguments["seed"]),
        "known_class_names": bundle.class_names,
        "sample_counts": bundle.sample_counts,
        "split_metadata": bundle.split_metadata,
        "split_sizes": {
            "train": len(bundle.train),
            "validation": len(bundle.validation),
            "test": len(bundle.test),
            "test_unknown": int(test["unknown"].sum()),
        },
        "validation_thresholds": thresholds,
        "reports": reports,
        "selection_evidence": selection,
        "arguments": {
            **vars(args),
            "source_run": str(source_run),
            "output_dir": str(args.output_dir),
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    np.savez_compressed(
        args.output_dir / "scores.npz",
        validation_labels=validation["labels"],
        test_labels=test["labels"],
        test_unknown=test["unknown"].astype(bool),
        test_prediction=prediction,
        **{
            f"validation_{method}": -validation_scores[method]
            for method in METHODS
        },
        **{f"test_{method}": -test_scores[method] for method in METHODS},
    )
    provenance = {
        "schema_version": "strict_v4_mlp_cadref_family_provenance_v1",
        "source_run": str(source_run),
        "source_artifact_sha256": source_sha256,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "scorer_module_sha256": sha256_file(
            Path(__file__).resolve().parent / "caeos" / "cadref_posthoc.py"
        ),
        "methods": list(METHODS),
        "postprocessor": postprocessor,
        "split_fingerprint": bundle.split_metadata.get("split_fingerprint"),
    }
    (args.output_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(reports, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
