from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path
from typing import Dict

import numpy as np
import torch
from torch.utils.data import DataLoader, WeightedRandomSampler

from caeos.data import make_synthetic_open_set, prepare_tabular_open_set
from caeos.evidence_temperature import (
    apply_evidence_temperature,
    fit_known_evidence_temperature,
)
from caeos.metrics import evaluate_open_set
from caeos.model import ConflictAwareEvidentialNet
from caeos.open_set import DiagnosticConformalCalibrator, OpenSetCalibrator
from caeos.training import collect_outputs, evaluate_counterfactual_gate, train_model


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Conflict-aware evidential open-set traffic detection"
    )
    parser.add_argument("--dataset", choices=("synthetic", "tabular"), default="synthetic")
    parser.add_argument("--csv", default=None)
    parser.add_argument("--config", default="configs/nf_unsw_nb15.json")
    parser.add_argument("--unknown-classes", nargs="+", default=["Backdoor"])
    parser.add_argument("--benign-class", default="Benign")
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument(
        "--split-strategy",
        choices=("random", "fingerprint_grouped", "capture_grouped"),
        default="random",
    )
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--embedding-dim", type=int, default=64)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--conflict-scale", type=float, default=2.0)
    parser.add_argument(
        "--encoder-profile",
        choices=(
            "uniform_mlp",
            "mal_tls_heterogeneous",
            "mal_tls_conservative_residual",
            "mal_tls_geometry_preserving_adapter",
            "mal_tls_counterfactual_conflict_gate",
        ),
        default="uniform_mlp",
    )
    parser.add_argument("--evidence-temperature-calibration", action="store_true")
    parser.add_argument("--initial-checkpoint", type=Path, default=None)
    parser.add_argument("--freeze-base-for-adapter", action="store_true")
    parser.add_argument("--consistency-weight", type=float, default=0.0)
    parser.add_argument("--counterfactual-weight", type=float, default=0.0)
    parser.add_argument("--counterfactual-margin", type=float, default=0.05)
    parser.add_argument(
        "--counterfactual-nonattenuation-weight", type=float, default=0.1
    )
    parser.add_argument(
        "--counterfactual-gate-max-log-attenuation", type=float, default=1.0
    )
    parser.add_argument("--prefer-last-epoch-on-known-f1-tie", action="store_true")
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--annealing-epochs", type=int, default=8)
    parser.add_argument("--corruption-probability", type=float, default=0.20)
    parser.add_argument("--corruption-noise", type=float, default=1.0)
    parser.add_argument("--known-acceptance", type=float, default=0.95)
    parser.add_argument(
        "--calibrator", choices=("weighted", "conformal"), default="weighted"
    )
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--output-dir", default="runs/latest")
    parser.add_argument("--no-amp", action="store_true")
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def choose_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(name)


def make_weighted_sampler(labels: torch.Tensor) -> WeightedRandomSampler:
    counts = torch.bincount(labels)
    class_weight = 1.0 / counts.to(torch.float64).clamp_min(1.0)
    sample_weight = class_weight[labels]
    return WeightedRandomSampler(sample_weight, len(labels), replacement=True)


def json_dump(path: Path, value: Dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)


def encoder_kinds_for_profile(profile: str, modality_names: list[str]) -> list[str]:
    if profile in {
        "uniform_mlp",
        "mal_tls_geometry_preserving_adapter",
        "mal_tls_counterfactual_conflict_gate",
    }:
        return ["mlp"] * len(modality_names)
    if profile not in {"mal_tls_heterogeneous", "mal_tls_conservative_residual"}:
        raise ValueError(f"unknown encoder profile: {profile}")
    expected = {
        "tls_handshake": (
            "tls_gated"
            if profile == "mal_tls_heterogeneous"
            else "tls_residual_025"
        ),
        "ip_flow_statistics": "mlp",
        "payload_statistics": "mlp",
        "packet_sequence": (
            "sequence_tcn"
            if profile == "mal_tls_heterogeneous"
            else "sequence_residual_025"
        ),
    }
    if set(modality_names) != set(expected):
        raise ValueError(
            f"{profile} requires TLS, IP flow, payload and packet sequence modalities"
        )
    return [expected[name] for name in modality_names]


def evidence_adapter_kinds_for_profile(
    profile: str, modality_names: list[str]
) -> list[str]:
    if profile != "mal_tls_geometry_preserving_adapter":
        return ["none"] * len(modality_names)
    expected = {
        "tls_handshake": "tls_gated",
        "ip_flow_statistics": "none",
        "payload_statistics": "none",
        "packet_sequence": "sequence_tcn",
    }
    if set(modality_names) != set(expected):
        raise ValueError(
            "mal_tls_geometry_preserving_adapter requires TLS, IP flow, payload "
            "and packet sequence modalities"
        )
    return [expected[name] for name in modality_names]


def load_and_freeze_geometry_preserving_adapter(
    model: ConflictAwareEvidentialNet,
    checkpoint: dict[str, object],
) -> None:
    missing, unexpected = model.load_state_dict(checkpoint["model_state"], strict=False)
    if unexpected:
        raise ValueError(f"unexpected reference checkpoint keys: {unexpected}")
    if any(not key.startswith("evidence_adapters.") for key in missing):
        raise ValueError(f"non-adapter checkpoint keys are missing: {missing}")
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    for parameter in model.evidence_adapters.parameters():
        parameter.requires_grad_(True)
    if not any(parameter.requires_grad for parameter in model.parameters()):
        raise ValueError("geometry-preserving adapter has no trainable parameters")


def load_and_freeze_counterfactual_conflict_gate(
    model: ConflictAwareEvidentialNet,
    checkpoint: dict[str, object],
) -> None:
    missing, unexpected = model.load_state_dict(checkpoint["model_state"], strict=False)
    if unexpected:
        raise ValueError(f"unexpected reference checkpoint keys: {unexpected}")
    if any(not key.startswith("counterfactual_conflict_gate.") for key in missing):
        raise ValueError(f"non-gate checkpoint keys are missing: {missing}")
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    if model.counterfactual_conflict_gate is None:
        raise ValueError("counterfactual conflict gate is not configured")
    for parameter in model.counterfactual_conflict_gate.parameters():
        parameter.requires_grad_(True)
    if not any(parameter.requires_grad for parameter in model.parameters()):
        raise ValueError("counterfactual conflict gate has no trainable parameters")


def main() -> None:
    args = parse_arguments()
    set_seed(args.seed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dataset == "synthetic":
        bundle = make_synthetic_open_set(seed=args.seed)
    else:
        if not args.csv:
            raise ValueError("--csv is required for tabular data")
        with open(args.config, "r", encoding="utf-8") as handle:
            data_config = json.load(handle)
        bundle = prepare_tabular_open_set(
            args.csv,
            data_config,
            args.unknown_classes,
            args.benign_class,
            args.max_per_class,
            args.chunksize,
            args.seed,
            args.split_strategy,
        )

    print("class_names=" + json.dumps(bundle.class_names, ensure_ascii=False))
    print("sample_counts=" + json.dumps(bundle.sample_counts, ensure_ascii=False))
    print("split_sizes=train:%d validation:%d test:%d" % (
        len(bundle.train), len(bundle.validation), len(bundle.test)
    ))

    train_loader = DataLoader(
        bundle.train,
        batch_size=args.batch_size,
        sampler=make_weighted_sampler(bundle.train.labels),
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    train_calibration_loader = DataLoader(
        bundle.train,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    validation_loader = DataLoader(
        bundle.validation,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    test_loader = DataLoader(
        bundle.test,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    device = choose_device(args.device)
    print("device=%s torch=%s" % (device, torch.__version__))
    encoder_kinds = encoder_kinds_for_profile(
        args.encoder_profile, bundle.modality_names
    )
    evidence_adapter_kinds = evidence_adapter_kinds_for_profile(
        args.encoder_profile, bundle.modality_names
    )
    model = ConflictAwareEvidentialNet(
        bundle.input_dims,
        len(bundle.class_names),
        args.hidden_dim,
        args.embedding_dim,
        args.dropout,
        args.conflict_scale,
        encoder_kinds=encoder_kinds,
        evidence_adapter_kinds=evidence_adapter_kinds,
        counterfactual_conflict_gate=(
            args.encoder_profile == "mal_tls_counterfactual_conflict_gate"
        ),
        counterfactual_gate_max_log_attenuation=(
            args.counterfactual_gate_max_log_attenuation
        ),
    ).to(device)

    teacher_model = None
    if args.encoder_profile == "mal_tls_geometry_preserving_adapter":
        if args.initial_checkpoint is None or not args.freeze_base_for_adapter:
            raise ValueError(
                "geometry-preserving adapter requires --initial-checkpoint and "
                "--freeze-base-for-adapter"
            )
        if args.consistency_weight <= 0.0:
            raise ValueError("geometry-preserving adapter requires positive consistency")
        checkpoint = torch.load(args.initial_checkpoint, map_location="cpu")
        if checkpoint["input_dims"] != bundle.input_dims:
            raise ValueError("reference checkpoint input dimensions differ")
        if checkpoint["class_names"] != bundle.class_names:
            raise ValueError("reference checkpoint class order differs")
        if checkpoint["modality_names"] != bundle.modality_names:
            raise ValueError("reference checkpoint modality order differs")
        load_and_freeze_geometry_preserving_adapter(model, checkpoint)
        teacher_model = ConflictAwareEvidentialNet(
            bundle.input_dims,
            len(bundle.class_names),
            args.hidden_dim,
            args.embedding_dim,
            args.dropout,
            args.conflict_scale,
            encoder_kinds=encoder_kinds,
        ).to(device)
        teacher_model.load_state_dict(checkpoint["model_state"])
        teacher_model.requires_grad_(False)
        teacher_model.eval()
    elif args.encoder_profile == "mal_tls_counterfactual_conflict_gate":
        if args.initial_checkpoint is None or not args.freeze_base_for_adapter:
            raise ValueError(
                "counterfactual conflict gate requires --initial-checkpoint and "
                "--freeze-base-for-adapter"
            )
        if args.consistency_weight <= 0.0 or args.counterfactual_weight <= 0.0:
            raise ValueError(
                "counterfactual conflict gate requires positive consistency and "
                "counterfactual weights"
            )
        if not args.prefer_last_epoch_on_known_f1_tie:
            raise ValueError(
                "counterfactual conflict gate requires the frozen F1-tie selection rule"
            )
        checkpoint = torch.load(args.initial_checkpoint, map_location="cpu")
        if checkpoint["input_dims"] != bundle.input_dims:
            raise ValueError("reference checkpoint input dimensions differ")
        if checkpoint["class_names"] != bundle.class_names:
            raise ValueError("reference checkpoint class order differs")
        if checkpoint["modality_names"] != bundle.modality_names:
            raise ValueError("reference checkpoint modality order differs")
        load_and_freeze_counterfactual_conflict_gate(model, checkpoint)
        teacher_model = ConflictAwareEvidentialNet(
            bundle.input_dims,
            len(bundle.class_names),
            args.hidden_dim,
            args.embedding_dim,
            args.dropout,
            args.conflict_scale,
            encoder_kinds=encoder_kinds,
        ).to(device)
        teacher_model.load_state_dict(checkpoint["model_state"])
        teacher_model.requires_grad_(False)
        teacher_model.eval()
    elif args.initial_checkpoint is not None or args.freeze_base_for_adapter:
        raise ValueError("checkpoint adapter options require the adapter profile")

    history = train_model(
        model,
        train_loader,
        validation_loader,
        device,
        bundle.benign_index,
        args.epochs,
        args.learning_rate,
        args.weight_decay,
        args.annealing_epochs,
        args.corruption_probability,
        args.corruption_noise,
        not args.no_amp,
        teacher_model=teacher_model,
        consistency_weight=args.consistency_weight,
        counterfactual_weight=args.counterfactual_weight,
        counterfactual_margin=args.counterfactual_margin,
        counterfactual_modality_indices=(0, 3),
        counterfactual_nonattenuation_weight=(
            args.counterfactual_nonattenuation_weight
        ),
        prefer_last_epoch_on_known_f1_tie=(
            args.prefer_last_epoch_on_known_f1_tie
        ),
    )

    train_output, train_labels, _ = collect_outputs(
        model, train_calibration_loader, device
    )
    validation_output, validation_labels, validation_unknown = collect_outputs(
        model, validation_loader, device
    )
    evidence_temperature = 1.0
    evidence_temperature_nll = None
    if args.evidence_temperature_calibration:
        if bool(validation_unknown.any()):
            raise ValueError("evidence temperature calibration requires known-only validation")
        evidence_temperature, evidence_temperature_nll = (
            fit_known_evidence_temperature(validation_output, validation_labels)
        )
        train_output = apply_evidence_temperature(train_output, evidence_temperature)
        validation_output = apply_evidence_temperature(
            validation_output, evidence_temperature
        )
    if args.calibrator == "conformal":
        calibrator = DiagnosticConformalCalibrator(
            len(bundle.class_names),
            bundle.benign_index,
            known_acceptance=args.known_acceptance,
        )
    else:
        calibrator = OpenSetCalibrator(
            len(bundle.class_names),
            bundle.benign_index,
            known_acceptance=args.known_acceptance,
        )
    calibrator.fit_prototypes(train_output["fused_embedding"], train_labels)
    if args.calibrator == "conformal":
        calibrator.fit_reference(train_output, train_labels)
    calibrator.fit_known_validation(validation_output)

    test_output, test_labels, test_unknown = collect_outputs(model, test_loader, device)
    if args.evidence_temperature_calibration:
        test_output = apply_evidence_temperature(test_output, evidence_temperature)
    report = evaluate_open_set(test_output, test_labels, test_unknown, calibrator)
    report["calibrator"] = args.calibrator
    report["encoder_profile"] = args.encoder_profile
    report["encoder_kinds"] = encoder_kinds
    report["evidence_adapter_kinds"] = evidence_adapter_kinds
    report["geometry_preserving_frozen_base"] = bool(args.freeze_base_for_adapter)
    report["known_only_consistency_weight"] = float(args.consistency_weight)
    report["known_only_counterfactual_weight"] = float(args.counterfactual_weight)
    report["counterfactual_margin"] = float(args.counterfactual_margin)
    report["counterfactual_gate_max_log_attenuation"] = float(
        args.counterfactual_gate_max_log_attenuation
    )
    report["prefer_last_epoch_on_known_f1_tie"] = bool(
        args.prefer_last_epoch_on_known_f1_tie
    )
    if args.encoder_profile == "mal_tls_counterfactual_conflict_gate":
        report["known_validation_counterfactual_gate"] = evaluate_counterfactual_gate(
            model,
            validation_loader,
            device,
            (0, 3),
            args.counterfactual_margin,
        )
    report["evidence_temperature_calibration"] = bool(
        args.evidence_temperature_calibration
    )
    report["evidence_temperature"] = float(evidence_temperature)
    report["known_validation_temperature_nll"] = evidence_temperature_nll
    print("metrics=" + json.dumps(report, ensure_ascii=False, sort_keys=True))

    checkpoint = {
        "model_state": model.state_dict(),
        "input_dims": bundle.input_dims,
        "class_names": bundle.class_names,
        "modality_names": bundle.modality_names,
        "encoder_kinds": encoder_kinds,
        "evidence_adapter_kinds": evidence_adapter_kinds,
        "benign_index": bundle.benign_index,
        "arguments": vars(args),
        "evidence_temperature": float(evidence_temperature),
    }
    torch.save(checkpoint, str(output_dir / "model.pt"))
    json_dump(output_dir / "calibrator.json", calibrator.state_dict())
    json_dump(
        output_dir / "evidence_temperature.json",
        {
            "enabled": bool(args.evidence_temperature_calibration),
            "temperature": float(evidence_temperature),
            "known_validation_nll": evidence_temperature_nll,
            "fit_split": "known_only_validation",
            "unknown_or_test_labels_used": False,
        },
    )
    json_dump(output_dir / "metrics.json", report)
    json_dump(output_dir / "history.json", {"epochs": history})
    json_dump(
        output_dir / "data_metadata.json",
        {
            "class_names": bundle.class_names,
            "modality_names": bundle.modality_names,
            "input_dims": bundle.input_dims,
            "encoder_profile": args.encoder_profile,
            "encoder_kinds": encoder_kinds,
            "evidence_adapter_kinds": evidence_adapter_kinds,
            "evidence_temperature_calibration": bool(
                args.evidence_temperature_calibration
            ),
            "evidence_temperature": float(evidence_temperature),
            "sample_counts": bundle.sample_counts,
            "preprocessing": bundle.preprocessing,
            "split_metadata": bundle.split_metadata,
        },
    )


if __name__ == "__main__":
    main()
