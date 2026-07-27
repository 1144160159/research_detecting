from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from caeos.csr_runtime import CSRRuntime
from caeos.rrc_csr_runtime import RRCCSRRuntime
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def materialize(
    protocol: Dict[str, Any],
    certificate: Dict[str, Any],
    source_capture_dir: Path,
    output_dir: Path,
    *,
    suite: str,
    scenario: str,
    training_seed: int,
    corruption_seed: int,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_rrc_csr_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
    ):
        raise ValueError("canonical admitted RRC execution protocol required")
    expected = {
        (
            task["suite"],
            task["scenario"],
            int(task["training_seed"]),
            int(task["corruption_seed"]),
        ): task
        for task in protocol["tasks"]
    }
    identity = (suite, scenario, int(training_seed), int(corruption_seed))
    if identity not in expected:
        raise ValueError("RRC materialization task is outside frozen universe")
    if (
        certificate.get("schema_version")
        != "strict_v4_rrc_csr_scenario_certificate_v1"
        or certificate.get("manifest_sha256") != canonical_hash(certificate)
        or certificate.get("protocol_manifest_sha256")
        != protocol["manifest_sha256"]
        or certificate.get("suite") != suite
        or certificate.get("scenario") != scenario
        or certificate.get("unknown_or_test_labels_used") is not False
        or certificate.get("test_arrays_read") is not False
        or certificate.get("test_effect_metrics_read") is not False
    ):
        raise ValueError("canonical known-only RRC scenario certificate required")
    seed_records = {
        int(row["training_seed"]): row
        for row in certificate["seed_records"]
    }
    if set(seed_records) != set(certificate["training_seeds"]):
        raise ValueError("scenario certificate seed registry mismatch")
    seed_record = seed_records.get(int(training_seed))
    if seed_record is None:
        raise ValueError("training seed is not certified")

    source_manifest_path = source_capture_dir / "capture_manifest.json"
    source = load_json(source_manifest_path)
    source_artifact = source_capture_dir / source["runtime_artifact"]
    source_inputs = source_capture_dir / source["evaluation_inputs"]
    if (
        source.get("schema_version")
        != "strict_v4_csr_caeos_runtime_capture_v1"
        or source.get("state") != "complete"
        or source.get("algorithm") != "csr_caeos_v1"
        or source.get("task") != {"suite": suite, "scenario": scenario}
        or int(source.get("training_seed", -1)) != int(training_seed)
        or file_hash(source_manifest_path)
        != seed_record["source_capture_manifest_file_sha256"]
        or file_hash(source_artifact) != source["runtime_artifact_sha256"]
        or file_hash(source_inputs) != source["evaluation_inputs_sha256"]
        or source.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
        or source.get("test_labels_read_for_roundtrip_or_selection") is not False
        or source.get("test_effect_metrics_computed") is not False
    ):
        raise ValueError("complete certificate-bound CSR source capture required")

    base_runtime = joblib.load(source_artifact)
    if not isinstance(base_runtime, CSRRuntime):
        raise TypeError("source artifact is not CSRRuntime")
    aggregation = certificate["scenario_aggregation"]
    thresholds = certificate["thresholds"]
    runtime = RRCCSRRuntime(
        base_runtime=base_runtime,
        routing_enabled=bool(certificate["routing_enabled"]),
        scenario_identity=f"{suite}/{scenario}",
        scenario_certificate_manifest_sha256=certificate["manifest_sha256"],
        training_seed=int(training_seed),
        certified_training_seeds=tuple(certificate["training_seeds"]),
        seed_error_detection_auroc=float(
            seed_record["calibration_error_detection_auroc"]
        ),
        seed_safety_active_rate_upper_95pct=float(
            seed_record["safety_active_rate_upper_95pct"]
        ),
        scenario_mean_error_detection_auroc=float(
            aggregation["mean_calibration_error_detection_auroc"]
        ),
        scenario_minimum_error_detection_auroc=float(
            aggregation["minimum_calibration_error_detection_auroc"]
        ),
        all_seed_safety_checks_pass=bool(
            aggregation["all_seed_safety_checks_pass"]
        ),
        scenario_mean_auroc_minimum=float(
            thresholds["scenario_mean_error_detection_auroc_minimum"]
        ),
        per_seed_auroc_minimum=float(
            thresholds["per_seed_error_detection_auroc_minimum"]
        ),
        safety_active_rate_upper_maximum=float(
            thresholds[
                "per_seed_safety_active_rate_upper_95pct_maximum"
            ]
        ),
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / "rrc_csr_runtime.joblib"
    inputs_path = output_dir / "evaluation_inputs.npz"
    joblib.dump(runtime, artifact_path, compress=3)
    shutil.copyfile(source_inputs, inputs_path)
    loaded = joblib.load(artifact_path)
    evidence = runtime.evidence()
    with np.load(inputs_path, allow_pickle=False) as archive:
        views = [
            np.asarray(archive[f"view_{index}"])[:32]
            for index in range(int(evidence["modality_count"]))
        ]
    before = runtime.predict(views)
    after = loaded.predict(views)
    roundtrip = {
        "prediction_array_equal": bool(
            np.array_equal(before["prediction"], after["prediction"])
        ),
        "probability_max_absolute_difference": float(
            np.max(np.abs(before["probability"] - after["probability"]))
        ),
        "risk_max_absolute_difference": float(
            np.max(np.abs(before["risk"] - after["risk"]))
        ),
        "active_array_equal": bool(
            np.array_equal(before["active"], after["active"])
        ),
    }
    roundtrip["passes"] = bool(
        roundtrip["prediction_array_equal"]
        and roundtrip["probability_max_absolute_difference"] == 0.0
        and roundtrip["risk_max_absolute_difference"] == 0.0
        and roundtrip["active_array_equal"]
    )
    if not roundtrip["passes"]:
        raise ValueError("RRC runtime serialization roundtrip failed")

    value: Dict[str, Any] = {
        "schema_version": "strict_v4_rrc_csr_runtime_capture_v1",
        "state": "complete",
        "algorithm": "rrc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "scenario_certificate_manifest_sha256": certificate[
            "manifest_sha256"
        ],
        "task": {"suite": suite, "scenario": scenario},
        "training_seed": int(training_seed),
        "corruption_seed": int(corruption_seed),
        "weight": float(source["weight"]),
        "routing_enabled": bool(certificate["routing_enabled"]),
        "source_csr_capture_manifest_file_sha256": file_hash(
            source_manifest_path
        ),
        "source_csr_runtime_artifact_sha256": source[
            "runtime_artifact_sha256"
        ],
        "runtime_artifact": artifact_path.name,
        "runtime_artifact_sha256": file_hash(artifact_path),
        "runtime_artifact_bytes": artifact_path.stat().st_size,
        "evaluation_inputs": inputs_path.name,
        "evaluation_inputs_sha256": file_hash(inputs_path),
        "runtime_evidence": loaded.evidence(),
        "roundtrip": roundtrip,
        "unknown_or_test_labels_used_for_training_selection_or_calibration": (
            False
        ),
        "test_features_read_for_serialization_roundtrip_only": True,
        "test_labels_read_for_materialization_or_roundtrip": False,
        "test_effect_metrics_computed": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    manifest_path = output_dir / "capture_manifest.json"
    manifest_path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--source-capture-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--corruption-seed", type=int, required=True)
    args = parser.parse_args()
    value = materialize(
        load_json(args.protocol),
        load_json(args.certificate),
        args.source_capture_dir.resolve(),
        args.output_dir.resolve(),
        suite=args.suite,
        scenario=args.scenario,
        training_seed=args.training_seed,
        corruption_seed=args.corruption_seed,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
