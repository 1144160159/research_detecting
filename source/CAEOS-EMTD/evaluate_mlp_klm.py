from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from caeos.data import prepare_tabular_open_set
from caeos.kl_matching import evidence, fit_kl_matching_templates, kl_matching_risk
from caeos.multiclass import ConcatMLPClassifier
from evaluate_mlp_posthoc_ood import load_checkpoint, sha256_file, validate_source
from train_neural_open_set import choose_device, collect, report_for


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate official-formula KLM from a frozen strict MLP run"
    )
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=1024)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--epsilon", type=float, default=1e-12)
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
            raise ValueError("strict KLM matrix only accepts tabular runs")
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
        validation = collect(model, validation_loader, device)
        test = collect(model, test_loader, device)

        np.testing.assert_array_equal(
            validation["labels"], source_scores["validation_labels"]
        )
        np.testing.assert_array_equal(test["labels"], source_scores["test_labels"])
        np.testing.assert_array_equal(
            test["unknown"].astype(bool), source_scores["test_unknown"]
        )
    if validation["unknown"].astype(bool).any():
        raise ValueError("KLM template split must contain known validation samples only")

    templates = fit_kl_matching_templates(validation["logits"])
    validation_risk = kl_matching_risk(
        validation["logits"], templates, args.epsilon
    )
    test_risk = kl_matching_risk(test["logits"], templates, args.epsilon)
    prediction = test["logits"].argmax(axis=1)
    acceptance = float(arguments.get("known_acceptance", 0.95))
    threshold, report = report_for(
        test["labels"],
        test["unknown"].astype(bool),
        prediction,
        validation_risk,
        test_risk,
        acceptance,
    )

    source_sha256 = {name: sha256_file(path) for name, path in source_paths.items()}
    serialized_arguments = dict(vars(args))
    serialized_arguments.update(
        {"source_run": str(source_run), "output_dir": str(args.output_dir)}
    )
    result: dict[str, Any] = {
        "schema_version": "strict_v4_mlp_klm_v1",
        "model": "mlp_klm",
        "method": "klm",
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
        "validation_thresholds": {"klm": threshold},
        "reports": {"klm": report},
        "implementation": "OpenOOD KLM formula adapted to frozen tabular MLP softmax",
        "selection_evidence": {
            "protocol": "strict_frozen_checkpoint_known_validation_klm",
            "source_run": str(source_run),
            "source_artifact_sha256": source_sha256,
            "postprocessor": evidence(args.epsilon),
            "deployment_threshold": {
                "split": "known_only_validation",
                "known_acceptance_quantile": acceptance,
                "value": threshold,
            },
            "unknown_or_test_labels_used_for_fitting_or_selection": False,
            "test_labels_used_for_final_metrics_only": True,
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
        test_prediction=prediction,
        validation_klm=validation_risk,
        test_klm=test_risk,
        klm_templates=templates,
    )
    provenance = {
        "schema_version": "strict_v4_mlp_klm_provenance_v1",
        "source_run": str(source_run),
        "source_artifact_sha256": source_sha256,
        "implementation_sha256": sha256_file(Path(__file__).resolve()),
        "scorer_module_sha256": sha256_file(
            Path(__file__).resolve().parent / "caeos" / "kl_matching.py"
        ),
        "methods": ["klm"],
        "split_fingerprint": bundle.split_metadata.get("split_fingerprint"),
    }
    (args.output_dir / "provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"klm": report}, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
