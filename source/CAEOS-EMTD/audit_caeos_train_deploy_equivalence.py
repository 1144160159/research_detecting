from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from caeos_paper_views import (
    deployment_json_to_views,
    exact_view_bytes,
    training_row_to_views,
)


VIEW_COLUMNS = (
    "payload_b64",
    "packet_count_stored",
    "packet_length_seq",
    "packet_iat_us_seq",
    "direction_seq",
    "packet_protocol_seq",
    "tcp_flags_seq",
    "packet_payload_length_seq",
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def build_report(manifest: dict[str, Any], samples_per_class: int) -> dict[str, Any]:
    if not manifest.get("complete"):
        raise ValueError("dataset manifest is not complete")
    if samples_per_class < 1:
        raise ValueError("samples per class must be positive")
    sample_digests: list[dict[str, str]] = []
    for item in manifest["class_csvs"]:
        path = Path(item["path"])
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None or not set(VIEW_COLUMNS).issubset(reader.fieldnames):
                raise ValueError(f"view columns missing from {path}")
            for index, row in enumerate(reader):
                if index >= samples_per_class:
                    break
                input_row = {name: row[name] for name in VIEW_COLUMNS}
                serialized = json.dumps(
                    input_row, sort_keys=True, separators=(",", ":")
                ).encode("utf-8")
                training = exact_view_bytes(training_row_to_views(input_row))
                deployment = exact_view_bytes(deployment_json_to_views(serialized))
                if training != deployment:
                    raise ValueError("train and deployment materialization differ")
                sample_digests.append(
                    {
                        "attack_category": item["attack_category"],
                        "input_sha256": hashlib.sha256(serialized).hexdigest(),
                        "view_sha256": hashlib.sha256(training).hexdigest(),
                    }
                )
    expected = len(manifest["class_csvs"]) * samples_per_class
    gate_pass = len(sample_digests) == expected
    return {
        "schema_version": "caeos_train_deploy_equivalence_v1",
        "dataset_id": manifest["dataset_id"],
        "dataset_manifest_sha256": manifest["manifest_sha256"],
        "samples_per_class": samples_per_class,
        "sample_count": len(sample_digests),
        "comparison": "exact_serialized_view_bytes",
        "payload_tokens": 512,
        "packet_count": 16,
        "samples": sample_digests,
        "gate_pass": gate_pass,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--samples-per-class", type=int, default=8)
    args = parser.parse_args()
    report = build_report(load_json(args.dataset_manifest), args.samples_per_class)
    atomic_json(args.output, report)
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
