from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np

from caeos.hybrid_open_set import evaluate_hybrid_open_set
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_mdr_caeos_design import FAMILIES, FIXED_SEVERITY
from evaluate_strict_v4_comparative_corruption import risk_ece


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def selected_modality(
    coverage_manifest_sha256: str,
    suite: str,
    scenario: str,
    family: str,
    modality_count: int,
) -> int:
    digest = hashlib.sha256(
        (
            f"{coverage_manifest_sha256}:{suite}:{scenario}:{family}"
        ).encode("utf-8")
    ).hexdigest()
    return int(digest, 16) % int(modality_count)


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


def evaluate(
    capture_dir: Path,
    design: Dict[str, Any],
    *,
    suite: str,
    scenario: str,
    condition: str,
    output: Path,
) -> Dict[str, Any]:
    if (
        design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("MDR execution requires the canonical v2 design")
    if condition not in ("clean", *FAMILIES):
        raise ValueError("unsupported MDR pilot condition")
    capture_manifest_path = capture_dir / "capture_manifest.json"
    capture = load(capture_manifest_path)
    if capture.get("schema_version") != "strict_v4_mdr_caeos_runtime_capture_v1":
        raise ValueError("invalid MDR runtime capture")
    artifact = capture_dir / capture["runtime_artifact"]
    inputs_path = capture_dir / capture["evaluation_inputs"]
    if (
        file_hash(artifact) != capture["runtime_artifact_sha256"]
        or file_hash(inputs_path) != capture["evaluation_inputs_sha256"]
    ):
        raise ValueError("MDR capture artifact hash mismatch")
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
            design["input_manifest_sha256"]["coverage"],
            suite,
            scenario,
            condition,
            len(views),
        )
        severity = float(FIXED_SEVERITY[condition])
        corrupted = runtime.corrupt(
            views,
            family=condition,
            modality=modality,
            severity=severity,
            seed=int(design["pilot"]["corruption_seed"]),
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
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_pilot_evaluation_v1",
        "state": "complete",
        "algorithm": "mdr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "suite": suite,
        "scenario": scenario,
        "training_seed": int(design["pilot"]["training_seed"]),
        "condition": condition,
        "corruption": {
            "family": condition,
            "modality": modality,
            "severity": severity,
            "seed": int(design["pilot"]["corruption_seed"]),
            "selection_uses_effect_metrics": False,
        },
        "capture": {
            "manifest_file_sha256": file_hash(capture_manifest_path),
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
                    inference["prediction"][~inference["active"]],
                    inference["clean_prediction"][~inference["active"]],
                )
            ),
            "inactive_risk_exactly_pairwise": bool(
                np.array_equal(
                    inference["risk"][~inference["active"]],
                    inference["clean_risk"][~inference["active"]],
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
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--condition", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = evaluate(
        args.capture_dir,
        load(args.design),
        suite=args.suite,
        scenario=args.scenario,
        condition=args.condition,
        output=args.output,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
