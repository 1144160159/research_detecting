#!/usr/bin/env python3
"""Validate, split, and sample the unified CAEOS experiment reservoir."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

from caeos.unified_data import (
    DataContractError,
    DatasetPolicyRegistry,
    SplitPlan,
    TrainOnlySampler,
    TrainingSamplingPolicy,
    UnifiedDatasetLoader,
    build_experiment_data_manifest,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_SCHEMA = ROOT / "configs" / "unified_multimodal_v4.schema.json"
DEFAULT_FEATURE_VIEWS = ROOT / "configs" / "unified_multimodal_v5.feature_views.json"
DEFAULT_POLICY_REGISTRY = ROOT / "configs" / "unified_data_access_v1.json"


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def add_access_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--feature-views", type=Path, default=DEFAULT_FEATURE_VIEWS)
    parser.add_argument("--policy-registry", type=Path, default=DEFAULT_POLICY_REGISTRY)
    parser.add_argument("--integrity", choices=("manifest", "stat", "sha256"), default="stat")
    parser.add_argument("--row-validation", choices=("labels", "full"), default="labels")
    parser.add_argument(
        "--modality",
        action="append",
        dest="modalities",
        choices=("payload_semantics", "packet_behavior", "packet_interaction_graph"),
    )
    parser.add_argument("--payload-bytes", type=int, default=512)
    parser.add_argument("--packet-count", type=int, default=16)
    parser.add_argument("--include-sanitized-l4-baseline", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Contract-driven CAEOS data admission, OSR splitting, and train-only sampling."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate immutable dataset metadata.")
    add_access_arguments(validate)
    validate.add_argument("--dataset", action="append", dest="datasets")
    validate.add_argument("--report", type=Path)

    split = subparsers.add_parser("split", help="Build a grouped open-set split plan.")
    add_access_arguments(split)
    split.add_argument("--dataset", required=True)
    split.add_argument("--unknown-family", action="append", required=True)
    split.add_argument("--seed", type=int, required=True)
    split.add_argument("--label-column", default="family_label")
    split.add_argument("--train-ratio", type=float, default=0.7)
    split.add_argument("--validation-ratio", type=float, default=0.1)
    split.add_argument("--test-ratio", type=float, default=0.2)
    split.add_argument("--mixed-unknown-action", choices=("reject", "exclude"), default="reject")
    split.add_argument("--split-plan", type=Path, required=True)

    sample = subparsers.add_parser(
        "sample-index", help="Select a deterministic bounded subset of training rows only."
    )
    add_access_arguments(sample)
    sample.add_argument("--dataset", required=True)
    sample.add_argument("--split-plan", type=Path, required=True)
    sample.add_argument("--seed", type=int, required=True)
    sample.add_argument("--label-column", default="family_label")
    sample.add_argument("--default-class-cap", type=int)
    sample.add_argument("--class-cap", action="append", default=[], metavar="LABEL=COUNT")
    sample.add_argument("--max-rows-per-group", type=int)
    sample.add_argument("--group-column", choices=("capture_id", "flow_key_hash"), default="capture_id")
    sample.add_argument("--sample-index", type=Path, required=True)
    sample.add_argument("--sampling-audit", type=Path, required=True)
    sample.add_argument("--experiment-manifest", type=Path, required=True)
    return parser


def open_loader(args: argparse.Namespace, dataset_id: str) -> UnifiedDatasetLoader:
    return UnifiedDatasetLoader.open(
        output_root=args.output_root.resolve(),
        schema_path=args.schema.resolve(),
        feature_views_path=args.feature_views.resolve(),
        policy_registry_path=args.policy_registry.resolve(),
        dataset_id=dataset_id,
        integrity=args.integrity,
        row_validation=args.row_validation,
        modalities=tuple(args.modalities or (
            "payload_semantics",
            "packet_behavior",
            "packet_interaction_graph",
        )),
        payload_bytes=args.payload_bytes,
        packet_count=args.packet_count,
        include_sanitized_l4_baseline=args.include_sanitized_l4_baseline,
    )


def parse_class_caps(items: Iterable[str]) -> dict[str, int]:
    caps: dict[str, int] = {}
    for item in items:
        label, separator, raw_count = item.rpartition("=")
        if not separator or not label:
            raise DataContractError(f"invalid --class-cap value: {item!r}")
        try:
            count = int(raw_count)
        except ValueError as error:
            raise DataContractError(f"invalid --class-cap count: {item!r}") from error
        if label in caps:
            raise DataContractError(f"duplicate --class-cap label: {label}")
        caps[label] = count
    return caps


def command_validate(args: argparse.Namespace) -> int:
    registry = DatasetPolicyRegistry.load(args.policy_registry.resolve())
    dataset_ids = args.datasets or sorted(registry.specs)
    reports: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for dataset_id in dataset_ids:
        try:
            reports.append(open_loader(args, dataset_id).metadata_report())
        except (DataContractError, OSError, json.JSONDecodeError) as error:
            errors.append({"dataset_id": dataset_id, "error": str(error)})
    result = {
        "schema_version": "caeos_unified_data_validation_report_v1",
        "gate_pass": not errors,
        "integrity": args.integrity,
        "validated_dataset_count": len(reports),
        "failed_dataset_count": len(errors),
        "datasets": reports,
        "errors": errors,
    }
    if args.report:
        atomic_json(args.report.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not errors else 2


def command_split(args: argparse.Namespace) -> int:
    loader = open_loader(args, args.dataset)
    split_plan = loader.strategy().build_split_plan(
        unknown_families=args.unknown_family,
        seed=args.seed,
        label_column=args.label_column,
        train_ratio=args.train_ratio,
        validation_ratio=args.validation_ratio,
        test_ratio=args.test_ratio,
        mixed_unknown_action=args.mixed_unknown_action,
    )
    atomic_json(args.split_plan.resolve(), split_plan.to_dict())
    print(json.dumps(split_plan.summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def command_sample_index(args: argparse.Namespace) -> int:
    loader = open_loader(args, args.dataset)
    strategy = loader.strategy()
    split_plan = SplitPlan.load(args.split_plan.resolve())
    policy = TrainingSamplingPolicy(
        seed=args.seed,
        label_column=args.label_column,
        default_class_cap=args.default_class_cap,
        class_caps=parse_class_caps(args.class_cap),
        max_rows_per_group=args.max_rows_per_group,
        group_column=args.group_column,
    )
    sampler = TrainOnlySampler(policy)
    result = sampler.select(strategy.iter_records(split_plan, partitions=("train",)))
    atomic_jsonl(
        args.sample_index.resolve(),
        (
            {
                "dataset_id": record.dataset_id,
                "partition": record.partition,
                "sample_id": record.sample_id,
                "capture_id": record.capture_id,
                "traffic_class": record.row["traffic_class"],
                "attack_category": record.row["attack_category"],
                "attack_subcategory": record.row["attack_subcategory"],
                "fine_label": record.row["fine_label"],
                "family_label": record.row["family_label"],
                "binary_label": record.row["binary_label"],
            }
            for record in result.records
        ),
    )
    atomic_json(args.sampling_audit.resolve(), result.audit)
    experiment_manifest = build_experiment_data_manifest(loader, split_plan, result)
    atomic_json(args.experiment_manifest.resolve(), experiment_manifest)
    print(json.dumps(result.audit, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "validate":
            return command_validate(args)
        if args.command == "split":
            return command_split(args)
        if args.command == "sample-index":
            return command_sample_index(args)
        raise AssertionError(f"unhandled command: {args.command}")
    except (DataContractError, OSError, json.JSONDecodeError) as error:
        print(f"data contract failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
