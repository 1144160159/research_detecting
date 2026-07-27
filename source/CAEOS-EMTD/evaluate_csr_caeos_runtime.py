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
from create_strict_v4_mdr_caeos_design import FAMILIES, FIXED_SEVERITY
from evaluate_mdr_caeos_runtime import selected_modality
from evaluate_strict_v4_comparative_corruption import risk_ece


def load_json(path: Path) -> Dict[str, Any]:
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
        design.get("schema_version")
        not in {
            "strict_v4_csr_caeos_design_v2",
            "strict_v4_csr_caeos_design_v3",
            "strict_v4_csr_caeos_design_v4",
        }
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("CSR execution requires a canonical design")
    if condition not in ("clean", *FAMILIES):
        raise ValueError("unsupported CSR pilot condition")
    capture_path = capture_dir / "capture_manifest.json"
    capture = load_json(capture_path)
    if (
        capture.get("schema_version")
        != "strict_v4_csr_caeos_runtime_capture_v1"
        or capture.get("algorithm") != "csr_caeos_v1"
        or capture.get("test_effect_metrics_computed") is not False
    ):
        raise ValueError("valid zero-effect CSR runtime capture required")
    artifact = capture_dir / capture["runtime_artifact"]
    inputs_path = capture_dir / capture["evaluation_inputs"]
    if (
        file_hash(artifact) != capture["runtime_artifact_sha256"]
        or file_hash(inputs_path) != capture["evaluation_inputs_sha256"]
    ):
        raise ValueError("CSR capture artifact hash mismatch")
    runtime = joblib.load(artifact)
    runtime_evidence = runtime.evidence()
    if (
        runtime_evidence.get("algorithm") != "csr_caeos_v1"
        or runtime_evidence.get("contains_test_ground_truth") is not False
    ):
        raise ValueError("invalid CSR runtime identity")
    with np.load(inputs_path, allow_pickle=False) as inputs:
        views = [
            np.asarray(inputs[f"view_{index}"])
            for index in range(runtime_evidence["modality_count"])
        ]
        labels = np.asarray(inputs["test_labels"], dtype=np.int64)
        unknown = np.asarray(inputs["test_unknown"], dtype=bool)
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
            seed=int(design["development"]["corruption_seed"]),
        )
    inference = runtime.predict(corrupted)
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
        inference["clean_probability"].argmax(axis=1),
        inference["clean_risk"],
        threshold,
    )
    inactive = ~np.asarray(inference["active"], dtype=bool)
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_csr_caeos_pilot_evaluation_v1",
        "state": "complete",
        "algorithm": "csr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "suite": suite,
        "scenario": scenario,
        "training_seed": int(design["development"]["training_seed"]),
        "condition": condition,
        "corruption": {
            "family": condition,
            "modality": modality,
            "severity": severity,
            "seed": int(design["development"]["corruption_seed"]),
            "selection_uses_effect_metrics": False,
        },
        "capture": {
            "manifest_file_sha256": file_hash(capture_path),
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
                    inference["prediction"],
                    inference["clean_probability"].argmax(axis=1),
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
        load_json(args.design),
        suite=args.suite,
        scenario=args.scenario,
        condition=args.condition,
        output=args.output,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
