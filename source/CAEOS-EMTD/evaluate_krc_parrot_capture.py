from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd

from caeos.pairwise_deployment import PairwiseDeploymentBundle
from capture_krc_parrot_deployment_bundle import trainer_namespace
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_parrot_capture import batched_predictions, benign_metrics
import train_hybrid_open_set as trainer


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def evaluate(
    *,
    protocol: Dict[str, Any],
    source: Dict[str, Any],
    deployment_dir: Path,
    output: Path,
) -> Dict[str, Any]:
    if (
        protocol.get("schema_version")
        != "strict_v4_krc_parrot_safety_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
    ):
        raise ValueError("canonical KRC PARROT protocol required")
    identity = (str(source["scenario"]), int(source["training_seed"]))
    matches = [
        item
        for item in protocol["source_model_pairs"]
        if (str(item["scenario"]), int(item["training_seed"])) == identity
    ]
    if len(matches) != 1:
        raise ValueError("KRC PARROT source identity is not in protocol")
    frozen = matches[0]
    manifest_path = deployment_dir / "capture_manifest.json"
    manifest = load(manifest_path)
    candidate_path = deployment_dir / manifest["deployment_artifact"]
    comparator_path = Path(frozen["opendetect_runtime"])
    if (
        manifest.get("schema_version")
        != "strict_v4_krc_parrot_deployment_capture_v1"
        or manifest.get("manifest_sha256") != canonical_hash(manifest)
        or manifest.get("state") != "complete"
        or manifest.get("scenario") != identity[0]
        or int(manifest.get("training_seed", -1)) != identity[1]
        or manifest.get("source_split_fingerprint")
        != frozen["source_split_fingerprint"]
        or manifest.get("preprocessing_replay", {}).get(
            "all_view_arrays_equal"
        )
        is not True
        or manifest.get("serialization_roundtrip", {}).get("passes")
        is not True
        or manifest.get("model_refit_performed") is not False
        or file_hash(candidate_path)
        != manifest["deployment_artifact_sha256"]
        or file_hash(comparator_path)
        != frozen["opendetect_runtime_sha256"]
    ):
        raise ValueError("invalid KRC PARROT model pair artifacts")
    candidate = joblib.load(candidate_path)
    comparator = joblib.load(comparator_path)
    _, comparator_config, comparator_data = trainer_namespace(
        list(frozen["opendetect_preprocessing_arguments"]),
        Path(protocol["paths"]["project_root"]),
    )
    comparator_preprocessing = comparator_data.preprocessing
    comparator_transform = PairwiseDeploymentBundle(
        runtime=candidate.runtime,
        modality_names=tuple(comparator_data.modality_names),
        modalities={
            str(name): tuple(columns)
            for name, columns in comparator_preprocessing[
                "modalities"
            ].items()
        },
        processor_states={
            str(name): {
                key: list(values) for key, values in state.items()
            }
            for name, state in comparator_preprocessing[
                "processors"
            ].items()
        },
        class_names=tuple(comparator_data.class_names),
        benign_index=int(comparator_data.benign_index),
        selected_threshold=float(frozen["opendetect_threshold"]),
        risk_policy_name="opendetect_frozen_preprocessing_only",
        source_config_sha256=file_hash(comparator_config),
    )
    with np.load(
        Path(frozen["opendetect_benchmark_inputs"]), allow_pickle=False
    ) as archive:
        names = sorted(
            archive.files, key=lambda name: int(name.rsplit("_", 1)[1])
        )
        comparator_frozen_views = [np.asarray(archive[name]) for name in names]
    comparator_prepared_views = [
        np.asarray(view) for view in trainer.views(comparator_data.test)
    ]
    if (
        file_hash(Path(frozen["opendetect_benchmark_inputs"]))
        != frozen["opendetect_benchmark_inputs_sha256"]
        or file_hash(Path(frozen["opendetect_csv"]))
        != frozen["opendetect_csv_sha256"]
        or file_hash(comparator_config)
        != frozen["opendetect_config_sha256"]
        or len(comparator_prepared_views) != len(comparator_frozen_views)
        or not all(
            np.array_equal(left, right)
            for left, right in zip(
                comparator_prepared_views, comparator_frozen_views
            )
        )
        or tuple(candidate.class_names)
        != tuple(comparator_transform.class_names)
        or int(candidate.benign_index)
        != int(comparator_transform.benign_index)
    ):
        raise ValueError("OpenDetect preprocessing replay contract drifted")
    evidence = candidate.evidence()
    if (
        evidence.get("schema_version")
        != "strict_v4_krc_deployment_bundle_v1"
        or evidence.get("feature_count") != 56
        or list(candidate.feature_columns) != protocol["feature_columns"]
        or evidence.get("source_config_sha256") != frozen["config_sha256"]
        or evidence.get("source_split_fingerprint")
        != frozen["source_split_fingerprint"]
        or evidence.get("source_capture_manifest_sha256")
        != frozen["source_capture_manifest_sha256"]
    ):
        raise ValueError("KRC PARROT deployment contract drifted")
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
        comparator_views, _ = comparator_transform.transform_frame(frame)
        candidate_output = batched_predictions(candidate.runtime.predict, views)
        comparator_output = batched_predictions(
            comparator.predict, comparator_views
        )
        records.append(
            {
                "capture_id": capture_id,
                "application": capture["application"],
                "flow_row_count": int(len(frame)),
                "feature_shard_manifest_sha256": shard_manifest[
                    "manifest_sha256"
                ],
                "feature_csv_sha256": shard_manifest["features_csv_sha256"],
                "input_quality_mean_by_modality": np.mean(
                    quality, axis=0
                ).tolist(),
                "krc_csr_caeos_v1": benign_metrics(
                    candidate_output["prediction"],
                    candidate_output["risk"],
                    candidate.selected_threshold,
                    candidate.benign_index,
                ),
                "opendetect": benign_metrics(
                    comparator_output["prediction"],
                    comparator_output["risk"],
                    float(frozen["opendetect_threshold"]),
                    candidate.benign_index,
                ),
            }
        )
    if len(records) != 320 or len(
        {record["capture_id"] for record in records}
    ) != 320:
        raise ValueError("KRC PARROT capture coverage is incomplete")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_parrot_model_pair_metrics_v1",
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "source": {
            "suite": "ustc_tfc2016",
            "scenario": identity[0],
            "training_seed": identity[1],
            "opendetect_training_seed": int(
                frozen["opendetect_training_seed"]
            ),
            "source_split_fingerprint": frozen[
                "source_split_fingerprint"
            ],
        },
        "candidate_deployment_manifest_file_sha256": file_hash(manifest_path),
        "candidate_deployment_artifact_sha256": manifest[
            "deployment_artifact_sha256"
        ],
        "opendetect_runtime_sha256": frozen["opendetect_runtime_sha256"],
        "opendetect_threshold": float(frozen["opendetect_threshold"]),
        "source_benign_reference": manifest["source_benign_reference"],
        "capture_count": len(records),
        "records": records,
        "failure_count": 0,
        "parrot_features_or_labels_used_for_fit_selection_calibration_or_threshold": (
            False
        ),
        "payload_decryption_used": False,
        "candidate_model_refit_for_parrot": False,
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
