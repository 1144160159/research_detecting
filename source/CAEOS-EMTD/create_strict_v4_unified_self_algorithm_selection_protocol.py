from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_protocol(
    *,
    pairwise_manifest: dict[str, Any],
    mal_tls_selection_protocol: dict[str, Any],
    ctc_pilot_protocol: dict[str, Any],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_decisions: int,
) -> dict[str, Any]:
    if observed_decisions != 0:
        raise ValueError("unified selection protocol must freeze before decisions")
    expected = (
        (pairwise_manifest, "strict_v4_boundary_pairwise_candidate_v1"),
        (mal_tls_selection_protocol, "mal_tls_self_algorithm_selection_protocol_v2"),
        (ctc_pilot_protocol, "strict_v4_conflict_topology_copula_protocol_v1"),
    )
    for payload, schema in expected:
        if payload.get("schema_version") != schema:
            raise ValueError(f"unexpected unified-selection input schema: {schema}")
        if payload.get("manifest_sha256") != canonical_hash(payload):
            raise ValueError(f"unified-selection input SHA mismatch: {schema}")
    if ctc_pilot_protocol.get("metrics_observed_at_freeze") != 0:
        raise ValueError("CTC pilot protocol was not result-free")
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_unified_self_algorithm_selection_protocol_v1",
        "status": "frozen_before_new_self_algorithm_results",
        "global_incumbent": "caeos_pairwise",
        "global_challenger": "caeos_conflict_topology_copula",
        "pairwise_candidate_manifest_sha256": pairwise_manifest["manifest_sha256"],
        "mal_tls_selection_protocol_manifest_sha256": mal_tls_selection_protocol[
            "manifest_sha256"
        ],
        "ctc_pilot_protocol_manifest_sha256": ctc_pilot_protocol["manifest_sha256"],
        "expected_schemas": {
            "mal_tls_selection_audit": "mal_tls_self_algorithm_selection_audit_v1",
            "ctc_pilot_analysis": "strict_v4_conflict_topology_copula_analysis_v1",
            "ctc_confirmation_protocol": (
                "strict_v4_conflict_topology_copula_confirmation_protocol_v1"
            ),
            "ctc_confirmation_analysis": (
                "strict_v4_conflict_topology_copula_confirmation_v1"
            ),
        },
        "selection_rule": {
            "global_accuracy_algorithm": (
                "select CTC only when its pilot and reserved-seed confirmation both pass; "
                "otherwise retain Pairwise"
            ),
            "mal_tls_component": (
                "inherit only the confirmed component selected by the frozen Mal_TLS audit"
            ),
            "result_dependent_ensembling_forbidden": True,
            "ctc_accuracy_pass_does_not_imply_deployment_pass": True,
        },
        "deployment_gates": {
            "ctc_if_accuracy_selected": [
                "isolated_efficiency_and_resource_gate",
                "LSNM2024_external_open_set_gate",
                "CICDDoS2019_external_family_gate",
            ],
            "pairwise_if_retained": [
                "optimized_efficiency_v6",
                "external_dataset_gates",
            ],
        },
        "claim_boundary": {
            "accuracy_selection_is_not_final_deployment_selection": True,
            "mal_tls_component_is_dataset_specific": True,
            "unknown_or_test_labels_used_for_runtime_selection": False,
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "decisions_observed_at_freeze": 0,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairwise-manifest", type=Path, required=True)
    parser.add_argument("--mal-tls-selection-protocol", type=Path, required=True)
    parser.add_argument("--ctc-pilot-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = {
        "pairwise_manifest": args.pairwise_manifest,
        "mal_tls_selection_protocol": args.mal_tls_selection_protocol,
        "ctc_pilot_protocol": args.ctc_pilot_protocol,
    }
    implementations = (
        "create_strict_v4_unified_self_algorithm_selection_protocol.py",
        "select_strict_v4_unified_self_algorithm.py",
        "scripts/wait_and_select_strict_v4_unified_self_algorithm.sh",
    )
    protocol = create_protocol(
        pairwise_manifest=json.loads(args.pairwise_manifest.read_text(encoding="utf-8")),
        mal_tls_selection_protocol=json.loads(
            args.mal_tls_selection_protocol.read_text(encoding="utf-8")
        ),
        ctc_pilot_protocol=json.loads(args.ctc_pilot_protocol.read_text(encoding="utf-8")),
        input_file_sha256={name: file_hash(path) for name, path in sources.items()},
        implementation_sha256={
            name: file_hash(args.project_root / name) for name in implementations
        },
        observed_decisions=int(args.output.is_file()),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
