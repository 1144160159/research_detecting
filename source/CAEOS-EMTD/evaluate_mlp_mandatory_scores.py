from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from caeos.data import prepare_tabular_open_set
from caeos.mandatory_scores import PrototypeDistanceCalibrator, evidence, shannon_entropy_risk
from caeos.multiclass import ConcatMLPClassifier
from evaluate_mlp_posthoc_ood import load_checkpoint, sha256_file, validate_source
from train_neural_open_set import choose_device, collect, report_for


METHODS = ("shannon_entropy", "prototype_distance")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate mandatory Entropy and Prototype scores from a frozen strict MLP")
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--torch-threads", type=int, default=1)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    torch.set_num_threads(args.torch_threads)
    source_run = args.source_run.resolve()
    source_paths = {name: source_run / name for name in ("metrics.json", "scores.npz", "model.pt")}
    missing = [str(path) for path in source_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing source artifacts: " + ", ".join(missing))
    metrics = json.loads(source_paths["metrics.json"].read_text(encoding="utf-8"))
    checkpoint = load_checkpoint(source_paths["model.pt"])
    with np.load(source_paths["scores.npz"], allow_pickle=False) as source_scores:
        arguments = validate_source(metrics, checkpoint, source_scores)
        if arguments.get("dataset") != "tabular":
            raise ValueError("mandatory score matrix only accepts tabular runs")
        config_path = Path(str(arguments["config"]))
        if not config_path.is_absolute():
            config_path = Path.cwd() / config_path
        config = json.loads(config_path.read_text(encoding="utf-8"))
        unknown_classes = [item.strip() for item in str(arguments["unknown_classes"]).split(",") if item.strip()]
        bundle = prepare_tabular_open_set(
            str(arguments["csv"]), config, unknown_classes, str(arguments["benign_class"]),
            int(arguments["max_per_class"]), int(arguments["chunksize"]), int(arguments["seed"]),
            str(arguments["split_strategy"]),
        )
        if bundle.class_names != list(checkpoint["class_names"]):
            raise ValueError("reconstructed data and checkpoint class names differ")
        if list(bundle.input_dims) != list(checkpoint["input_dims"]):
            raise ValueError("reconstructed data and checkpoint input dimensions differ")
        reconstructed_split = json.loads(json.dumps(bundle.split_metadata, ensure_ascii=False, sort_keys=True))
        if reconstructed_split != metrics.get("split_metadata"):
            raise ValueError("reconstructed split metadata differs from frozen source")
        device = choose_device(args.device)
        loader_options = {"batch_size": args.batch_size, "num_workers": args.num_workers, "pin_memory": device.type == "cuda"}
        model = ConcatMLPClassifier(
            bundle.input_dims, len(bundle.class_names), int(arguments["hidden_dim"]),
            int(arguments["embedding_dim"]), float(arguments["dropout"]),
        ).to(device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        train = collect(model, DataLoader(bundle.train, shuffle=False, **loader_options), device)
        validation = collect(model, DataLoader(bundle.validation, shuffle=False, **loader_options), device)
        test = collect(model, DataLoader(bundle.test, shuffle=False, **loader_options), device)
        np.testing.assert_array_equal(validation["labels"], source_scores["validation_labels"])
        np.testing.assert_array_equal(test["labels"], source_scores["test_labels"])
        np.testing.assert_array_equal(test["unknown"].astype(bool), source_scores["test_unknown"])

    prototype = PrototypeDistanceCalibrator().fit(train["embedding"], train["labels"])
    validation_risks = {
        "shannon_entropy": shannon_entropy_risk(validation["logits"]),
        "prototype_distance": prototype.score(validation["embedding"]),
    }
    test_risks = {
        "shannon_entropy": shannon_entropy_risk(test["logits"]),
        "prototype_distance": prototype.score(test["embedding"]),
    }
    prediction = test["logits"].argmax(axis=1)
    acceptance = float(arguments.get("known_acceptance", 0.95))
    reports: dict[str, Any] = {}
    thresholds: dict[str, float] = {}
    for name in METHODS:
        thresholds[name], reports[name] = report_for(
            test["labels"], test["unknown"].astype(bool), prediction,
            validation_risks[name], test_risks[name], acceptance,
        )
    source_sha256 = {name: sha256_file(path) for name, path in source_paths.items()}
    serialized_arguments = dict(vars(args))
    serialized_arguments.update({"source_run": str(source_run), "output_dir": str(args.output_dir)})
    result = {
        "schema_version": "strict_v4_mlp_mandatory_scores_v1", "model": "mlp_mandatory_scores",
        "method": "mlp_mandatory_score_suite", "unknown_classes": unknown_classes,
        "seed": int(arguments["seed"]), "known_class_names": bundle.class_names,
        "sample_counts": bundle.sample_counts, "split_metadata": bundle.split_metadata,
        "split_sizes": {"train": len(bundle.train), "validation": len(bundle.validation), "test": len(bundle.test), "test_unknown": int(test["unknown"].sum())},
        "validation_thresholds": thresholds, "reports": reports,
        "implementation": "standard Shannon entropy and nearest known-class centroid distance on one frozen-MLP forward pass",
        "selection_evidence": {
            "protocol": "strict_full102_mandatory_scores_no_ood_tuning",
            "source_run": str(source_run), "source_artifact_sha256": source_sha256,
            "postprocessors": {**evidence(), "prototype_distance": prototype.evidence()},
            "deployment_thresholds": {
                name: {"split": "known_only_validation", "known_acceptance_quantile": acceptance, "value": value}
                for name, value in thresholds.items()
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "diagnostics": {
            name: {"validation_risk_std": float(validation_risks[name].std()), "test_risk_std": float(test_risks[name].std())}
            for name in METHODS
        },
        "arguments": serialized_arguments,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    archive = {
        "validation_labels": validation["labels"], "test_labels": test["labels"],
        "test_unknown": test["unknown"].astype(bool), "test_prediction": prediction,
    }
    for name in METHODS:
        archive["validation_" + name] = validation_risks[name]
        archive["test_" + name] = test_risks[name]
    np.savez_compressed(args.output_dir / "scores.npz", **archive)
    provenance = {
        "schema_version": "strict_v4_mlp_mandatory_scores_provenance_v1",
        "source_run": str(source_run), "source_artifact_sha256": source_sha256,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "scorer_module_sha256": sha256_file(Path(__file__).resolve().parent / "caeos" / "mandatory_scores.py"),
        "methods": list(METHODS), "split_fingerprint": bundle.split_metadata.get("split_fingerprint"),
    }
    (args.output_dir / "provenance.json").write_text(json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(reports, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
