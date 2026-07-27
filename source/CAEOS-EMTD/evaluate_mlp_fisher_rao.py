from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from torch.utils.data import DataLoader

from caeos.data import prepare_tabular_open_set
from caeos.fisher_rao_posthoc import evidence, fisher_rao_score_batch, fit_fisher_rao
from caeos.multiclass import ConcatMLPClassifier
from evaluate_mlp_posthoc_ood import load_checkpoint, sha256_file, validate_source
from train_neural_open_set import choose_device, collect, report_for


METHODS = ("fim_standard", "fim_tensor", "fim_additive")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate ICLR 2026 Fisher-Rao FIM Trace from a frozen strict MLP run"
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
            raise ValueError("strict Fisher-Rao matrix only accepts tabular runs")
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
        model = ConcatMLPClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            int(arguments["hidden_dim"]),
            int(arguments["embedding_dim"]),
            float(arguments["dropout"]),
        ).to(device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        model.eval()
        train = collect(model, DataLoader(bundle.train, shuffle=False, **options), device)
        validation = collect(
            model, DataLoader(bundle.validation, shuffle=False, **options), device
        )
        test = collect(model, DataLoader(bundle.test, shuffle=False, **options), device)
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

    state = fit_fisher_rao(train["embedding"], train["logits"], train["labels"])
    train_scores, train_diagnostics = fisher_rao_score_batch(
        train["embedding"], train["logits"], state
    )
    validation_scores, validation_diagnostics = fisher_rao_score_batch(
        validation["embedding"], validation["logits"], state
    )
    test_scores, test_diagnostics = fisher_rao_score_batch(
        test["embedding"], test["logits"], state
    )
    acceptance = float(arguments.get("known_acceptance", 0.95))
    thresholds = {}
    reports = {}
    for method in METHODS:
        threshold, report = report_for(
            test["labels"],
            test["unknown"].astype(bool),
            prediction,
            -validation_scores[method],
            -test_scores[method],
            acceptance,
        )
        thresholds[method] = threshold
        reports[method] = report

    source_sha256 = {name: sha256_file(path) for name, path in source_paths.items()}
    postprocessor = evidence()
    selection = {
        "protocol": "strict_frozen_checkpoint_ICLR2026_Fisher_Rao_ID_only",
        "source_run": str(source_run),
        "source_artifact_sha256": source_sha256,
        "postprocessor": postprocessor,
        "fit_diagnostics": {
            "known_training_sample_count": state.train_sample_count,
            "class_count": state.class_count,
            "feature_subspace_rank": int(state.feature_basis.shape[1]),
            "probability_subspace_rank": int(state.probability_basis.shape[1]),
            "lambda_magnitude_signed": -state.lambda_magnitude,
            "lambda_residual_signed": state.lambda_residual,
            "train_scores": train_diagnostics,
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
        "schema_version": "strict_v4_mlp_fisher_rao_family_v1",
        "model": "mlp_fisher_rao_family",
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
        **{f"validation_{name}": -validation_scores[name] for name in METHODS},
        **{f"test_{name}": -test_scores[name] for name in METHODS},
    )
    provenance = {
        "schema_version": "strict_v4_mlp_fisher_rao_family_provenance_v1",
        "source_run": str(source_run),
        "source_artifact_sha256": source_sha256,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "scorer_module_sha256": sha256_file(
            Path(__file__).resolve().parent / "caeos" / "fisher_rao_posthoc.py"
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
