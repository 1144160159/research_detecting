from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def benign_metrics(
    prediction: np.ndarray,
    risk: np.ndarray,
    threshold: float | np.ndarray,
    benign_index: int,
) -> Dict[str, Any]:
    prediction = np.asarray(prediction, dtype=np.int64)
    risk = np.asarray(risk, dtype=np.float64)
    thresholds = np.broadcast_to(
        np.asarray(threshold, dtype=np.float64), risk.shape
    )
    if (
        prediction.ndim != 1
        or risk.shape != prediction.shape
        or not len(prediction)
        or not np.isfinite(risk).all()
        or not np.isfinite(thresholds).all()
        or np.any(thresholds <= 0.0)
    ):
        raise ValueError("invalid benign safety output")
    return {
        "row_count": int(len(prediction)),
        "false_alert_rate": float(
            np.mean(prediction != int(benign_index))
        ),
        "known_attack_assignment_rate": float(
            np.mean(
                (risk <= thresholds)
                & (prediction != int(benign_index))
            )
        ),
        "reject_rate": float(np.mean(risk > thresholds)),
        "operational_intervention_rate": float(
            np.mean(
                (prediction != int(benign_index))
                | (risk > thresholds)
            )
        ),
        "normalized_risk_quantiles": {
            name: float(np.quantile(risk / thresholds, quantile))
            for name, quantile in (
                ("p50", 0.50),
                ("p95", 0.95),
                ("p99", 0.99),
            )
        },
    }


def batched_predictions(method, views, batch_size: int = 8192):
    arrays = [np.asarray(view) for view in views]
    if (
        not arrays
        or len({len(view) for view in arrays}) != 1
        or int(batch_size) < 1
    ):
        raise ValueError("aligned views and positive batch size required")
    outputs = []
    for start in range(0, len(arrays[0]), int(batch_size)):
        stop = min(len(arrays[0]), start + int(batch_size))
        outputs.append(method([view[start:stop] for view in arrays]))
    return {
        name: np.concatenate(
            [np.asarray(output[name]) for output in outputs], axis=0
        )
        for name in ("prediction", "risk")
    }


def evaluate(
    *,
    protocol: Dict[str, Any],
    source: Dict[str, Any],
    deployment_dir: Path,
    output: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_mdr_parrot_safety_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical MDR PARROT protocol required")
    identity = (str(source["scenario"]), int(source["training_seed"]))
    matches = [
        item
        for item in protocol["source_model_pairs"]
        if (
            str(item["scenario"]),
            int(item["training_seed"]),
        )
        == identity
    ]
    if len(matches) != 1:
        raise ValueError("MDR PARROT source identity is not in protocol")
    frozen = matches[0]
    manifest_path = deployment_dir / "capture_manifest.json"
    manifest = load(manifest_path)
    candidate_path = deployment_dir / manifest["deployment_artifact"]
    comparator_path = Path(frozen["opendetect_runtime"])
    if (
        manifest.get("schema_version")
        != "strict_v4_mdr_parrot_deployment_capture_v1"
        or manifest.get("manifest_sha256") != canonical_hash(manifest)
        or manifest.get("state") != "complete"
        or manifest.get("scenario") != identity[0]
        or int(manifest.get("training_seed", -1)) != identity[1]
        or manifest.get("source_split_fingerprint")
        != frozen["source_split_fingerprint"]
        or manifest.get("serialization_roundtrip", {}).get("passes")
        is not True
        or file_hash(candidate_path)
        != manifest["deployment_artifact_sha256"]
        or file_hash(comparator_path)
        != frozen["opendetect_runtime_sha256"]
    ):
        raise ValueError("invalid MDR PARROT model pair artifacts")
    candidate = joblib.load(candidate_path)
    comparator = joblib.load(comparator_path)
    evidence = candidate.evidence()
    if (
        evidence.get("schema_version")
        != "strict_v4_mdr_deployment_bundle_v1"
        or evidence.get("feature_columns") != protocol["feature_columns"]
        or int(evidence.get("feature_count", -1)) != 56
        or evidence.get("source_config_sha256") != frozen["config_sha256"]
        or evidence.get("source_split_fingerprint")
        != frozen["source_split_fingerprint"]
    ):
        raise ValueError("MDR PARROT raw-feature deployment contract drifted")
    feature_root = Path(protocol["feature_root"])
    records = []
    for capture in protocol["parrot_captures"]:
        capture_id = str(capture["capture_id"])
        shard_root = feature_root / "shards" / capture_id
        shard_manifest_path = shard_root / "manifest.json"
        csv_path = shard_root / "features.csv"
        shard_manifest = load(shard_manifest_path)
        if (
            shard_manifest.get("schema_version")
            != "parrot2025_no_decryption_feature_shard_v1"
            or shard_manifest.get("manifest_sha256")
            != canonical_hash(shard_manifest)
            or shard_manifest.get("capture") != capture
            or shard_manifest.get("manifest_sha256")
            != protocol["feature_shard_manifest_sha256"][capture_id]
            or shard_manifest.get("features_csv_sha256")
            != file_hash(csv_path)
        ):
            raise ValueError(f"invalid PARROT feature shard: {capture_id}")
        frame = pd.read_csv(csv_path)
        if (
            list(frame.columns)
            != protocol["feature_columns"] + protocol["metadata_columns"]
            or len(frame) != int(shard_manifest["flow_row_count"])
            or not len(frame)
        ):
            raise ValueError(f"invalid PARROT feature frame: {capture_id}")
        views, quality = candidate.transform_frame(frame)
        candidate_output = batched_predictions(candidate.predict_views, views)
        comparator_output = batched_predictions(comparator.predict, views)
        candidate_metrics = benign_metrics(
            candidate_output["prediction"],
            candidate_output["risk"],
            candidate.selected_threshold,
            candidate.benign_index,
        )
        comparator_metrics = benign_metrics(
            comparator_output["prediction"],
            comparator_output["risk"],
            float(frozen["opendetect_threshold"]),
            candidate.benign_index,
        )
        records.append(
            {
                "capture_id": capture_id,
                "application": capture["application"],
                "flow_row_count": int(len(frame)),
                "feature_shard_manifest_sha256": shard_manifest[
                    "manifest_sha256"
                ],
                "feature_csv_sha256": shard_manifest[
                    "features_csv_sha256"
                ],
                "input_quality_mean_by_modality": np.mean(
                    quality, axis=0
                ).tolist(),
                "mdr_caeos_v1": candidate_metrics,
                "opendetect": comparator_metrics,
            }
        )
    if len(records) != 320 or len(
        {record["capture_id"] for record in records}
    ) != 320:
        raise ValueError("MDR PARROT capture coverage is incomplete")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_parrot_model_pair_metrics_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "source": {
            "suite": "ustc_tfc2016",
            "scenario": identity[0],
            "training_seed": identity[1],
            "source_split_fingerprint": frozen[
                "source_split_fingerprint"
            ],
        },
        "candidate_deployment_manifest_file_sha256": file_hash(
            manifest_path
        ),
        "candidate_deployment_artifact_sha256": manifest[
            "deployment_artifact_sha256"
        ],
        "opendetect_runtime_sha256": frozen["opendetect_runtime_sha256"],
        "opendetect_threshold": float(frozen["opendetect_threshold"]),
        "source_benign_reference": manifest["source_benign_reference"],
        "capture_count": len(records),
        "records": records,
        "failure_count": 0,
        "parrot_features_or_labels_used_for_fit_selection_calibration_or_threshold": False,
        "payload_decryption_used": False,
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
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--training-seed", type=int, required=True)
    parser.add_argument("--deployment-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = evaluate(
        protocol=load(args.protocol),
        source={
            "scenario": args.scenario,
            "training_seed": args.training_seed,
        },
        deployment_dir=args.deployment_dir,
        output=args.output,
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
