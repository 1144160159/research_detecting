from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import numpy as np
from sklearn.metrics import f1_score, roc_auc_score

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def validation_arrays(capture_dir: Path) -> tuple[np.ndarray, ...]:
    evidence_path = capture_dir / "clean_run" / "evidence_package.npz"
    scores_path = capture_dir / "robust_run" / "scores.npz"
    with np.load(evidence_path, allow_pickle=False) as archive:
        probability = np.asarray(
            archive["validation_final_probability"], dtype=np.float64
        )
        risk = np.asarray(
            archive["validation_selected_risk"], dtype=np.float64
        )
    with np.load(scores_path, allow_pickle=False) as archive:
        labels = np.asarray(archive["validation_labels"], dtype=np.int64)
    return probability, risk, labels


def certify(
    protocol: Dict[str, Any],
    capture_dir: Path,
    *,
    suite: str,
    scenario: str,
) -> Dict[str, Any]:
    capture_path = capture_dir / "capture_manifest.json"
    capture = load(capture_path)
    identity = f"{suite}/{scenario}"
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_csr_development_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or capture.get("schema_version")
        != "strict_v4_csr_caeos_runtime_capture_v1"
        or capture.get("task", {}).get("suite") != suite
        or capture.get("task", {}).get("scenario") != scenario
        or file_hash(capture_path)
        != protocol["source_capture_manifest_file_sha256"].get(identity)
    ):
        raise ValueError("protocol-bound source capture required")
    probability, risk, labels = validation_arrays(capture_dir)
    if not (len(probability) == len(risk) == len(labels)):
        raise ValueError("known-validation arrays are not aligned")
    selected = np.arange(len(labels), dtype=np.int64)[::2]
    prediction = probability[selected].argmax(axis=1)
    errors = prediction != labels[selected]
    macro_f1 = float(
        f1_score(
            labels[selected],
            prediction,
            average="macro",
            zero_division=0,
        )
    )
    error_auroc = (
        float(roc_auc_score(errors.astype(np.int64), risk[selected]))
        if len(np.unique(errors)) == 2
        else None
    )
    gate = protocol["known_only_certificate"]
    enabled = bool(
        macro_f1 >= float(gate["calibration_known_macro_f1_minimum"])
        and error_auroc is not None
        and error_auroc
        >= float(gate["calibration_error_detection_auroc_minimum"])
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_csr_certificate_v1",
        "state": "complete_known_validation_only",
        "algorithm": "krc_csr_caeos_v1",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "suite": suite,
        "scenario": scenario,
        "source_capture_manifest_file_sha256": file_hash(capture_path),
        "clean_evidence_file_sha256": file_hash(
            capture_dir / "clean_run" / "evidence_package.npz"
        ),
        "validation_labels_file_sha256": file_hash(
            capture_dir / "robust_run" / "scores.npz"
        ),
        "partition": {
            "rule": "even_indices_existing_csr_calibration_partition",
            "total_count": int(len(labels)),
            "calibration_count": int(len(selected)),
        },
        "calibration_known_macro_f1": macro_f1,
        "calibration_error_detection_auroc": error_auroc,
        "thresholds": gate,
        "routing_enabled": enabled,
        "test_arrays_read": [],
        "unknown_or_test_labels_used": False,
        "known_validation_labels_used": True,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--capture-dir", type=Path, required=True)
    parser.add_argument("--suite", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = certify(
        load(args.protocol),
        args.capture_dir.resolve(),
        suite=args.suite,
        scenario=args.scenario,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
