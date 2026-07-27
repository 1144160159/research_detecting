from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_external_runtime import report


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def identity(value: Dict[str, Any]) -> tuple[str, str, int]:
    return (
        str(value["dataset"]),
        str(value["unknown_attack_family"]),
        int(value["training_seed"]),
    )


def evaluate(
    *,
    capture_dir: Path,
    protocol: Dict[str, Any],
    task: Dict[str, Any],
    output: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_external_malicious_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
        or protocol.get("algorithm") != "krc_csr_caeos_v1"
    ):
        raise ValueError("canonical admitted KRC external protocol required")
    expected = {
        identity(record): record for record in protocol.get("tasks", [])
    }
    task_identity = identity(task)
    if task_identity not in expected or expected[task_identity] != task:
        raise ValueError("external task is not in the frozen protocol")

    capture_path = capture_dir / "capture_manifest.json"
    capture = load(capture_path)
    if (
        capture.get("schema_version")
        != "strict_v4_krc_csr_runtime_capture_v1"
        or capture.get("manifest_sha256") != canonical_hash(capture)
        or capture.get("algorithm") != "krc_csr_caeos_v1"
        or capture.get("task")
        != {
            "suite": task["dataset"],
            "scenario": task["unknown_attack_family"],
        }
        or int(capture.get("training_seed", -1))
        != int(task["training_seed"])
        or float(capture.get("weight", -1.0))
        != float(protocol["krc_policy"]["augmentation_weight"])
        or capture.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
        or capture.get("test_labels_read_for_certificate_or_roundtrip")
        is not False
    ):
        raise ValueError("KRC external capture identity mismatch")

    artifact = capture_dir / capture["runtime_artifact"]
    inputs_path = capture_dir / capture["evaluation_inputs"]
    robust_metrics_path = capture_dir / "robust_run" / "metrics.json"
    if (
        file_hash(artifact) != capture["runtime_artifact_sha256"]
        or file_hash(inputs_path) != capture["evaluation_inputs_sha256"]
    ):
        raise ValueError("KRC external capture artifact SHA mismatch")
    robust_metrics = load(robust_metrics_path)
    split = robust_metrics.get("split_metadata")
    if (
        not isinstance(split, dict)
        or split.get("split_fingerprint") != capture["split_fingerprint"]
        or any(
            int(value) != 0
            for value in split.get("fingerprint_overlap", {}).values()
        )
        or split.get("cross_label_fingerprint_filter", {}).get(
            "unknown_labels_used"
        )
        is not False
    ):
        raise ValueError("KRC external split binding or overlap mismatch")

    runtime = joblib.load(artifact)
    evidence = runtime.evidence()
    certificate = capture["known_only_certificate"]
    if (
        evidence.get("algorithm") != "krc_csr_caeos_v1"
        or int(evidence.get("training_seed", -1))
        != int(task["training_seed"])
        or float(evidence.get("augmentation_weight", -1.0))
        != float(protocol["krc_policy"]["augmentation_weight"])
        or bool(evidence.get("routing_enabled"))
        != bool(certificate["routing_enabled"])
        or evidence.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError("KRC external runtime evidence mismatch")

    with np.load(inputs_path, allow_pickle=False) as inputs:
        views = [
            np.asarray(inputs[f"view_{index}"])
            for index in range(int(evidence["modality_count"]))
        ]
        labels = np.asarray(inputs["test_labels"], dtype=np.int64)
        unknown = np.asarray(inputs["test_unknown"], dtype=bool)
    inference = runtime.predict(views)
    pairwise_prediction = np.asarray(
        inference["clean_probability"]
    ).argmax(axis=1)
    candidate_prediction = np.asarray(inference["prediction"])
    candidate_probability = np.asarray(inference["probability"])
    candidate_risk = np.asarray(inference["risk"])
    pairwise_probability = np.asarray(inference["clean_probability"])
    pairwise_risk = np.asarray(inference["clean_risk"])
    active = np.asarray(inference["active"], dtype=bool)
    inactive = ~active
    enabled = bool(evidence["routing_enabled"])

    routing = {
        "certificate_routing_enabled": enabled,
        "active_count": int(active.sum()),
        "active_rate": float(active.mean()),
        "missing_count": int(
            np.asarray(inference["any_missing"], dtype=bool).sum()
        ),
        "prediction_exactly_pairwise_all_rows": bool(
            np.array_equal(candidate_prediction, pairwise_prediction)
        ),
        "probability_exactly_pairwise_all_rows": bool(
            np.array_equal(candidate_probability, pairwise_probability)
        ),
        "risk_monotone_not_below_pairwise": bool(
            np.all(candidate_risk >= pairwise_risk - 1e-12)
        ),
        "inactive_risk_exactly_pairwise": bool(
            np.array_equal(
                candidate_risk[inactive], pairwise_risk[inactive]
            )
        ),
        "disabled_risk_exactly_pairwise_all_rows": bool(
            enabled or np.array_equal(candidate_risk, pairwise_risk)
        ),
        "unknown_or_test_labels_used": False,
    }
    if not all(
        routing[name]
        for name in (
            "prediction_exactly_pairwise_all_rows",
            "probability_exactly_pairwise_all_rows",
            "risk_monotone_not_below_pairwise",
            "inactive_risk_exactly_pairwise",
            "disabled_risk_exactly_pairwise_all_rows",
        )
    ):
        raise ValueError("KRC external routing contract failed")

    threshold = float(runtime.clean_threshold)
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_external_runtime_metrics_v1",
        "state": "complete",
        "algorithm": "krc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "dataset": task["dataset"],
        "unknown_attack_family": task["unknown_attack_family"],
        "training_seed": int(task["training_seed"]),
        "split_metadata": split,
        "capture": {
            "manifest_file_sha256": file_hash(capture_path),
            "runtime_artifact_sha256": capture[
                "runtime_artifact_sha256"
            ],
            "evaluation_inputs_sha256": capture[
                "evaluation_inputs_sha256"
            ],
            "split_fingerprint": capture["split_fingerprint"],
            "augmentation_weight": float(capture["weight"]),
        },
        "known_only_certificate": {
            "routing_enabled": bool(certificate["routing_enabled"]),
            "calibration_known_macro_f1": float(
                certificate["calibration_known_macro_f1"]
            ),
            "calibration_error_detection_auroc": certificate[
                "calibration_error_detection_auroc"
            ],
            "unknown_or_test_labels_used": False,
        },
        "reports": {
            "candidate": report(
                labels,
                unknown,
                candidate_prediction,
                candidate_risk,
                threshold,
            ),
            "embedded_pairwise": report(
                labels,
                unknown,
                pairwise_prediction,
                pairwise_risk,
                threshold,
            ),
        },
        "routing": routing,
        "diagnostics": {
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing": False,
            "test_labels_used_for_final_metrics_only": True,
            "external_parameters_reselected": False,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--unknown-attack-family", required=True)
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    task = next(
        (
            record
            for record in protocol.get("tasks", [])
            if identity(record)
            == (
                args.dataset,
                args.unknown_attack_family,
                int(args.training_seed),
            )
        ),
        None,
    )
    if task is None:
        raise ValueError("external task is not in the frozen protocol")
    value = evaluate(
        capture_dir=args.capture_dir.resolve(),
        protocol=protocol,
        task=task,
        output=args.output.resolve(),
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
