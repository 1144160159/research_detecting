from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from torch.utils.data import DataLoader

from caeos.adascale_posthoc import (
    AdaSCALECalibrator,
    collect_adascale_features,
)
from caeos.data import prepare_tabular_open_set
from caeos.multiclass import ConcatMLPClassifier
from evaluate_mlp_posthoc_ood import load_checkpoint, sha256_file, validate_source
from train_neural_open_set import choose_device, report_for


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate fixed AdaSCALE-A from a frozen strict MLP run"
    )
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--p-min", type=float, default=60.0)
    parser.add_argument("--p-max", type=float, default=85.0)
    parser.add_argument("--k1-percent", type=float, default=1.0)
    parser.add_argument("--k2-percent", type=float, default=5.0)
    parser.add_argument("--lmbda", type=float, default=10.0)
    parser.add_argument("--perturb-fraction", type=float, default=0.05)
    parser.add_argument("--epsilon", type=float, default=0.5)
    parser.add_argument("--temperature", type=float, default=1.0)
    return parser.parse_args()


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
            raise ValueError("strict AdaSCALE matrix only accepts tabular runs")
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
        validation = collect_adascale_features(
            model,
            validation_loader,
            device,
            perturb_fraction=args.perturb_fraction,
            epsilon=args.epsilon,
        )
        test = collect_adascale_features(
            model,
            test_loader,
            device,
            perturb_fraction=args.perturb_fraction,
            epsilon=args.epsilon,
        )
        np.testing.assert_array_equal(
            validation["labels"], source_scores["validation_labels"]
        )
        np.testing.assert_array_equal(test["labels"], source_scores["test_labels"])
        np.testing.assert_array_equal(
            test["unknown"].astype(bool), source_scores["test_unknown"]
        )

    calibrator = AdaSCALECalibrator(
        p_min=args.p_min,
        p_max=args.p_max,
        k1_percent=args.k1_percent,
        k2_percent=args.k2_percent,
        lmbda=args.lmbda,
        perturb_fraction=args.perturb_fraction,
        epsilon=args.epsilon,
        temperature=args.temperature,
    )
    calibrator.fit(
        validation["feature"],
        validation["feature_perturbed"],
        model.classifier.weight.detach().cpu().numpy(),
        model.classifier.bias.detach().cpu().numpy(),
    )
    validation_output = calibrator.evaluate(
        validation["feature"], validation["feature_perturbed"]
    )
    test_output = calibrator.evaluate(test["feature"], test["feature_perturbed"])
    acceptance = float(arguments.get("known_acceptance", 0.95))
    threshold, report = report_for(
        test["labels"],
        test["unknown"].astype(bool),
        test_output["prediction"],
        validation_output["risk"],
        test_output["risk"],
        acceptance,
    )

    source_sha256 = {name: sha256_file(path) for name, path in source_paths.items()}
    serialized_arguments = dict(vars(args))
    serialized_arguments.update(
        {"source_run": str(source_run), "output_dir": str(args.output_dir)}
    )
    result: dict[str, Any] = {
        "schema_version": "strict_v4_mlp_adascale_v1",
        "model": "mlp_adascale_a_60_85",
        "method": "adascale_a_60_85",
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
        "validation_thresholds": {"adascale_a_60_85": threshold},
        "reports": {"adascale_a_60_85": report},
        "implementation": (
            "paper-consistent AdaSCALE-A with fixed official defaults on frozen tabular MLP"
        ),
        "selection_evidence": {
            "protocol": "strict_frozen_checkpoint_fixed_adascale_a_60_85",
            "source_run": str(source_run),
            "source_artifact_sha256": source_sha256,
            "postprocessor": calibrator.evidence(),
            "deployment_threshold": {
                "split": "known_only_validation",
                "known_acceptance_quantile": acceptance,
                "value": threshold,
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
        },
        "diagnostics": {
            "validation_percentile_min": float(validation_output["percentile"].min()),
            "validation_percentile_max": float(validation_output["percentile"].max()),
            "test_percentile_min": float(test_output["percentile"].min()),
            "test_percentile_max": float(test_output["percentile"].max()),
            "validation_factor_mean": float(validation_output["factor"].mean()),
            "test_factor_mean": float(test_output["factor"].mean()),
        },
        "arguments": serialized_arguments,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    np.savez_compressed(
        args.output_dir / "scores.npz",
        validation_labels=validation["labels"],
        test_labels=test["labels"],
        test_unknown=test["unknown"].astype(bool),
        test_prediction=test_output["prediction"],
        validation_adascale_a_60_85=validation_output["risk"],
        test_adascale_a_60_85=test_output["risk"],
        validation_percentile=validation_output["percentile"],
        test_percentile=test_output["percentile"],
    )
    provenance = {
        "schema_version": "strict_v4_mlp_adascale_provenance_v1",
        "source_run": str(source_run),
        "source_artifact_sha256": source_sha256,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "scorer_module_sha256": sha256_file(
            Path(__file__).resolve().parent / "caeos" / "adascale_posthoc.py"
        ),
        "methods": ["adascale_a_60_85"],
        "split_fingerprint": bundle.split_metadata.get("split_fingerprint"),
    }
    (args.output_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps({"adascale_a_60_85": report}, ensure_ascii=False, sort_keys=True),
        flush=True,
    )


if __name__ == "__main__":
    main()
