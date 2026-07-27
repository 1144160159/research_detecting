from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict

import joblib

from caeos.csr_exact_replay_runtime import CSRExactReplayRuntime
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from run_strict_v4_csr_caeos_pilot import validate_capture


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validate_protocol(protocol: Dict[str, Any]) -> None:
    if (
        protocol.get("schema_version")
        != "strict_v4_csr_caeos_exact_replay_protocol_v2"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("status") != "frozen_before_repair_outputs"
    ):
        raise ValueError("canonical frozen CSR exact-replay protocol required")


def materialize(
    protocol: Dict[str, Any],
    source_dir: Path,
    output_dir: Path,
    *,
    suite: str,
    scenario: str,
    materializer_file_sha256: str,
    wrapper_file_sha256: str,
) -> Dict[str, Any]:
    validate_protocol(protocol)
    source_manifest_path = source_dir / "capture_manifest.json"
    source_manifest = load(source_manifest_path)
    validate_capture(source_manifest_path, suite, scenario, 0.5)
    identity = f"{suite}/{scenario}"
    expected_source_sha = protocol["source_capture_manifest_file_sha256"].get(
        identity
    )
    if expected_source_sha != file_hash(source_manifest_path):
        raise ValueError("source CSR capture differs from frozen protocol")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("exact-replay output directory must be empty")
    output_dir.mkdir(parents=True, exist_ok=True)

    source_artifact = source_dir / source_manifest["runtime_artifact"]
    source_inputs = source_dir / source_manifest["evaluation_inputs"]
    if (
        file_hash(source_artifact)
        != source_manifest["runtime_artifact_sha256"]
        or file_hash(source_inputs)
        != source_manifest["evaluation_inputs_sha256"]
    ):
        raise ValueError("source CSR capture artifact hash mismatch")
    base_runtime = joblib.load(source_artifact)
    if base_runtime.evidence().get("algorithm") != "csr_caeos_v1":
        raise ValueError("source CSR runtime identity mismatch")
    repaired_runtime = CSRExactReplayRuntime(base_runtime)
    repaired_artifact = output_dir / "csr_exact_replay_runtime.joblib"
    repaired_inputs = output_dir / "evaluation_inputs.npz"
    joblib.dump(repaired_runtime, repaired_artifact, compress=3)
    shutil.copy2(source_inputs, repaired_inputs)

    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_exact_replay_capture_v2",
        "state": "complete",
        "algorithm": "csr_caeos_v1",
        "runtime_revision": "exact_clean_probability_replay_v2",
        "suite": suite,
        "scenario": scenario,
        "weight": 0.5,
        "repair_protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": protocol["design_manifest_sha256"],
        "clean_admission_manifest_sha256": protocol[
            "clean_admission_manifest_sha256"
        ],
        "source_integrity_rejection_manifest_sha256": protocol[
            "source_integrity_rejection_manifest_sha256"
        ],
        "source_capture_manifest": str(source_manifest_path),
        "source_capture_manifest_file_sha256": file_hash(
            source_manifest_path
        ),
        "source_runtime_artifact_sha256": file_hash(source_artifact),
        "source_evaluation_inputs_sha256": file_hash(source_inputs),
        "runtime_artifact": repaired_artifact.name,
        "runtime_artifact_sha256": file_hash(repaired_artifact),
        "evaluation_inputs": repaired_inputs.name,
        "evaluation_inputs_sha256": file_hash(repaired_inputs),
        "materializer_file_sha256": materializer_file_sha256,
        "wrapper_file_sha256": wrapper_file_sha256,
        "technical_change": {
            "prediction": "clean_probability_argmax_from_same_forward",
            "probability": "clean_probability_copy_from_same_forward",
            "risk": "unchanged_from_source_runtime",
            "active_mask": "unchanged_from_source_runtime",
            "threshold": "unchanged_from_source_runtime",
            "training": "not_repeated",
        },
        "effect_metric_fields_read": [],
        "test_labels_read_for_repair": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    manifest_path = output_dir / "repair_capture_manifest.json"
    manifest_path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--wrapper", type=Path, required=True)
    args = parser.parse_args()
    value = materialize(
        load(args.protocol),
        args.source_dir.resolve(),
        args.output_dir.resolve(),
        suite=args.suite,
        scenario=args.scenario,
        materializer_file_sha256=file_hash(Path(__file__).resolve()),
        wrapper_file_sha256=file_hash(args.wrapper.resolve()),
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
