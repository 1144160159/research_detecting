from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from external_dataset_protocol_utils import (
    canonical_hash,
    file_hash,
    load_json,
)


DATASET_CONTRACT = {
    "LSNM2024": {
        "benign_label": "normal",
        "attack_family_count": 15,
        "config": "configs/lsnm2024_external.json",
    },
    "CICDDoS2019": {
        "benign_label": "BENIGN",
        "attack_family_count": 17,
        "config": "configs/cicids2017_strict.json",
    },
}


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def derive_seed(
    design_manifest_sha256: str,
    dataset: str,
    attack_family: str,
    training_seed: int,
    purpose: str,
) -> int:
    token = (
        f"{design_manifest_sha256}:{dataset}:{attack_family}:"
        f"{int(training_seed)}:{purpose}"
    )
    return int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16) & (
        2**31 - 1
    )


def config_columns(config: Dict[str, Any]) -> list[str]:
    columns = [
        str(column)
        for values in config["modalities"].values()
        for column in values
    ]
    columns.extend(
        [str(config["group_column"]), str(config["label_column"])]
    )
    if len(columns) != len(set(columns)):
        raise ValueError("external config columns are not unique")
    return columns


def verify_zero_outputs(result_root: Path) -> Dict[str, int]:
    patterns = {
        "capture_manifest": "capture_manifest.json",
        "candidate_metrics": "candidate_metrics.json",
        "opendetect_metrics": "opendetect_metrics.json",
        "summary": "summary.json",
        "audit": "audit.json",
    }
    counts = {
        name: len(list(result_root.rglob(pattern)))
        if result_root.exists()
        else 0
        for name, pattern in patterns.items()
    }
    if any(counts.values()):
        raise ValueError(
            "KRC external input protocol requires a zero-result root"
        )
    return counts


def build_tasks(
    *,
    project_root: Path,
    data_root: Path,
    downstream_design: Dict[str, Any],
    preparation_summary: Dict[str, Any],
    readiness: Dict[str, Any],
) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
    external = downstream_design["fresh_external_malicious"]
    datasets = list(external["datasets"])
    seeds = [int(seed) for seed in external["training_seeds"]]
    if datasets != ["LSNM2024", "CICDDoS2019"]:
        raise ValueError("unexpected external dataset order")
    if seeds != [223, 227, 229]:
        raise ValueError("unexpected external training seeds")

    tasks: list[Dict[str, Any]] = []
    registry: Dict[str, Any] = {}
    for dataset in datasets:
        contract = DATASET_CONTRACT[dataset]
        dataset_root = data_root / dataset
        manifest_path = dataset_root / "manifest.json"
        manifest = load_json(manifest_path)
        summary_entry = preparation_summary["datasets"][dataset]
        readiness_entry = readiness["external_prepared"][dataset]
        manifest_file_sha256 = file_hash(manifest_path)
        if (
            manifest.get("schema_version")
            != "gpu_external_prepared_dataset_manifest_v1"
            or manifest.get("dataset") != dataset
            or manifest.get("passed") is not True
            or summary_entry.get("manifest_sha256")
            != manifest_file_sha256
            or readiness_entry.get("manifest_file_sha256")
            != manifest_file_sha256
            or readiness_entry.get("passes") is not True
        ):
            raise ValueError(
                f"invalid prepared dataset identity: {dataset}"
            )

        config_path = project_root / contract["config"]
        config = load_json(config_path)
        expected_columns = config_columns(config)
        config_sha256 = file_hash(config_path)
        seed_records: Dict[str, Any] = {}
        reference_labels: list[str] | None = None
        for seed in seeds:
            csv_path = dataset_root / f"seed{seed}.csv"
            sidecar_path = Path(f"{csv_path}.json")
            sidecar = load_json(sidecar_path)
            manifest_sidecar = manifest["files"].get(str(seed))
            readiness_seed = readiness_entry["seed_checks"].get(str(seed))
            if (
                sidecar != manifest_sidecar
                or sidecar.get("schema_version")
                != "gpu_external_prepared_seed_v1"
                or sidecar.get("dataset") != dataset
                or int(sidecar.get("seed", -1)) != seed
                or sidecar.get("passed") is not True
                or sidecar.get("columns") != expected_columns
                or sidecar.get("csv_sha256") != file_hash(csv_path)
                or sidecar["provenance"].get("config_sha256")
                != config_sha256
                or readiness_seed.get("passes") is not True
                or int(readiness_seed.get("rows", -1))
                != int(sidecar["rows"])
            ):
                raise ValueError(
                    f"invalid prepared seed identity: {dataset}/{seed}"
                )
            labels = sorted(map(str, sidecar["label_counts"]))
            if reference_labels is None:
                reference_labels = labels
            elif labels != reference_labels:
                raise ValueError(
                    f"label set differs across seeds: {dataset}/{seed}"
                )
            seed_records[str(seed)] = {
                "csv": csv_path.resolve().as_posix(),
                "csv_sha256": sidecar["csv_sha256"],
                "sidecar": sidecar_path.resolve().as_posix(),
                "sidecar_file_sha256": file_hash(sidecar_path),
                "rows": int(sidecar["rows"]),
                "label_count": len(labels),
                "groups_per_label": {
                    str(key): int(value)
                    for key, value in sorted(
                        sidecar["groups_per_label"].items()
                    )
                },
            }

        assert reference_labels is not None
        benign_label = str(contract["benign_label"])
        attacks = [
            label for label in reference_labels if label != benign_label
        ]
        if (
            benign_label not in reference_labels
            or len(attacks) != int(contract["attack_family_count"])
            or any(
                seed_records[str(seed)]["groups_per_label"].get(label, 0)
                < 3
                for seed in seeds
                for label in reference_labels
            )
        ):
            raise ValueError(f"invalid external label universe: {dataset}")
        if dataset == "CICDDoS2019" and (
            "UDP-lag" in reference_labels
            or "UDPLag" not in attacks
            or "WebDDoS" not in attacks
        ):
            raise ValueError("CICDDoS2019 reconciliation is not preserved")

        registry[dataset] = {
            "manifest": manifest_path.resolve().as_posix(),
            "manifest_file_sha256": manifest_file_sha256,
            "config": config_path.resolve().as_posix(),
            "config_sha256": config_sha256,
            "benign_label": benign_label,
            "labels": reference_labels,
            "attack_families": attacks,
            "attack_family_count": len(attacks),
            "seeds": seed_records,
        }
        for attack_family in attacks:
            for seed in seeds:
                seed_record = seed_records[str(seed)]
                tasks.append(
                    {
                        "dataset": dataset,
                        "unknown_attack_family": attack_family,
                        "benign_label": benign_label,
                        "training_seed": seed,
                        "split_seed": derive_seed(
                            downstream_design["manifest_sha256"],
                            dataset,
                            attack_family,
                            seed,
                            "split",
                        ),
                        "augmentation_seed": derive_seed(
                            downstream_design["manifest_sha256"],
                            dataset,
                            attack_family,
                            seed,
                            "augmentation",
                        ),
                        "validation_profile_seed": derive_seed(
                            downstream_design["manifest_sha256"],
                            dataset,
                            attack_family,
                            seed,
                            "validation_profile",
                        ),
                        "opendetect_seed": derive_seed(
                            downstream_design["manifest_sha256"],
                            dataset,
                            attack_family,
                            seed,
                            "opendetect",
                        ),
                        "csv": seed_record["csv"],
                        "csv_sha256": seed_record["csv_sha256"],
                        "sidecar": seed_record["sidecar"],
                        "sidecar_file_sha256": seed_record[
                            "sidecar_file_sha256"
                        ],
                        "config": config_path.resolve().as_posix(),
                        "config_sha256": config_sha256,
                    }
                )

    identities = {
        (
            task["dataset"],
            task["unknown_attack_family"],
            int(task["training_seed"]),
        )
        for task in tasks
    }
    expected_total = sum(
        int(DATASET_CONTRACT[dataset]["attack_family_count"])
        for dataset in datasets
    ) * len(seeds)
    if len(tasks) != expected_total or len(identities) != len(tasks):
        raise ValueError("external task universe is incomplete or duplicated")
    return tasks, registry


def create_protocol(
    *,
    project_root: Path,
    data_root: Path,
    result_root: Path,
    downstream_design_path: Path,
    krc_protocol_path: Path,
    preparation_protocol_path: Path,
    preparation_summary_path: Path,
    readiness_path: Path,
    creator_path: Path,
) -> Dict[str, Any]:
    downstream_design = load_json(downstream_design_path)
    krc_protocol = load_json(krc_protocol_path)
    preparation_protocol = load_json(preparation_protocol_path)
    preparation_summary = load_json(preparation_summary_path)
    readiness = load_json(readiness_path)
    require_canonical(
        downstream_design,
        "strict_v4_krc_downstream_sota_design_v1",
        "KRC downstream design",
    )
    require_canonical(
        krc_protocol,
        "strict_v4_krc_csr_confirmation_protocol_v1",
        "KRC confirmation protocol",
    )
    require_canonical(
        preparation_protocol,
        "gpu_external_dataset_preparation_protocol_v2",
        "external preparation protocol",
    )
    require_canonical(
        readiness,
        "strict_v4_krc_downstream_data_readiness_v2",
        "external readiness",
    )
    if (
        downstream_design.get("execution_admitted") is not False
        or downstream_design["activation_gate"][
            "confirmation_summary_protocol_manifest_sha256"
        ]
        != krc_protocol["manifest_sha256"]
        or preparation_summary.get("schema_version")
        != "gpu_external_dataset_preparation_summary_v2"
        or preparation_summary.get(
            "ready_for_frozen_external_experiments"
        )
        is not True
        or preparation_summary.get("protocol_manifest_sha256")
        != preparation_protocol["manifest_sha256"]
        or readiness.get("ready_for_downstream_execution") is not True
        or not all(readiness["checks"].values())
    ):
        raise ValueError("KRC external input activation prerequisites fail")

    tasks, registry = build_tasks(
        project_root=project_root,
        data_root=data_root,
        downstream_design=downstream_design,
        preparation_summary=preparation_summary,
        readiness=readiness,
    )
    zero_counts = verify_zero_outputs(result_root)
    attack_count = sum(
        int(record["attack_family_count"]) for record in registry.values()
    )
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_external_malicious_input_protocol_v1"
        ),
        "status": (
            "data_frozen_ready_waiting_positive_krc_confirmation"
        ),
        "execution_admitted": False,
        "algorithm": "krc_csr_caeos_v1",
        "comparators": ["caeos_pairwise", "opendetect"],
        "scenario_rule": (
            "leave_each_retained_non_benign_attack_family_out_once_per_seed"
        ),
        "split_rule": (
            "fingerprint_grouped_with_zero_train_validation_test_group_overlap"
        ),
        "known_only_fit_selection_calibration_and_threshold": True,
        "dataset_registry": registry,
        "tasks": tasks,
        "task_counts": {
            "datasets": 2,
            "attack_families": attack_count,
            "training_seeds": 3,
            "total_scenarios_per_algorithm": len(tasks),
            "LSNM2024": 45,
            "CICDDoS2019": 51,
        },
        "activation_gate": {
            "confirmation_summary_path": downstream_design[
                "activation_gate"
            ]["confirmation_summary_path"],
            "confirmation_audit_path": downstream_design["activation_gate"][
                "confirmation_audit_path"
            ],
            "confirmation_summary_passes": True,
            "confirmation_audit_passes": True,
            "confirmation_selection": "krc_csr_caeos_v1",
            "confirmation_audit_decision_matches_summary": True,
            "all_frozen_input_file_and_manifest_hashes_match": True,
            "otherwise": (
                "write_not_required_and_retain_caeos_pairwise"
            ),
        },
        "confirmation_gate": downstream_design[
            "fresh_external_malicious"
        ]["confirmation_gate"],
        "input_manifest_sha256": {
            "downstream_design": downstream_design["manifest_sha256"],
            "krc_confirmation_protocol": krc_protocol["manifest_sha256"],
            "preparation_protocol": preparation_protocol["manifest_sha256"],
            "readiness": readiness["manifest_sha256"],
        },
        "input_file_sha256": {
            "downstream_design": file_hash(downstream_design_path),
            "krc_confirmation_protocol": file_hash(krc_protocol_path),
            "preparation_protocol": file_hash(preparation_protocol_path),
            "preparation_summary": file_hash(preparation_summary_path),
            "readiness": file_hash(readiness_path),
        },
        "implementation_sha256": {
            creator_path.name: file_hash(creator_path)
        },
        "output_counts_at_freeze": zero_counts,
        "result_root": result_root.resolve().as_posix(),
        "claim_boundary": {
            "data_readiness_is_not_model_effect_evidence": True,
            "protocol_does_not_authorize_execution_before_krc_selection": True,
            "candidate_must_be_retrained_for_every_external_split": True,
            "source_confirmation_test_effects_cannot_select_parameters": True,
            "parrot_benign_safety_cannot_replace_malicious_external_tasks": True,
            "no_dataset_metric_seed_or_comparator_splicing": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--downstream-design", type=Path, required=True)
    parser.add_argument("--krc-protocol", type=Path, required=True)
    parser.add_argument("--preparation-protocol", type=Path, required=True)
    parser.add_argument("--preparation-summary", type=Path, required=True)
    parser.add_argument("--readiness", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_protocol(
        project_root=args.project_root.resolve(),
        data_root=args.data_root.resolve(),
        result_root=args.result_root.resolve(),
        downstream_design_path=args.downstream_design.resolve(),
        krc_protocol_path=args.krc_protocol.resolve(),
        preparation_protocol_path=args.preparation_protocol.resolve(),
        preparation_summary_path=args.preparation_summary.resolve(),
        readiness_path=args.readiness.resolve(),
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
