from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from create_gpu_dataset_expansion_protocol import central_directory_identity
from create_gpu_dataset_label_reconciliation_protocol import (
    verify_protocol as verify_reconciliation_protocol,
)
from create_gpu_external_preparation_protocol_v2 import (
    verify_protocol as verify_preparation_protocol,
)
from external_dataset_protocol_utils import canonical_hash, file_hash, load_json


SEEDS = ("223", "227", "229")


def prepared_dataset(
    *,
    data_root: Path,
    dataset: str,
    expected_label_count: int,
    admission_file_sha256: str,
    reconciliation_manifest_sha256: str,
) -> Dict[str, Any]:
    root = data_root / dataset
    manifest_path = root / "manifest.json"
    complete_path = root / "preparation_complete"
    if not manifest_path.is_file() or not complete_path.is_file():
        return {
            "dataset": dataset,
            "manifest_exists": manifest_path.is_file(),
            "complete_marker_exists": complete_path.is_file(),
            "seed_checks": {},
            "passes": False,
        }
    manifest = load_json(manifest_path)
    files = manifest.get("files", {})
    seed_checks = {}
    for seed in SEEDS:
        entry = files.get(seed, {})
        csv_path = root / f"seed{seed}.csv"
        sidecar_path = root / f"seed{seed}.csv.json"
        sidecar = (
            load_json(sidecar_path) if sidecar_path.is_file() else None
        )
        provenance = entry.get("provenance", {})
        labels = set(entry.get("label_counts", {}))
        label_check = len(labels) == expected_label_count
        if dataset == "CICDDoS2019":
            label_check = bool(
                label_check
                and "UDP-lag" not in labels
                and {"BENIGN", "UDPLag", "WebDDoS"} <= labels
            )
        else:
            label_check = bool(label_check and "normal" in labels)
        checks = {
            "csv_exists": csv_path.is_file(),
            "sidecar_exists": sidecar_path.is_file(),
            "sidecar_content_matches_manifest": sidecar == entry,
            "sidecar_passed": entry.get("passed") is True,
            "csv_sha256_matches": (
                csv_path.is_file()
                and entry.get("csv_sha256") == file_hash(csv_path)
            ),
            "expected_label_set_size_and_identity": label_check,
            "reconciled_admission_bound": (
                provenance.get("reconciled_admission_audit_sha256")
                == admission_file_sha256
            ),
            "label_protocol_bound": (
                provenance.get(
                    "label_reconciliation_protocol_manifest_sha256"
                )
                == reconciliation_manifest_sha256
            ),
        }
        seed_checks[seed] = {
            "checks": checks,
            "rows": entry.get("rows"),
            "label_count": len(labels),
            "passes": all(checks.values()),
        }
    checks = {
        "schema": (
            manifest.get("schema_version")
            == "gpu_external_prepared_dataset_manifest_v1"
        ),
        "dataset": manifest.get("dataset") == dataset,
        "manifest_passed": manifest.get("passed") is True,
        "three_seeds": set(files) == set(SEEDS),
        "all_seed_checks": all(
            value["passes"] for value in seed_checks.values()
        ),
    }
    return {
        "dataset": dataset,
        "manifest_exists": True,
        "manifest_file_sha256": file_hash(manifest_path),
        "complete_marker_exists": True,
        "seed_checks": seed_checks,
        "checks": checks,
        "passes": all(checks.values()),
    }


def audit(project_root: Path, dataset_root: Path) -> Dict[str, Any]:
    expansion_path = (
        project_root
        / "results/gpu_malicious_dataset_expansion_protocol_v1/protocol.json"
    )
    reconciliation_path = (
        project_root
        / "results/gpu_dataset_label_reconciliation_protocol_v1/protocol.json"
    )
    admission_path = (
        project_root
        / "results/gpu_dataset_reconciled_admission_audit_v2/admission_audit.json"
    )
    admission_marker = admission_path.parent / "admission_passed"
    preparation_path = (
        project_root
        / "results/gpu_external_dataset_preparation_protocol_v2/protocol.json"
    )
    preparation_summary_path = (
        project_root
        / "results/gpu_external_dataset_preparation_v2/summary.json"
    )
    preparation_complete_path = (
        project_root
        / "results/gpu_external_dataset_preparation_v2/preparation_complete"
    )
    external_design_path = (
        project_root
        / "results/gpu_external_dataset_evaluation_v1/design_protocol.json"
    )
    parrot_path = (
        project_root
        / "results/parrot2025_full_no_decryption_features_v1/protocol.json"
    )

    expansion = load_json(expansion_path)
    reconciliation = load_json(reconciliation_path)
    admission = load_json(admission_path)
    preparation = load_json(preparation_path)
    external_design = load_json(external_design_path)
    parrot = load_json(parrot_path)
    verify_reconciliation_protocol(reconciliation)
    verify_preparation_protocol(preparation)
    if (
        admission.get("schema_version")
        != "gpu_malicious_dataset_reconciled_admission_audit_v2"
        or admission.get("manifest_sha256") != canonical_hash(admission)
        or admission.get("admission_passed") is not True
        or not admission_marker.is_file()
        or external_design.get("manifest_sha256")
        != canonical_hash(external_design)
        or parrot.get("manifest_sha256") != canonical_hash(parrot)
    ):
        raise ValueError("canonical downstream v2 inputs required")

    raw_rows = []
    for expected in expansion["source_identity"]:
        path = Path(expected["path"])
        actual = central_directory_identity(path) if path.is_file() else None
        raw_rows.append(
            {
                "path": str(path),
                "exists": path.is_file(),
                "identity_matches": actual == expected,
            }
        )
    raw_external_passes = len(raw_rows) == 3 and all(
        row["identity_matches"] for row in raw_rows
    )

    prepared_root = dataset_root / "caeos_external_open_set_v2"
    admission_file_sha256 = file_hash(admission_path)
    prepared = {
        "LSNM2024": prepared_dataset(
            data_root=prepared_root,
            dataset="LSNM2024",
            expected_label_count=16,
            admission_file_sha256=admission_file_sha256,
            reconciliation_manifest_sha256=reconciliation[
                "manifest_sha256"
            ],
        ),
        "CICDDoS2019": prepared_dataset(
            data_root=prepared_root,
            dataset="CICDDoS2019",
            expected_label_count=18,
            admission_file_sha256=admission_file_sha256,
            reconciliation_manifest_sha256=reconciliation[
                "manifest_sha256"
            ],
        ),
    }
    prepared_passes = all(value["passes"] for value in prepared.values())

    summary = (
        load_json(preparation_summary_path)
        if preparation_summary_path.is_file()
        else None
    )
    summary_passes = bool(
        summary is not None
        and summary.get("schema_version")
        == "gpu_external_dataset_preparation_summary_v2"
        and summary.get("status") == "complete"
        and summary.get("protocol_manifest_sha256")
        == preparation["manifest_sha256"]
        and summary.get("ready_for_frozen_external_experiments") is True
        and all(
            summary.get("datasets", {})
            .get(name, {})
            .get("manifest_sha256")
            == prepared[name].get("manifest_file_sha256")
            for name in ("LSNM2024", "CICDDoS2019")
        )
        and preparation_complete_path.is_file()
    )

    parrot_root = dataset_root / "PARROT2025_mitmproxy"
    observed_pcaps = {
        path.name: path.stat().st_size
        for path in sorted(parrot_root.glob("*.pcap"))
    }
    expected_pcaps = {
        str(record["member"]).split("/", 1)[-1]: int(record["size_bytes"])
        for record in parrot["captures"]
    }
    parrot_passes = bool(
        observed_pcaps == expected_pcaps
        and parrot.get("capture_count") == 320
        and parrot.get("application_count") == 80
        and parrot.get("feature_count") == 56
        and parrot.get("safety_policy", {}).get("payload_decryption")
        is False
        and parrot.get("safety_policy", {}).get("training_use") is False
        and parrot.get("safety_policy", {}).get("threshold_selection_use")
        is False
    )
    checks = {
        "external_raw_archives_match_frozen_identity": raw_external_passes,
        "reconciled_full_admission_passes": True,
        "external_three_seed_preparation_passes": prepared_passes,
        "preparation_summary_and_marker_pass": summary_passes,
        "parrot_320_capture_56_feature_no_decryption_passes": parrot_passes,
    }
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_downstream_data_readiness_v2",
        "state": "read_only_snapshot",
        "raw_external_archives": raw_rows,
        "reconciled_admission": {
            "protocol_manifest_sha256": reconciliation["manifest_sha256"],
            "audit_manifest_sha256": admission["manifest_sha256"],
            "audit_file_sha256": admission_file_sha256,
            "passes": True,
            "cicddos_attack_family_count": 17,
        },
        "external_prepared": prepared,
        "preparation_summary": {
            "exists": preparation_summary_path.is_file(),
            "complete_marker_exists": preparation_complete_path.is_file(),
            "passes": summary_passes,
        },
        "parrot": {
            "raw_capture_count": len(observed_pcaps),
            "passes": parrot_passes,
        },
        "checks": checks,
        "raw_data_available": bool(raw_external_passes and parrot_passes),
        "ready_for_downstream_execution": all(checks.values()),
        "input_file_sha256": {
            "expansion_protocol": file_hash(expansion_path),
            "reconciliation_protocol": file_hash(reconciliation_path),
            "reconciled_admission_audit": admission_file_sha256,
            "preparation_protocol": file_hash(preparation_path),
            "external_design": file_hash(external_design_path),
            "parrot_feature_protocol": file_hash(parrot_path),
            "auditor": file_hash(Path(__file__)),
        },
        "claim_boundary": {
            "readiness_is_not_model_effect_evidence": True,
            "parrot_supports_benign_safety_only": True,
            "webddos_is_retained_as_attack_family": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = audit(args.project_root.resolve(), args.dataset_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
