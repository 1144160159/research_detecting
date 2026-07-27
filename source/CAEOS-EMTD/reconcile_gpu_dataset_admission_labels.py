from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
from typing import Any, Dict

from create_gpu_dataset_label_reconciliation_protocol import (
    BENIGN_LABELS,
    verify_protocol,
)
from external_dataset_protocol_utils import canonical_hash, file_hash, load_json


def _canonical_counts(
    counts: Dict[str, Any], aliases: Dict[str, str]
) -> Dict[str, int]:
    canonical: Counter[str] = Counter()
    for label, count in counts.items():
        canonical[aliases.get(label, label)] += int(count)
    return dict(sorted(canonical.items()))


def reconcile(
    protocol: Dict[str, Any],
    failed_audit: Dict[str, Any],
) -> Dict[str, Any]:
    verify_protocol(protocol)
    if (
        failed_audit.get("schema_version")
        != "gpu_malicious_dataset_full_admission_audit_v1"
        or failed_audit.get("status") != "complete"
        or failed_audit.get("admission_passed") is not False
    ):
        raise ValueError("complete failed v1 audit required")
    if (
        file_hash(Path(protocol["bindings"]["failed_full_admission_audit"]["path"]))
        != protocol["bindings"]["failed_full_admission_audit"]["sha256"]
    ):
        raise ValueError("failed audit changed after reconciliation freeze")

    aliases = protocol["reconciliation"]["label_aliases"]
    expected = set(protocol["reconciliation"]["canonical_attack_families"])
    cic_source = failed_audit["datasets"]["CICDDoS2019"]
    cic = dict(cic_source)
    cic["label_counts"] = _canonical_counts(
        cic_source["label_counts"], aliases
    )
    cic["groups_by_label"] = _canonical_counts(
        cic_source["groups_by_label"], aliases
    )
    attacks = set(cic["label_counts"]) - BENIGN_LABELS
    checks = dict(cic_source["checks"])
    checks["no_unexpected_attack_labels"] = attacks <= expected
    checks["all_expected_attack_families_observed"] = expected <= attacks
    checks["canonical_attack_family_set_matches"] = attacks == expected
    checks["alias_rows_preserved"] = (
        int(cic["label_counts"]["UDPLag"]) == 368_334
    )
    checks["webddos_retained"] = (
        int(cic["label_counts"]["WebDDoS"]) == 439
        and int(cic["groups_by_label"]["WebDDoS"]) == 439
    )
    cic["checks"] = checks
    cic["admission_passed"] = all(checks.values())
    cic["raw_label_counts_before_reconciliation"] = cic_source[
        "label_counts"
    ]
    cic["raw_groups_by_label_before_reconciliation"] = cic_source[
        "groups_by_label"
    ]

    lsnm = failed_audit["datasets"]["LSNM2024"]
    source_hash_checks = {
        path: file_hash(Path(path)) == expected_hash
        for path, expected_hash in protocol["source_sha256"].items()
    }
    top_checks = {
        "protocol_and_bindings_valid": True,
        "source_full_sha256_unchanged": all(source_hash_checks.values()),
        "lsnm_original_full_admission_passed": (
            lsnm.get("admission_passed") is True
        ),
        "cicddos_reconciled_full_admission_passed": (
            cic["admission_passed"] is True
        ),
        "total_rows_preserved": (
            int(lsnm["rows"]) + int(cic["rows"])
            == int(failed_audit["datasets"]["LSNM2024"]["rows"])
            + int(failed_audit["datasets"]["CICDDoS2019"]["rows"])
        ),
    }
    value: Dict[str, Any] = {
        "schema_version": (
            "gpu_malicious_dataset_reconciled_admission_audit_v2"
        ),
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "original_failed_audit_file_sha256": protocol["bindings"][
            "failed_full_admission_audit"
        ]["sha256"],
        "source_sha256": protocol["source_sha256"],
        "source_sha256_checks": source_hash_checks,
        "datasets": {"LSNM2024": lsnm, "CICDDoS2019": cic},
        "checks": top_checks,
        "admission_passed": all(top_checks.values()),
        "formal_selection_evidence": False,
        "model_metric_count": 0,
        "next_step": (
            "freeze_and_run_three_seed_preparation_v2"
            if all(top_checks.values())
            else "stop_before_preparation"
        ),
        "claim_boundary": protocol["claim_boundary"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--failed-audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = load_json(args.protocol)
    failed = load_json(args.failed_audit)
    value = reconcile(protocol, failed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    temporary = args.output_dir / "admission_audit.json.tmp"
    output = args.output_dir / "admission_audit.json"
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output)
    (args.output_dir / "audit_complete").touch()
    if value["admission_passed"]:
        (args.output_dir / "admission_passed").touch()
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
