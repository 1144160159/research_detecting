from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from external_dataset_protocol_utils import canonical_hash, file_hash, load_json


BENIGN_LABELS = {"normal", "BENIGN", "Benign", "benign"}
EXPECTED_UNREGISTERED_LABELS = {"UDP-lag", "WebDDoS"}


def _binding(path: Path) -> Dict[str, str]:
    return {"path": str(path.resolve()), "sha256": file_hash(path)}


def _member_evidence(member_scan_root: Path) -> list[Dict[str, Any]]:
    rows = []
    for path in sorted(member_scan_root.glob("*.json")):
        value = load_json(path)
        counts = value.get("label_counts", {})
        if any(label in counts for label in ("UDP-lag", "UDPLag", "WebDDoS")):
            rows.append(
                {
                    "member": value["member"],
                    "member_crc32": value["member_crc32"],
                    "member_uncompressed_size": int(
                        value["member_uncompressed_size"]
                    ),
                    "label_counts": {
                        label: int(counts[label])
                        for label in ("UDP-lag", "UDPLag", "WebDDoS")
                        if label in counts
                    },
                    "scan_file_sha256": file_hash(path),
                }
            )
    return rows


def _only_expected_failure(checks: Dict[str, Any]) -> bool:
    return bool(
        checks.get("no_unexpected_attack_labels") is False
        and all(
            value is True
            for name, value in checks.items()
            if name != "no_unexpected_attack_labels"
        )
    )


def create_protocol(
    *,
    expansion_path: Path,
    failed_audit_path: Path,
    member_scan_root: Path,
    reconciler_path: Path,
    preparer_path: Path,
    label_module_path: Path,
    reconciled_output_root: Path,
    prepared_output_root: Path,
) -> Dict[str, Any]:
    if (reconciled_output_root / "admission_audit.json").exists():
        raise ValueError("label protocol must be frozen before reconciled audit")
    if list(prepared_output_root.glob("*/manifest.json")):
        raise ValueError("label protocol must be frozen before v2 preparation")

    expansion = load_json(expansion_path)
    failed = load_json(failed_audit_path)
    if (
        expansion.get("schema_version")
        != "gpu_malicious_dataset_expansion_protocol_v1"
        or expansion.get("status") != "frozen_before_full_scan_and_training"
        or failed.get("schema_version")
        != "gpu_malicious_dataset_full_admission_audit_v1"
        or failed.get("status") != "complete"
        or failed.get("admission_passed") is not False
    ):
        raise ValueError("complete frozen v1 failure evidence required")
    if failed.get("datasets", {}).get("LSNM2024", {}).get(
        "admission_passed"
    ) is not True:
        raise ValueError("LSNM2024 must have passed the original full scan")

    cic = failed["datasets"]["CICDDoS2019"]
    if cic.get("admission_passed") is not False or not _only_expected_failure(
        cic["checks"]
    ):
        raise ValueError("CICDDoS2019 failure is not label-registry-only")
    expected = set(expansion["datasets"]["CICDDoS2019"]["families"])
    observed = set(cic["label_counts"]) - BENIGN_LABELS
    if observed - expected != EXPECTED_UNREGISTERED_LABELS:
        raise ValueError("unexpected CICDDoS2019 label discrepancy")
    if (
        int(cic["label_counts"].get("UDP-lag", 0)) != 366_461
        or int(cic["groups_by_label"].get("UDP-lag", 0)) != 366_461
        or int(cic["label_counts"].get("UDPLag", 0)) != 1_873
        or int(cic["groups_by_label"].get("UDPLag", 0)) != 1_873
        or int(cic["label_counts"].get("WebDDoS", 0)) != 439
        or int(cic["groups_by_label"].get("WebDDoS", 0)) != 439
    ):
        raise ValueError("CICDDoS2019 label discrepancy counts changed")

    evidence = _member_evidence(member_scan_root)
    alias_rows = [
        row
        for row in evidence
        if row["member"].endswith("01-12/UDPLag.csv")
        and row["label_counts"].get("UDP-lag") == 366_461
        and row["label_counts"].get("WebDDoS") == 439
    ]
    canonical_rows = [
        row
        for row in evidence
        if row["member"].endswith("03-11/UDPLag.csv")
        and row["label_counts"].get("UDPLag") == 1_873
    ]
    if len(alias_rows) != 1 or len(canonical_rows) != 1:
        raise ValueError("member-level label reconciliation evidence is incomplete")

    canonical_families = sorted(expected | {"WebDDoS"})
    protocol: Dict[str, Any] = {
        "schema_version": "gpu_dataset_label_reconciliation_protocol_v1",
        "status": "frozen_before_reconciled_audit_and_preparation",
        "execution_admitted": True,
        "source_identity": expansion["source_identity"],
        "source_sha256": failed["source_sha256"],
        "original_failure": {
            "audit_file_sha256": file_hash(failed_audit_path),
            "lsnm2024_passed": True,
            "cicddos2019_only_failed_check": (
                "no_unexpected_attack_labels"
            ),
            "model_metric_count": 0,
        },
        "reconciliation": {
            "dataset": "CICDDoS2019",
            "label_aliases": {"UDP-lag": "UDPLag"},
            "retained_new_families": ["WebDDoS"],
            "canonical_attack_families": canonical_families,
            "canonical_attack_family_count": len(canonical_families),
            "member_evidence": evidence,
            "row_count_preserved": True,
            "group_count_preserved": True,
            "model_feature_values_changed": False,
            "split_groups_changed": False,
        },
        "frozen_output_counts": {
            "reconciled_audit": 0,
            "prepared_manifests": 0,
            "model_metrics": 0,
        },
        "bindings": {
            "creator": _binding(Path(__file__).resolve()),
            "protocol_utils": _binding(
                Path(__file__).with_name(
                    "external_dataset_protocol_utils.py"
                ).resolve()
            ),
            "expansion_protocol": _binding(expansion_path),
            "failed_full_admission_audit": _binding(failed_audit_path),
            "reconciler": _binding(reconciler_path),
            "preparer": _binding(preparer_path),
            "label_module": _binding(label_module_path),
        },
        "claim_boundary": {
            "label_reconciliation_is_not_model_effect_evidence": True,
            "webddos_is_retained_instead_of_discarded": True,
            "unknown_or_test_metric_used": False,
            "krc_selection_or_threshold_changed": False,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def verify_protocol(protocol: Dict[str, Any]) -> None:
    if (
        protocol.get("schema_version")
        != "gpu_dataset_label_reconciliation_protocol_v1"
        or protocol.get("status")
        != "frozen_before_reconciled_audit_and_preparation"
        or protocol.get("execution_admitted") is not True
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or protocol.get("reconciliation", {}).get(
            "canonical_attack_family_count"
        )
        != 17
        or protocol.get("reconciliation", {}).get("label_aliases")
        != {"UDP-lag": "UDPLag"}
        or protocol.get("reconciliation", {}).get("retained_new_families")
        != ["WebDDoS"]
    ):
        raise ValueError("invalid label reconciliation protocol")
    for binding in protocol["bindings"].values():
        path = Path(binding["path"])
        if file_hash(path) != binding["sha256"]:
            raise ValueError(f"bound reconciliation input changed: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expansion-protocol", type=Path, required=True)
    parser.add_argument("--failed-audit", type=Path, required=True)
    parser.add_argument("--member-scan-root", type=Path, required=True)
    parser.add_argument("--reconciler", type=Path, required=True)
    parser.add_argument("--preparer", type=Path, required=True)
    parser.add_argument("--label-module", type=Path, required=True)
    parser.add_argument("--reconciled-output-root", type=Path, required=True)
    parser.add_argument("--prepared-output-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol = create_protocol(
        expansion_path=args.expansion_protocol.resolve(),
        failed_audit_path=args.failed_audit.resolve(),
        member_scan_root=args.member_scan_root.resolve(),
        reconciler_path=args.reconciler.resolve(),
        preparer_path=args.preparer.resolve(),
        label_module_path=args.label_module.resolve(),
        reconciled_output_root=args.reconciled_output_root.resolve(),
        prepared_output_root=args.prepared_output_root.resolve(),
    )
    verify_protocol(protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
