from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_caeos_runtime import report, selected_modality
from select_mdr_caeos_weight import load


def evaluate(
    protocol: Dict[str, Any],
    capture_dir: Path,
    *,
    suite: str,
    scenario: str,
    training_seed: int,
    corruption_seed: int,
    condition: str,
    output: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_caeos_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
    ):
        raise ValueError("canonical admitted MDR confirmation protocol required")
    conditions = protocol["confirmation"]["conditions"]
    if condition not in conditions:
        raise ValueError("unsupported MDR confirmation condition")
    task = (suite, scenario, int(training_seed), int(corruption_seed))
    expected = {
        (
            record["suite"],
            record["scenario"],
            int(record["training_seed"]),
            int(record["corruption_seed"]),
        )
        for record in protocol["confirmation"]["tasks"]
    }
    if task not in expected:
        raise ValueError("MDR confirmation task is outside the frozen universe")

    manifest_path = capture_dir / "capture_manifest.json"
    capture = load(manifest_path)
    if (
        capture.get("schema_version")
        != "strict_v4_mdr_caeos_runtime_capture_v1"
        or capture.get("state") != "complete"
        or capture.get("task")
        != {"suite": suite, "scenario": scenario}
        or int(capture.get("training_seed", -1)) != int(training_seed)
        or float(capture.get("weight", -1.0))
        != float(protocol["selected_augmentation_weight"])
        or capture.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
    ):
        raise ValueError("invalid MDR confirmation capture")
    artifact = capture_dir / capture["runtime_artifact"]
    inputs_path = capture_dir / capture["evaluation_inputs"]
    if (
        file_hash(artifact) != capture["runtime_artifact_sha256"]
        or file_hash(inputs_path) != capture["evaluation_inputs_sha256"]
    ):
        raise ValueError("MDR confirmation capture artifact hash mismatch")
    runtime = joblib.load(artifact)
    inputs = np.load(inputs_path, allow_pickle=False)
    views = [
        np.asarray(inputs[f"view_{index}"])
        for index in range(runtime.evidence()["modality_count"])
    ]
    if condition == "clean":
        modality = None
        severity = 0.0
        corrupted = views
    else:
        modality = selected_modality(
            protocol["coverage_manifest_sha256"],
            suite,
            scenario,
            condition,
            len(views),
        )
        severity = float(
            protocol["confirmation"]["fixed_severity"][condition]
        )
        corrupted = runtime.corrupt(
            views,
            family=condition,
            modality=modality,
            severity=severity,
            seed=int(corruption_seed),
        )
    inference = runtime.predict(corrupted)
    labels = np.asarray(inputs["test_labels"], dtype=np.int64)
    unknown = np.asarray(inputs["test_unknown"], dtype=bool)
    threshold = float(runtime.clean_threshold)
    candidate_report = report(
        labels,
        unknown,
        inference["prediction"],
        inference["risk"],
        threshold,
    )
    pairwise_report = report(
        labels,
        unknown,
        inference["clean_prediction"],
        inference["clean_risk"],
        threshold,
    )
    inactive = ~np.asarray(inference["active"], dtype=bool)
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_caeos_confirmation_evaluation_v1"
        ),
        "state": "complete",
        "algorithm": "mdr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": suite,
        "scenario": scenario,
        "training_seed": int(training_seed),
        "corruption_seed": int(corruption_seed),
        "condition": condition,
        "corruption": {
            "family": condition,
            "modality": modality,
            "severity": severity,
            "seed": int(corruption_seed),
            "selection_uses_effect_metrics": False,
        },
        "capture": {
            "manifest_file_sha256": file_hash(manifest_path),
            "runtime_artifact_sha256": capture["runtime_artifact_sha256"],
            "evaluation_inputs_sha256": capture["evaluation_inputs_sha256"],
            "weight": float(capture["weight"]),
        },
        "routing": {
            "active_count": int(inference["active"].sum()),
            "active_rate": float(inference["active"].mean()),
            "missing_count": int(inference["any_missing"].sum()),
            "missing_rate": float(inference["any_missing"].mean()),
            "inactive_prediction_exactly_pairwise": bool(
                np.array_equal(
                    inference["prediction"][inactive],
                    inference["clean_prediction"][inactive],
                )
            ),
            "inactive_risk_exactly_pairwise": bool(
                np.array_equal(
                    inference["risk"][inactive],
                    inference["clean_risk"][inactive],
                )
            ),
            "inactive_probability_exactly_pairwise": bool(
                np.array_equal(
                    inference["probability"][inactive],
                    inference["clean_probability"][inactive],
                )
            ),
            "unknown_or_test_labels_used": False,
        },
        "pairwise_report": pairwise_report,
        "candidate_report": candidate_report,
        "test_labels_used_for_final_evaluation_only": True,
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
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--corruption-seed", type=int, required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = evaluate(
        load(args.protocol),
        args.capture_dir,
        suite=args.suite,
        scenario=args.scenario,
        training_seed=args.training_seed,
        corruption_seed=args.corruption_seed,
        condition=args.condition,
        output=args.output,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
