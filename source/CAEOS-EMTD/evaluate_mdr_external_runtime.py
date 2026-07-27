from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_strict_v4_comparative_corruption import risk_ece


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def report(
    labels: np.ndarray,
    unknown: np.ndarray,
    prediction: np.ndarray,
    risk: np.ndarray,
    threshold: float,
) -> Dict[str, float]:
    value = evaluate_hybrid_open_set(
        labels, unknown, prediction, risk, threshold
    )
    value["ece"] = risk_ece(np.asarray(risk), np.asarray(unknown))
    return {name: float(number) for name, number in value.items()}


def scenario_identity(value: Dict[str, Any]) -> tuple[str, str, int]:
    return (
        str(value["dataset"]),
        str(value["unknown_attack_family"]),
        int(value["seed"]),
    )


def evaluate(
    *,
    capture_dir: Path,
    protocol: Dict[str, Any],
    scenario: Dict[str, Any],
    output: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_external_malicious_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("selected_algorithm") != "mdr_caeos_v1"
    ):
        raise ValueError("canonical MDR external protocol required")
    expected = {
        scenario_identity(item) for item in protocol.get("scenarios", [])
    }
    identity = scenario_identity(scenario)
    if identity not in expected:
        raise ValueError("external scenario is not in the protocol")
    capture_path = capture_dir / "capture_manifest.json"
    capture = load(capture_path)
    if (
        capture.get("schema_version")
        != "strict_v4_mdr_caeos_runtime_capture_v1"
        or capture.get("algorithm") != "mdr_caeos_v1"
        or capture.get("task", {}).get("suite") != scenario["dataset"]
        or capture.get("task", {}).get("scenario")
        != scenario["unknown_attack_family"]
        or int(capture.get("training_seed", -1)) != int(scenario["seed"])
        or float(capture.get("weight", -1.0))
        != float(protocol["mdr_policy"]["augmentation_weight"])
    ):
        raise ValueError("MDR external capture identity mismatch")
    artifact = capture_dir / capture["runtime_artifact"]
    inputs_path = capture_dir / capture["evaluation_inputs"]
    robust_metrics_path = capture_dir / "robust_run" / "metrics.json"
    if (
        file_hash(artifact) != capture["runtime_artifact_sha256"]
        or file_hash(inputs_path) != capture["evaluation_inputs_sha256"]
    ):
        raise ValueError("MDR external capture artifact SHA mismatch")
    robust_metrics = load(robust_metrics_path)
    split = robust_metrics.get("split_metadata")
    if (
        not isinstance(split, dict)
        or split.get("split_fingerprint") != capture["split_fingerprint"]
    ):
        raise ValueError("MDR external split binding mismatch")
    runtime = joblib.load(artifact)
    evidence = runtime.evidence()
    if (
        evidence.get("algorithm") != "mdr_caeos_v1"
        or float(evidence.get("augmentation_weight", -1.0))
        != float(protocol["mdr_policy"]["augmentation_weight"])
        or int(evidence.get("training_seed", -1)) != int(scenario["seed"])
        or evidence.get(
            "unknown_or_test_labels_used_for_runtime_fitting_or_selection"
        )
        is not False
    ):
        raise ValueError("MDR external runtime evidence mismatch")
    inputs = np.load(inputs_path, allow_pickle=False)
    views = [
        np.asarray(inputs[f"view_{index}"])
        for index in range(int(evidence["modality_count"]))
    ]
    labels = np.asarray(inputs["test_labels"], dtype=np.int64)
    unknown = np.asarray(inputs["test_unknown"], dtype=bool)
    inference = runtime.predict(views)
    threshold = float(runtime.clean_threshold)
    candidate = report(
        labels,
        unknown,
        np.asarray(inference["prediction"]),
        np.asarray(inference["risk"]),
        threshold,
    )
    pairwise = report(
        labels,
        unknown,
        np.asarray(inference["clean_prediction"]),
        np.asarray(inference["clean_risk"]),
        threshold,
    )
    active = np.asarray(inference["active"], dtype=bool)
    inactive_prediction = bool(
        np.array_equal(
            np.asarray(inference["prediction"])[~active],
            np.asarray(inference["clean_prediction"])[~active],
        )
    )
    inactive_risk = bool(
        np.array_equal(
            np.asarray(inference["risk"])[~active],
            np.asarray(inference["clean_risk"])[~active],
        )
    )
    inactive_probability = bool(
        np.array_equal(
            np.asarray(inference["probability"])[~active],
            np.asarray(inference["clean_probability"])[~active],
        )
    )
    if not (
        inactive_prediction and inactive_risk and inactive_probability
    ):
        raise ValueError("MDR external inactive path differs from Pairwise")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_external_runtime_metrics_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "selected_algorithm": "mdr_caeos_v1",
        "dataset": scenario["dataset"],
        "unknown_attack_family": scenario["unknown_attack_family"],
        "seed": int(scenario["seed"]),
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
        "reports": {"candidate": candidate, "embedded_pairwise": pairwise},
        "routing": {
            "active_count": int(active.sum()),
            "active_rate": float(active.mean()),
            "inactive_prediction_exactly_pairwise": inactive_prediction,
            "inactive_risk_exactly_pairwise": inactive_risk,
            "inactive_probability_exactly_pairwise": inactive_probability,
        },
        "diagnostics": {
            "unknown_or_test_labels_used_for_fit_selection_calibration_"
            "threshold_or_routing": False,
            "test_labels_used_for_final_metrics_only": True,
            "external_weight_reselected": False,
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
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = load(args.protocol)
    scenario = {
        "dataset": args.dataset,
        "unknown_attack_family": args.unknown_attack_family,
        "seed": args.seed,
    }
    value = evaluate(
        capture_dir=args.capture_dir,
        protocol=protocol,
        scenario=scenario,
        output=args.output,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
