from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


PAIRWISE = "caeos_pairwise"
CTC = "caeos_conflict_topology_copula"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_canonical(payload: dict[str, Any], schema: str, name: str) -> None:
    if payload.get("schema_version") != schema:
        raise ValueError(f"unexpected {name} schema")
    if payload.get("manifest_sha256") != canonical_hash(payload):
        raise ValueError(f"{name} SHA mismatch")


def select_unified(
    *,
    protocol: dict[str, Any],
    pairwise_manifest: dict[str, Any],
    mal_tls_audit: dict[str, Any],
    ctc_pilot: dict[str, Any],
    ctc_branch_complete: bool,
    ctc_not_required: dict[str, Any] | None,
    ctc_confirmation_protocol: dict[str, Any] | None,
    ctc_confirmation: dict[str, Any] | None,
) -> dict[str, Any]:
    _validate_canonical(
        protocol,
        "strict_v4_unified_self_algorithm_selection_protocol_v1",
        "unified selection protocol",
    )
    _validate_canonical(
        pairwise_manifest,
        "strict_v4_boundary_pairwise_candidate_v1",
        "Pairwise manifest",
    )
    if pairwise_manifest["manifest_sha256"] != protocol[
        "pairwise_candidate_manifest_sha256"
    ]:
        raise ValueError("Pairwise manifest binding mismatch")
    _validate_canonical(
        mal_tls_audit,
        protocol["expected_schemas"]["mal_tls_selection_audit"],
        "Mal_TLS selection audit",
    )
    if mal_tls_audit.get("protocol_manifest_sha256") != protocol[
        "mal_tls_selection_protocol_manifest_sha256"
    ]:
        raise ValueError("Mal_TLS selection audit binding mismatch")
    if not ctc_branch_complete:
        raise ValueError("CTC confirmation branch is incomplete")
    if ctc_pilot.get("schema_version") != protocol["expected_schemas"][
        "ctc_pilot_analysis"
    ]:
        raise ValueError("unexpected CTC pilot analysis schema")
    if ctc_pilot.get("protocol_manifest_sha256") != protocol[
        "ctc_pilot_protocol_manifest_sha256"
    ]:
        raise ValueError("CTC pilot analysis binding mismatch")

    pilot_passes = (
        ctc_pilot.get("passes") is True
        and ctc_pilot.get("decision") == "freeze_for_reserved_seed_confirmation"
    )
    confirmation_passes = False
    confirmation_status = "not_required"
    if pilot_passes:
        if ctc_confirmation_protocol is None or ctc_confirmation is None:
            raise ValueError("positive CTC pilot lacks reserved-seed confirmation")
        _validate_canonical(
            ctc_confirmation_protocol,
            protocol["expected_schemas"]["ctc_confirmation_protocol"],
            "CTC confirmation protocol",
        )
        if ctc_confirmation_protocol.get("pilot_protocol_manifest_sha256") != protocol[
            "ctc_pilot_protocol_manifest_sha256"
        ]:
            raise ValueError("CTC confirmation protocol pilot binding mismatch")
        if ctc_confirmation.get("schema_version") != protocol["expected_schemas"][
            "ctc_confirmation_analysis"
        ]:
            raise ValueError("unexpected CTC confirmation analysis schema")
        if ctc_confirmation.get("protocol_manifest_sha256") != ctc_confirmation_protocol[
            "manifest_sha256"
        ]:
            raise ValueError("CTC confirmation analysis binding mismatch")
        confirmation_status = "complete"
        confirmation_passes = ctc_confirmation.get("passes") is True
    else:
        if ctc_not_required is None:
            raise ValueError("negative CTC pilot lacks not-required evidence")
        if ctc_not_required.get("pilot_decision") != ctc_pilot.get("decision"):
            raise ValueError("CTC not-required decision mismatch")

    selected = CTC if confirmation_passes else PAIRWISE
    component = mal_tls_audit.get("selected_mal_tls_component")
    deployment_status = (
        "pending_ctc_efficiency_and_external_dataset_gates"
        if selected == CTC
        else "pending_pairwise_efficiency_and_external_dataset_gates"
    )
    result: dict[str, Any] = {
        "schema_version": "strict_v4_unified_self_algorithm_accuracy_decision_v1",
        "status": "accuracy_selection_complete_deployment_pending",
        "selection_protocol_manifest_sha256": protocol["manifest_sha256"],
        "global_incumbent": PAIRWISE,
        "global_challenger": CTC,
        "ctc_pilot_passes": pilot_passes,
        "ctc_confirmation_status": confirmation_status,
        "ctc_confirmation_passes": confirmation_passes,
        "selected_global_accuracy_algorithm": selected,
        "selected_mal_tls_component": component,
        "composed_accuracy_candidate": {
            "global_base": selected,
            "mal_tls_component": component,
        },
        "deployment_status": deployment_status,
        "deployment_selection_complete": False,
        "remaining_deployment_gates": protocol["deployment_gates"][
            "ctc_if_accuracy_selected" if selected == CTC else "pairwise_if_retained"
        ],
        "claim_boundary": protocol["claim_boundary"],
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--pairwise-manifest", type=Path, required=True)
    parser.add_argument("--mal-tls-audit", type=Path, required=True)
    parser.add_argument("--ctc-pilot-analysis", type=Path, required=True)
    parser.add_argument("--ctc-branch-root", type=Path, required=True)
    parser.add_argument("--ctc-confirmation-protocol", type=Path, required=True)
    parser.add_argument("--ctc-confirmation-analysis", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    for name, expected in protocol["implementation_sha256"].items():
        path = args.protocol.resolve().parents[2] / name
        if file_hash(path) != expected:
            raise ValueError(f"unified selection implementation drift: {name}")
    not_required_path = args.ctc_branch_root / "not_required.json"
    result = select_unified(
        protocol=protocol,
        pairwise_manifest=json.loads(args.pairwise_manifest.read_text(encoding="utf-8")),
        mal_tls_audit=json.loads(args.mal_tls_audit.read_text(encoding="utf-8")),
        ctc_pilot=json.loads(args.ctc_pilot_analysis.read_text(encoding="utf-8")),
        ctc_branch_complete=(args.ctc_branch_root / "branch_complete").is_file(),
        ctc_not_required=(
            json.loads(not_required_path.read_text(encoding="utf-8"))
            if not_required_path.is_file()
            else None
        ),
        ctc_confirmation_protocol=(
            json.loads(args.ctc_confirmation_protocol.read_text(encoding="utf-8"))
            if args.ctc_confirmation_protocol.is_file()
            else None
        ),
        ctc_confirmation=(
            json.loads(args.ctc_confirmation_analysis.read_text(encoding="utf-8"))
            if args.ctc_confirmation_analysis.is_file()
            else None
        ),
    )
    result["input_file_sha256"] = {
        "protocol": file_hash(args.protocol),
        "pairwise_manifest": file_hash(args.pairwise_manifest),
        "mal_tls_audit": file_hash(args.mal_tls_audit),
        "ctc_pilot_analysis": file_hash(args.ctc_pilot_analysis),
        "ctc_not_required": file_hash(not_required_path) if not_required_path.is_file() else None,
        "ctc_confirmation_protocol": (
            file_hash(args.ctc_confirmation_protocol)
            if args.ctc_confirmation_protocol.is_file()
            else None
        ),
        "ctc_confirmation_analysis": (
            file_hash(args.ctc_confirmation_analysis)
            if args.ctc_confirmation_analysis.is_file()
            else None
        ),
    }
    result["selector_implementation_sha256"] = file_hash(Path(__file__))
    result["manifest_sha256"] = canonical_hash(result)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "accuracy_decision.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "accuracy_decision_complete").touch()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
