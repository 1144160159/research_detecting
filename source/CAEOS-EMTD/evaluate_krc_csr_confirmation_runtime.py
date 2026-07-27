from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from capture_pairwise_runtime import file_hash
from certify_krc_csr import load
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_caeos_runtime import report, selected_modality


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
        != "strict_v4_krc_csr_confirmation_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("execution_admitted") is not True
    ):
        raise ValueError("canonical admitted KRC confirmation protocol required")
    expected = {
        (
            task["suite"],
            task["scenario"],
            int(task["training_seed"]),
            int(task["corruption_seed"]),
        ): task
        for task in protocol["confirmation"]["tasks"]
    }
    identity = (suite, scenario, int(training_seed), int(corruption_seed))
    if identity not in expected:
        raise ValueError("KRC confirmation task is outside frozen universe")
    if condition not in protocol["confirmation"]["conditions"]:
        raise ValueError("unsupported KRC confirmation condition")
    manifest_path = capture_dir / "capture_manifest.json"
    capture = load(manifest_path)
    if (
        capture.get("schema_version")
        != "strict_v4_krc_csr_runtime_capture_v1"
        or capture.get("manifest_sha256") != canonical_hash(capture)
        or capture.get("task") != {"suite": suite, "scenario": scenario}
        or int(capture.get("training_seed", -1)) != int(training_seed)
        or capture.get(
            "unknown_or_test_labels_used_for_training_selection_or_calibration"
        )
        is not False
    ):
        raise ValueError("invalid KRC confirmation capture")
    artifact = capture_dir / capture["runtime_artifact"]
    inputs_path = capture_dir / capture["evaluation_inputs"]
    if (
        file_hash(artifact) != capture["runtime_artifact_sha256"]
        or file_hash(inputs_path) != capture["evaluation_inputs_sha256"]
    ):
        raise ValueError("KRC confirmation artifact hash mismatch")
    runtime = joblib.load(artifact)
    evidence = runtime.evidence()
    with np.load(inputs_path, allow_pickle=False) as inputs:
        views = [
            np.asarray(inputs[f"view_{index}"])
            for index in range(evidence["modality_count"])
        ]
        labels = np.asarray(inputs["test_labels"], dtype=np.int64)
        unknown = np.asarray(inputs["test_unknown"], dtype=bool)
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
    pairwise_prediction = inference["clean_probability"].argmax(axis=1)
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
        pairwise_prediction,
        inference["clean_risk"],
        threshold,
    )
    inactive = ~np.asarray(inference["active"], dtype=bool)
    enabled = bool(evidence["routing_enabled"])
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_confirmation_evaluation_v1",
        "state": "complete",
        "algorithm": "krc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": suite,
        "scenario": scenario,
        "training_seed": int(training_seed),
        "corruption_seed": int(corruption_seed),
        "primary_heldout_scenario": bool(
            expected[identity]["primary_heldout_scenario"]
        ),
        "condition": condition,
        "certificate_routing_enabled": enabled,
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
            "evaluation_inputs_sha256": capture[
                "evaluation_inputs_sha256"
            ],
            "weight": float(capture["weight"]),
        },
        "routing": {
            "active_count": int(inference["active"].sum()),
            "active_rate": float(inference["active"].mean()),
            "missing_count": int(inference["any_missing"].sum()),
            "missing_rate": float(inference["any_missing"].mean()),
            "prediction_exactly_pairwise_all_rows": bool(
                np.array_equal(
                    inference["prediction"], pairwise_prediction
                )
            ),
            "probability_exactly_pairwise_all_rows": bool(
                np.array_equal(
                    inference["probability"],
                    inference["clean_probability"],
                )
            ),
            "risk_monotone_not_below_pairwise": bool(
                np.all(
                    inference["risk"]
                    >= inference["clean_risk"] - 1e-12
                )
            ),
            "inactive_risk_exactly_pairwise": bool(
                np.array_equal(
                    inference["risk"][inactive],
                    inference["clean_risk"][inactive],
                )
            ),
            "disabled_risk_exactly_pairwise_all_rows": bool(
                enabled
                or np.array_equal(
                    inference["risk"], inference["clean_risk"]
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
        args.capture_dir.resolve(),
        suite=args.suite,
        scenario=args.scenario,
        training_seed=args.training_seed,
        corruption_seed=args.corruption_seed,
        condition=args.condition,
        output=args.output.resolve(),
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
