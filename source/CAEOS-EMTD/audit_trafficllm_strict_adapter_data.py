from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash


EXPECTED_CLASSES = {
    "BitTorrent",
    "Facetime",
    "Geodo",
    "Gmail",
    "Htbot",
    "Miuref",
    "Nsis-ay",
    "Outlook",
    "Skype",
    "Virut",
    "WorldOfWarcraft",
    "Zeus",
}
FULL_DIRECTORY = "USTC-TFC-2016_npy_v3_balacned_3000_6000"
SPLIT_DIRECTORY = (
    "USTC-TFC-2016_npy_v3_balacned_3000_6000_train_test_splited"
)
OFFICIAL_AGGREGATE_FILES = (
    "X_train.npy",
    "y_train.npy",
    "X_valid.npy",
    "y_valid.npy",
    "X_test.npy",
    "y_test.npy",
)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def class_directories(path: Path) -> set[str]:
    if not path.is_dir():
        return set()
    return {entry.name for entry in path.iterdir() if entry.is_dir()}


def immediate_sidecars(paths: tuple[Path, ...]) -> list[str]:
    suffixes = {".csv", ".json", ".jsonl", ".parquet"}
    sidecars = []
    for root in paths:
        if not root.is_dir():
            continue
        sidecars.extend(
            str(path.resolve())
            for path in root.iterdir()
            if path.is_file() and path.suffix.lower() in suffixes
        )
    return sorted(sidecars)


def audit(
    official_root: Path,
    prior_audit_path: Path,
    dataset_root: Path,
) -> dict[str, Any]:
    official_root = official_root.resolve()
    prior_audit_path = prior_audit_path.resolve()
    dataset_root = dataset_root.resolve()
    prior = load(prior_audit_path)
    source = prior["source_audit"]["TrafficLLM"]
    preprocessor = official_root / "preprocessor.py"
    if file_hash(preprocessor) != source["key_source_sha256"][
        "preprocessor.py"
    ]:
        raise ValueError("TrafficLLM preprocessor differs from frozen audit")
    text = preprocessor.read_text(encoding="utf-8")
    if "s.replace(" not in text:
        raise ValueError("TrafficLLM string preprocessing contract not found")
    if not all(name in text for name in OFFICIAL_AGGREGATE_FILES):
        raise ValueError("TrafficLLM aggregate input contract is incomplete")

    full_root = dataset_root / FULL_DIRECTORY
    split_root = dataset_root / SPLIT_DIRECTORY
    full_classes = class_directories(full_root)
    train_classes = class_directories(split_root / "train")
    test_classes = class_directories(split_root / "test")
    sample_paths = sorted(
        (split_root / "train" / sorted(EXPECTED_CLASSES)[0]).glob("*.npy")
    )
    if not sample_paths:
        raise ValueError("CrossPlatform USTC split has no deterministic sample")
    sample_path = sample_paths[0]
    sample = np.load(sample_path, allow_pickle=False)

    aggregate_locations = {}
    for name in OFFICIAL_AGGREGATE_FILES:
        candidates = [
            dataset_root / name,
            full_root / name,
            split_root / name,
        ]
        aggregate_locations[name] = [
            str(path.resolve()) for path in candidates if path.is_file()
        ]
    all_aggregate_files_present = all(aggregate_locations.values())
    sidecars = immediate_sidecars((dataset_root, full_root, split_root))
    sample_name = sample_path.name.lower()
    sample_group_bound = (
        "window_" in sample_name or "capturegroup" in sample_name
    )
    sample_string_compatible = isinstance(sample, (str, np.str_))

    result = {
        "schema_version": "trafficllm_strict_adapter_data_audit_v1",
        "prior_native_admission_audit_sha256": file_hash(prior_audit_path),
        "trafficllm_source": {
            "head": source["head"],
            "source_tree_sha256": source["source_tree_sha256"],
            "preprocessor_sha256": file_hash(preprocessor),
            "expects_aggregate_files": list(OFFICIAL_AGGREGATE_FILES),
            "expects_string_replace_preprocessing": True,
        },
        "candidate_dataset": {
            "root": str(dataset_root),
            "full_class_directories": sorted(full_classes),
            "train_class_directories": sorted(train_classes),
            "test_class_directories": sorted(test_classes),
            "expected_twelve_classes_exact": (
                full_classes == EXPECTED_CLASSES
                and train_classes == EXPECTED_CLASSES
                and test_classes == EXPECTED_CLASSES
            ),
            "official_aggregate_file_locations": aggregate_locations,
            "all_official_aggregate_files_present": (
                all_aggregate_files_present
            ),
            "immediate_group_sidecars": sidecars,
            "sample_path": str(sample_path.resolve()),
            "sample_sha256": file_hash(sample_path),
            "sample_shape": list(sample.shape),
            "sample_dtype": str(sample.dtype),
            "sample_is_string_compatible": sample_string_compatible,
            "sample_name_has_capture_or_window_group": sample_group_bound,
        },
        "strict_adapter_gates": {
            "frozen_official_source_binding": True,
            "twelve_class_directory_identity": (
                full_classes == EXPECTED_CLASSES
                and train_classes == EXPECTED_CLASSES
                and test_classes == EXPECTED_CLASSES
            ),
            "official_aggregate_layout_present": all_aggregate_files_present,
            "sample_type_matches_official_preprocessor": (
                sample_string_compatible
            ),
            "capture_or_session_group_binding_present": (
                bool(sidecars) or sample_group_bound
            ),
            "unknown_or_test_labels_used": False,
        },
        "admission_decision": {
            "crossplatform_arrays_are_trafficllm_author_native_data": False,
            "strict_v4_protocol_adapter_execution_admitted": False,
            "new_model_metrics_generated": False,
            "count_as_formal_method_now": False,
            "required_next_evidence": [
                (
                    "Author-compatible USTC X_train/X_valid/X_test string "
                    "inputs with immutable file hashes."
                ),
                (
                    "A source-PCAP or session identifier for every sample so "
                    "train, validation, test, and unknown splits are group "
                    "disjoint."
                ),
                (
                    "A frozen GPT-2 model/tokenizer revision and dependency "
                    "lock before any metric is observed."
                ),
            ],
        },
        "claim_boundary": {
            "crossplatform_or_mapps_layout_must_not_be_called_trafficllm_native": (
                True
            ),
            "array_shape_compatibility_does_not_establish_data_lineage": True,
            "no_trafficllm_effect_or_sota_claim_admitted": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official-root", type=Path, required=True)
    parser.add_argument("--prior-audit", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit(
        args.official_root, args.prior_audit, args.dataset_root
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
