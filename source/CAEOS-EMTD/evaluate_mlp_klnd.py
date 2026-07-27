from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from caeos.data import prepare_tabular_open_set
from caeos.klnd import KLogitNeighborDistance, METHODS
from caeos.multiclass import ConcatMLPClassifier
from evaluate_mlp_posthoc_ood import load_checkpoint, sha256_file, validate_source
from train_neural_open_set import choose_device, collect, report_for


OFFICIAL_COMMIT = "673320b86dcaf72dcdeae5159b3b8ce91ac5e19c"
PAPER_DOI = "10.1016/j.comnet.2023.109991"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate paper-faithful k-LND1/2/3 on a frozen strict MLP run"
    )
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--torch-threads", type=int, default=1)
    parser.add_argument("--percentile", type=float, default=0.9)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    torch.set_num_threads(args.torch_threads)
    source_run = args.source_run.resolve()
    source_paths = {
        name: source_run / name
        for name in ("metrics.json", "scores.npz", "model.pt")
    }
    missing = [str(path) for path in source_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing source artifacts: " + ", ".join(missing))
    metrics = json.loads(source_paths["metrics.json"].read_text(encoding="utf-8"))
    checkpoint = load_checkpoint(source_paths["model.pt"])
    with np.load(source_paths["scores.npz"], allow_pickle=False) as source_scores:
        arguments = validate_source(metrics, checkpoint, source_scores)
        if arguments.get("dataset") != "tabular":
            raise ValueError("strict k-LND matrix only accepts tabular runs")
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
        model = ConcatMLPClassifier(
            bundle.input_dims,
            len(bundle.class_names),
            int(arguments["hidden_dim"]),
            int(arguments["embedding_dim"]),
            float(arguments["dropout"]),
        ).to(device)
        model.load_state_dict(checkpoint["model_state"], strict=True)
        train = collect(
            model, DataLoader(bundle.train, shuffle=False, **loader_options), device
        )
        validation = collect(
            model,
            DataLoader(bundle.validation, shuffle=False, **loader_options),
            device,
        )
        test = collect(
            model, DataLoader(bundle.test, shuffle=False, **loader_options), device
        )
        np.testing.assert_array_equal(
            validation["labels"], source_scores["validation_labels"]
        )
        np.testing.assert_array_equal(test["labels"], source_scores["test_labels"])
        np.testing.assert_array_equal(
            test["unknown"].astype(bool), source_scores["test_unknown"]
        )

    calibrator = KLogitNeighborDistance(percentile=args.percentile).fit(
        train["logits"],
        train["labels"],
        validation["logits"],
        validation["labels"],
    )
    validation_output = calibrator.evaluate(validation["logits"])
    test_output = calibrator.evaluate(test["logits"])
    acceptance = float(arguments.get("known_acceptance", 0.95))
    thresholds: dict[str, float] = {}
    reports: dict[str, Any] = {}
    for method in METHODS:
        thresholds[method], reports[method] = report_for(
            test["labels"],
            test["unknown"].astype(bool),
            test_output.prediction,
            validation_output.risks[method],
            test_output.risks[method],
            acceptance,
        )
    source_sha256 = {
        name: sha256_file(path) for name, path in source_paths.items()
    }
    serialized_arguments = dict(vars(args))
    serialized_arguments.update(
        {"source_run": str(source_run), "output_dir": str(args.output_dir)}
    )
    result: dict[str, Any] = {
        "schema_version": "strict_v4_mlp_klnd_v1",
        "model": "mlp_klnd",
        "method": "mlp_klnd_suite",
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
            "frozen strict MLP logits plus paper k-LND1/2/3 class centers "
            "and correct-known-validation distance calibration"
        ),
        "selection_evidence": {
            "protocol": "strict_frozen_checkpoint_klnd_known_only",
            "paper_doi": PAPER_DOI,
            "official_repository_commit": OFFICIAL_COMMIT,
            "source_run": str(source_run),
            "source_artifact_sha256": source_sha256,
            "klnd": calibrator.evidence(),
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
        "diagnostics": {
            method: {
                "validation_risk_std": float(
                    validation_output.risks[method].std()
                ),
                "test_risk_std": float(test_output.risks[method].std()),
                "validation_native_reject_fraction": float(
                    validation_output.native_reject[method].mean()
                ),
                "test_native_reject_fraction": float(
                    test_output.native_reject[method].mean()
                ),
            }
            for method in METHODS
        },
        "arguments": serialized_arguments,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    archive: dict[str, np.ndarray] = {
        "validation_labels": validation["labels"],
        "test_labels": test["labels"],
        "test_unknown": test["unknown"].astype(bool),
        "test_prediction": test_output.prediction,
    }
    for method in METHODS:
        archive[f"validation_{method}"] = validation_output.risks[method]
        archive[f"test_{method}"] = test_output.risks[method]
    np.savez_compressed(args.output_dir / "scores.npz", **archive)
    provenance = {
        "schema_version": "strict_v4_mlp_klnd_provenance_v1",
        "source_run": str(source_run),
        "source_artifact_sha256": source_sha256,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "scorer_module_sha256": sha256_file(
            Path(__file__).resolve().parent / "caeos" / "klnd.py"
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
