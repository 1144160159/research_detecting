from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from caeos.class_conditional_reliability_fusion import (
    fit_class_conditional_reliability,
    reliability_fused_candidate,
)
from caeos.validation_gated_reliability_fusion import (
    apply_validation_gate,
    validation_safety_gate,
)
from caeos.vgrf_deployment import VGRFDeploymentBundle


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def higher_quantile(values: np.ndarray, quantile: float) -> float:
    try:
        return float(np.quantile(values, quantile, method="higher"))
    except TypeError:
        return float(
            np.quantile(values, quantile, interpolation="higher")
        )


def _candidate(
    evidence: Any,
    split: str,
    class_reliability: np.ndarray,
    incumbent_risk: np.ndarray,
    risk_blend: float,
) -> dict[str, Any]:
    return reliability_fused_candidate(
        view_probability=evidence[f"{split}_view_probability"],
        class_reliability=class_reliability,
        global_probability=evidence[f"{split}_global_probability"],
        incumbent_view_fused_probability=evidence[
            f"{split}_view_fused_probability"
        ],
        incumbent_gate=evidence[f"{split}_gate"],
        incumbent_final_probability=evidence[f"{split}_final_probability"],
        incumbent_risk=incumbent_risk,
        risk_blend=risk_blend,
    )


def _gate(
    args: argparse.Namespace,
    labels: np.ndarray,
    incumbent_probability: np.ndarray,
    candidate_probability: np.ndarray,
    incumbent_risk: np.ndarray,
    candidate_risk: np.ndarray,
) -> dict[str, Any]:
    return validation_safety_gate(
        labels=labels,
        incumbent_probability=incumbent_probability,
        candidate_probability=candidate_probability,
        incumbent_risk=incumbent_risk,
        candidate_risk=candidate_risk,
        minimum_f1_gain=args.minimum_f1_gain,
        maximum_correct_risk_increase=args.maximum_correct_risk_increase,
        minimum_auc_gain=args.minimum_auc_gain,
        minimum_separation_gain=args.minimum_separation_gain,
        minimum_strict_proxy_gain=args.minimum_strict_proxy_gain,
    )


def _views(path: Path) -> list[np.ndarray]:
    with np.load(path, allow_pickle=False) as payload:
        if any(not name.startswith("view_") for name in payload.files):
            raise ValueError(f"invalid processed view name in {path}")
        names = sorted(
            payload.files, key=lambda name: int(name[len("view_") :])
        )
        if names != [f"view_{index}" for index in range(len(names))]:
            raise ValueError(f"non-contiguous processed views in {path}")
        return [np.asarray(payload[name]) for name in names]


def build(args: argparse.Namespace) -> dict[str, Any]:
    pairwise_capture_dir = args.pairwise_capture_dir.resolve()
    reference_run_dir = args.reference_run_dir.resolve()
    output_dir = args.output_dir.resolve()
    capture_manifest_path = pairwise_capture_dir / "capture_manifest.json"
    capture_manifest = json.loads(
        capture_manifest_path.read_text(encoding="utf-8")
    )
    if (
        capture_manifest.get("schema_version")
        != "strict_v4_pairwise_deployment_capture_v3"
    ):
        raise ValueError(
            "VGRF deployment requires Pairwise capture schema v3"
        )
    pairwise_path = pairwise_capture_dir / capture_manifest[
        "deployment_artifact"
    ]
    if file_hash(pairwise_path) != capture_manifest[
        "deployment_artifact_sha256"
    ]:
        raise ValueError("Pairwise deployment artifact SHA-256 mismatch")
    pairwise = joblib.load(pairwise_path)

    benchmark_inputs_path = pairwise_capture_dir / capture_manifest[
        "processed_benchmark_inputs"
    ]
    validation_inputs_path = pairwise_capture_dir / capture_manifest[
        "processed_validation_inputs"
    ]
    if file_hash(benchmark_inputs_path) != capture_manifest[
        "processed_benchmark_inputs_sha256"
    ]:
        raise ValueError("Pairwise benchmark input SHA-256 mismatch")
    if file_hash(validation_inputs_path) != capture_manifest[
        "processed_validation_inputs_sha256"
    ]:
        raise ValueError("Pairwise validation input SHA-256 mismatch")
    benchmark_views = _views(benchmark_inputs_path)
    validation_views = _views(validation_inputs_path)
    stable_validation = pairwise.runtime.predict(validation_views)
    stable_test = pairwise.runtime.predict(benchmark_views)

    evidence_path = reference_run_dir / "evidence_package.npz"
    scores_path = reference_run_dir / "scores.npz"
    if not evidence_path.is_file() or not scores_path.is_file():
        raise FileNotFoundError("reference run evidence or scores are missing")
    with np.load(scores_path, allow_pickle=False) as scores:
        if "validation_labels" not in scores.files:
            raise ValueError("reference scores lack validation labels")
        validation_labels = np.asarray(
            scores["validation_labels"], dtype=np.int64
        )
        score_fields_present_but_not_accessed = sorted(
            name for name in scores.files if name != "validation_labels"
        )

    with np.load(evidence_path, allow_pickle=False) as evidence:
        reliability_fit = fit_class_conditional_reliability(
            evidence["validation_view_probability"],
            validation_labels,
            shrinkage=args.shrinkage,
            minimum_reliability=args.minimum_reliability,
        )
        if not np.array_equal(
            stable_validation["probability"],
            evidence["validation_final_probability"],
        ):
            raise ValueError(
                "stable runtime validation probability differs from source"
            )
        if not np.array_equal(
            stable_test["probability"], evidence["test_final_probability"]
        ):
            raise ValueError("stable runtime test probability differs from source")

        source_validation_candidate = _candidate(
            evidence,
            "validation",
            reliability_fit["reliability"],
            evidence["validation_selected_risk"],
            args.risk_blend,
        )
        source_gate = _gate(
            args,
            validation_labels,
            evidence["validation_final_probability"],
            source_validation_candidate["candidate_probability"],
            evidence["validation_selected_risk"],
            source_validation_candidate["candidate_risk"],
        )
        deployment_validation_candidate = _candidate(
            evidence,
            "validation",
            reliability_fit["reliability"],
            stable_validation["risk"],
            args.risk_blend,
        )
        deployment_gate = _gate(
            args,
            validation_labels,
            evidence["validation_final_probability"],
            deployment_validation_candidate["candidate_probability"],
            stable_validation["risk"],
            deployment_validation_candidate["candidate_risk"],
        )
        if deployment_gate["enabled"] is not source_gate["enabled"]:
            raise RuntimeError(
                "stable runtime changes the known-validation VGRF gate decision"
            )
        _, source_validation_risk = apply_validation_gate(
            gate=source_gate,
            incumbent_probability=evidence[
                "validation_final_probability"
            ],
            candidate_probability=source_validation_candidate[
                "candidate_probability"
            ],
            incumbent_risk=evidence["validation_selected_risk"],
            candidate_risk=source_validation_candidate["candidate_risk"],
        )
        _, deployment_validation_risk = apply_validation_gate(
            gate=deployment_gate,
            incumbent_probability=evidence[
                "validation_final_probability"
            ],
            candidate_probability=deployment_validation_candidate[
                "candidate_probability"
            ],
            incumbent_risk=stable_validation["risk"],
            candidate_risk=deployment_validation_candidate[
                "candidate_risk"
            ],
        )
        source_test_candidate = _candidate(
            evidence,
            "test",
            reliability_fit["reliability"],
            evidence["test_selected_risk"],
            args.risk_blend,
        )
        source_test_probability, source_test_risk = apply_validation_gate(
            gate=source_gate,
            incumbent_probability=evidence["test_final_probability"],
            candidate_probability=source_test_candidate[
                "candidate_probability"
            ],
            incumbent_risk=evidence["test_selected_risk"],
            candidate_risk=source_test_candidate["candidate_risk"],
        )
        deployment_test_candidate = _candidate(
            evidence,
            "test",
            reliability_fit["reliability"],
            stable_test["risk"],
            args.risk_blend,
        )
        expected_probability, expected_risk = apply_validation_gate(
            gate=deployment_gate,
            incumbent_probability=evidence["test_final_probability"],
            candidate_probability=deployment_test_candidate[
                "candidate_probability"
            ],
            incumbent_risk=stable_test["risk"],
            candidate_risk=deployment_test_candidate["candidate_risk"],
        )

    source_threshold = higher_quantile(
        source_validation_risk, args.known_rejection_quantile
    )
    selected_threshold = higher_quantile(
        deployment_validation_risk, args.known_rejection_quantile
    )
    bundle = VGRFDeploymentBundle(
        pairwise=pairwise,
        class_reliability=reliability_fit["reliability"],
        validation_gate=deployment_gate,
        selected_threshold=selected_threshold,
        risk_blend=args.risk_blend,
        source_protocol_manifest_sha256=args.source_protocol_manifest_sha256,
    )
    replay = bundle.predict_views(benchmark_views)
    expected_prediction = np.asarray(expected_probability).argmax(axis=1)
    expected_prediction = expected_prediction.astype(np.int64)
    expected_rejected = np.asarray(expected_risk) > selected_threshold
    equivalence = {
        "schema_version": "strict_v4_vgrf_deployment_equivalence_v2",
        "probability_array_equal": bool(
            np.array_equal(replay["probability"], expected_probability)
        ),
        "closed_set_prediction_array_equal": bool(
            np.array_equal(replay["closed_set_index"], expected_prediction)
        ),
        "risk_array_equal": bool(
            np.array_equal(replay["risk"], expected_risk)
        ),
        "rejection_array_equal": bool(
            np.array_equal(replay["rejected"], expected_rejected)
        ),
        "selected_threshold": float(selected_threshold),
        "validation_gate_enabled": bool(deployment_gate["enabled"]),
        "test_count": int(len(expected_risk)),
        "unknown_or_test_labels_used_for_reliability_gate_threshold_or_prediction": False,
    }
    equivalence["passes"] = all(
        value is True
        for key, value in equivalence.items()
        if key.endswith("_equal")
    )
    if not equivalence["passes"]:
        raise RuntimeError(f"VGRF deployment equivalence failed: {equivalence}")

    compatibility = {
        "schema_version": "strict_v4_vgrf_source_runtime_compatibility_v1",
        "source_gate_enabled": bool(source_gate["enabled"]),
        "deployment_gate_enabled": bool(deployment_gate["enabled"]),
        "gate_decision_equal": bool(
            source_gate["enabled"] is deployment_gate["enabled"]
        ),
        "test_probability_array_equal": bool(
            np.array_equal(expected_probability, source_test_probability)
        ),
        "test_risk_max_absolute_difference": float(
            np.max(
                np.abs(
                    np.asarray(expected_risk)
                    - np.asarray(source_test_risk)
                )
            )
        ),
        "source_threshold": float(source_threshold),
        "deployment_threshold": float(selected_threshold),
        "threshold_absolute_difference": float(
            abs(source_threshold - selected_threshold)
        ),
        "interpretation": (
            "diagnostic_only_stable_runtime_tie_policy_is_used_for_deployment"
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = output_dir / "vgrf_deployment_bundle.joblib"
    joblib.dump(bundle, artifact_path, compress=3)
    restored = joblib.load(artifact_path)
    restored_output = restored.predict_views(benchmark_views)
    roundtrip = {
        name: bool(np.array_equal(restored_output[name], replay[name]))
        for name in (
            "closed_set_index",
            "probability",
            "risk",
            "rejected",
        )
    }
    roundtrip["passes"] = all(roundtrip.values())
    if not roundtrip["passes"]:
        raise RuntimeError(f"VGRF serialization failed: {roundtrip}")

    output_inputs_path = output_dir / "processed_benchmark_inputs.npz"
    np.savez_compressed(
        output_inputs_path,
        **{
            f"view_{index}": view
            for index, view in enumerate(benchmark_views)
        },
    )
    output_expected_path = (
        output_dir / "processed_benchmark_expected_outputs.npz"
    )
    np.savez_compressed(
        output_expected_path,
        closed_set_index=replay["closed_set_index"],
        probability=replay["probability"],
        risk=replay["risk"],
        rejected=replay["rejected"],
    )
    equivalence_path = output_dir / "equivalence.json"
    equivalence_path.write_text(
        json.dumps(equivalence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    compatibility_path = output_dir / "source_runtime_compatibility.json"
    compatibility_path.write_text(
        json.dumps(compatibility, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": "strict_v4_vgrf_deployment_capture_v2",
        "deployment_artifact": artifact_path.name,
        "deployment_artifact_sha256": file_hash(artifact_path),
        "deployment_artifact_bytes": artifact_path.stat().st_size,
        "processed_benchmark_inputs": output_inputs_path.name,
        "processed_benchmark_inputs_sha256": file_hash(output_inputs_path),
        "processed_benchmark_inputs_contain_labels": False,
        "processed_benchmark_expected_outputs": output_expected_path.name,
        "processed_benchmark_expected_outputs_sha256": file_hash(
            output_expected_path
        ),
        "processed_benchmark_expected_outputs_contain_ground_truth": False,
        "equivalence": equivalence_path.name,
        "equivalence_sha256": file_hash(equivalence_path),
        "source_equivalence": equivalence,
        "source_runtime_compatibility": compatibility_path.name,
        "source_runtime_compatibility_sha256": file_hash(
            compatibility_path
        ),
        "serialization_roundtrip": roundtrip,
        "deployment_evidence": bundle.evidence(),
        "validation_source": {
            "evidence_package_sha256": file_hash(evidence_path),
            "scores_archive_sha256": file_hash(scores_path),
            "scores_field_accessed": ["validation_labels"],
            "scores_fields_present_but_not_accessed": (
                score_fields_present_but_not_accessed
            ),
            "validation_labels_stored_in_deployment_artifact": False,
        },
        "known_validation_fit": {
            "support": reliability_fit["support"].tolist(),
            "correct": reliability_fit["correct"].tolist(),
            "base_reliability": reliability_fit[
                "base_reliability"
            ].tolist(),
            "source_validation_gate": source_gate,
            "deployment_validation_gate": deployment_gate,
        },
        "source_pairwise_capture_manifest_sha256": file_hash(
            capture_manifest_path
        ),
        "source_pairwise_artifact_sha256": file_hash(pairwise_path),
        "formal_model_metrics_admitted": 0,
        "formal_external_execution_admitted": False,
        "storage_policy": "gpu_private_do_not_publish",
    }
    manifest_path = output_dir / "capture_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairwise-capture-dir", type=Path, required=True)
    parser.add_argument("--reference-run-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-protocol-manifest-sha256", required=True)
    parser.add_argument("--shrinkage", type=float, default=20.0)
    parser.add_argument("--minimum-reliability", type=float, default=0.05)
    parser.add_argument("--risk-blend", type=float, default=0.25)
    parser.add_argument("--known-rejection-quantile", type=float, default=0.95)
    parser.add_argument("--minimum-f1-gain", type=float, default=-0.002)
    parser.add_argument(
        "--maximum-correct-risk-increase", type=float, default=0.01
    )
    parser.add_argument("--minimum-auc-gain", type=float, default=0.0)
    parser.add_argument("--minimum-separation-gain", type=float, default=0.0)
    parser.add_argument(
        "--minimum-strict-proxy-gain", type=float, default=0.005
    )
    result = build(parser.parse_args())
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
