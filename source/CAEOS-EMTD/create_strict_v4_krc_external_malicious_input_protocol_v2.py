from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Dict

from external_dataset_protocol_utils import (
    canonical_hash,
    file_hash,
    load_json,
)


def corrected_tasks(tasks: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    corrected = []
    for source in tasks:
        task = copy.deepcopy(source)
        seed = int(task["training_seed"])
        task["prepared_seed"] = seed
        task["split_seed"] = seed
        task["opendetect_seed"] = seed
        corrected.append(task)
    identities = {
        (
            task["dataset"],
            task["unknown_attack_family"],
            int(task["training_seed"]),
        )
        for task in corrected
    }
    if len(corrected) != 96 or len(identities) != 96:
        raise ValueError("corrected external task universe must be 96 unique")
    return corrected


def create(
    *,
    v1_path: Path,
    result_root: Path,
    creator_path: Path,
) -> Dict[str, Any]:
    v1 = load_json(v1_path)
    if (
        v1.get("schema_version")
        != "strict_v4_krc_external_malicious_input_protocol_v1"
        or v1.get("manifest_sha256") != canonical_hash(v1)
        or v1.get("execution_admitted") is not False
        or v1.get("task_counts", {}).get("total_scenarios_per_algorithm")
        != 96
    ):
        raise ValueError("canonical zero-result KRC external input v1 required")
    forbidden = [
        *result_root.rglob("capture_manifest.json"),
        *result_root.rglob("candidate_metrics.json"),
        *result_root.rglob("opendetect_metrics.json"),
        *result_root.rglob("summary.json"),
        *result_root.rglob("audit.json"),
    ] if result_root.exists() else []
    if forbidden:
        raise ValueError("KRC external v2 correction requires zero results")

    tasks = corrected_tasks(v1["tasks"])
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_external_malicious_input_protocol_v2"
        ),
        "status": (
            "seed_contract_corrected_before_execution_waiting_positive_"
            "krc_confirmation"
        ),
        "execution_admitted": False,
        "algorithm": v1["algorithm"],
        "comparators": v1["comparators"],
        "scenario_rule": v1["scenario_rule"],
        "split_rule": v1["split_rule"],
        "known_only_fit_selection_calibration_and_threshold": v1[
            "known_only_fit_selection_calibration_and_threshold"
        ],
        "dataset_registry": v1["dataset_registry"],
        "tasks": tasks,
        "task_counts": v1["task_counts"],
        "seed_contract": {
            "prepared_seed": [223, 227, 229],
            "candidate_training_seed": "equals_prepared_seed",
            "fingerprint_split_seed": "equals_candidate_training_seed",
            "opendetect_training_and_split_seed": (
                "equals_candidate_training_seed"
            ),
            "augmentation_seed": (
                "independently_derived_and_used_only_for_structured_"
                "augmentation"
            ),
            "validation_profile_seed": (
                "independently_derived_and_used_only_for_known_validation_"
                "profile"
            ),
            "same_split_fingerprint_required_across_candidate_pairwise_"
            "and_opendetect": True,
        },
        "activation_gate": v1["activation_gate"],
        "confirmation_gate": v1["confirmation_gate"],
        "result_root": result_root.resolve().as_posix(),
        "output_counts_at_freeze": {
            "capture_manifest": 0,
            "candidate_metrics": 0,
            "opendetect_metrics": 0,
            "summary": 0,
            "audit": 0,
        },
        "supersedes": {
            "schema_version": v1["schema_version"],
            "manifest_sha256": v1["manifest_sha256"],
            "file_sha256": file_hash(v1_path),
            "reason": (
                "v1 derived split_seed and opendetect_seed would either be "
                "unused or break exact same-split comparison because both "
                "trainers bind --seed to fingerprint splitting"
            ),
            "scientific_data_algorithm_metric_or_gate_changed": False,
            "seed_execution_contract_corrected": True,
        },
        "input_manifest_sha256": {
            **v1["input_manifest_sha256"],
            "input_protocol_v1": v1["manifest_sha256"],
        },
        "input_file_sha256": {
            **v1["input_file_sha256"],
            "input_protocol_v1": file_hash(v1_path),
        },
        "implementation_sha256": {
            creator_path.name: file_hash(creator_path)
        },
        "claim_boundary": {
            **v1["claim_boundary"],
            "v1_is_not_execution_authority": True,
            "same_split_is_required_for_all_three_reports": True,
            "seed_correction_does_not_authorize_execution": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create(
        v1_path=args.v1.resolve(),
        result_root=args.result_root.resolve(),
        creator_path=Path(__file__).resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
