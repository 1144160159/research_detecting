from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from caeos.data import prepare_tabular_open_set
from caeos.multiclass import ConcatMLPClassifier
from caeos.neural_open_set import DICECalibrator, ReActCalibrator, SHECalibrator
from train_neural_open_set import choose_device, collect, report_for


METHODS = ("react_energy", "dice", "she")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_checkpoint(path: Path) -> dict[str, Any]:
    try:
        return torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        return torch.load(path, map_location="cpu")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate ReAct, DICE, and SHE from a frozen strict MLP run"
    )
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--react-percentile", type=float, default=90.0)
    parser.add_argument("--dice-percentile", type=float, default=90.0)
    parser.add_argument("--temperature", type=float, default=1.0)
    return parser.parse_args()


def validate_source(
    metrics: dict[str, Any], checkpoint: dict[str, Any], source_scores: Any
) -> dict[str, Any]:
    arguments = checkpoint.get("arguments", {})
    if arguments.get("model") != "mlp" or metrics.get("model") != "mlp":
        raise ValueError("post-hoc OOD evaluation requires a frozen MLP source run")
    if list(checkpoint.get("class_names", [])) != list(metrics.get("known_class_names", [])):
        raise ValueError("source checkpoint and metrics class names differ")
    required = {"validation_labels", "test_labels", "test_unknown"}
    missing = required - set(source_scores.files)
    if missing:
        raise ValueError(f"source scores are missing arrays: {sorted(missing)}")
    return arguments


def main() -> None:
    args = parse_arguments()
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
            raise ValueError("strict post-hoc OOD matrix only accepts tabular runs")
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
        loader_options = {
            "batch_size": args.batch_size,
            "num_workers": args.num_workers,
            "pin_memory": device.type == "cuda",
        }
        train_loader = DataLoader(bundle.train, shuffle=False, **loader_options)
        validation_loader = DataLoader(bundle.validation, shuffle=False, **loader_options)
        test_loader = DataLoader(bundle.test, shuffle=False, **loader_options)
        model = ConcatMLPClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            int(arguments["hidden_dim"]),
            int(arguments["embedding_dim"]),
            float(arguments["dropout"]),
        ).to(device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        train_values = collect(model, train_loader, device)
        validation = collect(model, validation_loader, device)
        test = collect(model, test_loader, device)

        np.testing.assert_array_equal(validation["labels"], source_scores["validation_labels"])
        np.testing.assert_array_equal(test["labels"], source_scores["test_labels"])
        np.testing.assert_array_equal(test["unknown"].astype(bool), source_scores["test_unknown"])

    weight = model.classifier.weight.detach().cpu().numpy()
    bias = model.classifier.bias.detach().cpu().numpy()
    acceptance = float(arguments.get("known_acceptance", 0.95))
    reports: dict[str, Any] = {}
    thresholds: dict[str, float] = {}
    validation_risks: dict[str, np.ndarray] = {}
    test_risks: dict[str, np.ndarray] = {}
    test_predictions: dict[str, np.ndarray] = {}
    postprocessors: dict[str, Any] = {}

    react = ReActCalibrator(args.react_percentile, args.temperature)
    react.fit(train_values["embedding"], weight, bias)
    validation_risks["react_energy"] = react.score(validation["embedding"])
    test_risks["react_energy"] = react.score(test["embedding"])
    test_predictions["react_energy"] = react.logits(test["embedding"]).argmax(axis=1)
    postprocessors["react_energy"] = react.evidence()

    dice = DICECalibrator(args.dice_percentile, args.temperature)
    dice.fit(train_values["embedding"], weight, bias)
    validation_risks["dice"] = dice.score(validation["embedding"])
    test_risks["dice"] = dice.score(test["embedding"])
    test_predictions["dice"] = dice.logits(test["embedding"]).argmax(axis=1)
    postprocessors["dice"] = dice.evidence()

    she = SHECalibrator()
    she.fit(train_values["embedding"], train_values["logits"], train_values["labels"])
    validation_risks["she"] = she.score(validation["embedding"], validation["logits"])
    test_risks["she"] = she.score(test["embedding"], test["logits"])
    test_predictions["she"] = test["logits"].argmax(axis=1)
    postprocessors["she"] = she.evidence()

    for name in METHODS:
        thresholds[name], reports[name] = report_for(
            test["labels"],
            test["unknown"].astype(bool),
            test_predictions[name],
            validation_risks[name],
            test_risks[name],
            acceptance,
        )

    source_sha256 = {name: sha256_file(path) for name, path in source_paths.items()}
    result = {
        "schema_version": "strict_v4_mlp_posthoc_ood_v1",
        "model": "mlp_posthoc_ood",
        "method": "mlp_posthoc_ood_suite",
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
        "implementation": (
            "Official ReAct, DICE, and SHE formulas adapted to the frozen shared "
            "tabular MLP; no retraining and no unknown-label fitting"
        ),
        "selection_evidence": {
            "protocol": "strict_known_only_frozen_checkpoint_posthoc",
            "source_run": str(source_run),
            "source_artifact_sha256": source_sha256,
            "postprocessors": postprocessors,
            "deployment_thresholds": {
                name: {
                    "split": "known_only_validation",
                    "known_acceptance_quantile": acceptance,
                    "value": value,
                }
                for name, value in thresholds.items()
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "arguments": vars(args) | {"source_run": str(source_run), "output_dir": str(args.output_dir)},
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    score_archive: dict[str, np.ndarray] = {
        "validation_labels": validation["labels"],
        "test_labels": test["labels"],
        "test_unknown": test["unknown"].astype(bool),
    }
    for name in METHODS:
        score_archive[f"validation_{name}"] = validation_risks[name]
        score_archive[f"test_{name}"] = test_risks[name]
        score_archive[f"prediction_{name}"] = test_predictions[name]
    np.savez_compressed(args.output_dir / "scores.npz", **score_archive)
    provenance = {
        "schema_version": "strict_v4_mlp_posthoc_ood_provenance_v1",
        "source_run": str(source_run),
        "source_artifact_sha256": source_sha256,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "calibrator_module_sha256": sha256_file(
            (Path(__file__).resolve().parent / "caeos" / "neural_open_set.py")
        ),
        "methods": list(METHODS),
        "split_fingerprint": bundle.split_metadata.get("split_fingerprint"),
    }
    (args.output_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(reports, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
