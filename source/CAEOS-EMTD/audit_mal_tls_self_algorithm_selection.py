from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rank_eligible(
    records: list[dict[str, Any]], priority: list[str]
) -> dict[str, Any] | None:
    eligible = [record for record in records if record["eligible"]]
    if not eligible:
        return None
    order = {name: len(priority) - index for index, name in enumerate(priority)}
    return max(
        eligible,
        key=lambda record: (
            record["selection_score"]["minimum_bootstrap_95ci_lower_bound"],
            record["selection_score"]["mean_four_metric_oriented_gain"],
            order[record["candidate"]],
        ),
    )


def candidate_record(
    *,
    candidate: str,
    pilot_analysis_path: Path,
    branch_root: Path,
    confirmation_protocol_path: Path,
    confirmation_analysis_path: Path,
    expected_confirmation_schema: str,
    expected_pilot_schema: str,
    expected_pilot_manifest_sha256: str,
    metrics: list[str],
) -> tuple[dict[str, Any], dict[str, str]]:
    if not (branch_root / "branch_complete").is_file():
        raise ValueError(f"self-algorithm branch is incomplete: {candidate}")
    pilot = load_json(pilot_analysis_path)
    if pilot.get("schema_version") != expected_pilot_schema:
        raise ValueError(f"unexpected pilot analysis schema: {candidate}")
    if pilot.get("protocol_manifest_sha256") != expected_pilot_manifest_sha256:
        raise ValueError(f"pilot analysis binding mismatch: {candidate}")
    hashes = {f"{candidate}_pilot_analysis": file_hash(pilot_analysis_path)}
    pilot_passes = pilot.get("passes") is True
    if not pilot_passes:
        not_required = branch_root / "not_required.json"
        if not not_required.is_file():
            raise ValueError(f"negative pilot lacks not-required evidence: {candidate}")
        not_required_payload = load_json(not_required)
        if not_required_payload.get("pilot_decision") != pilot.get("decision"):
            raise ValueError(f"not-required decision mismatch: {candidate}")
        hashes[f"{candidate}_not_required"] = file_hash(not_required)
        return (
            {
                "candidate": candidate,
                "pilot_passes": False,
                "confirmation_status": "not_required",
                "confirmation_passes": False,
                "eligible": False,
                "selection_score": None,
            },
            hashes,
        )
    if (
        not confirmation_protocol_path.is_file()
        or not confirmation_analysis_path.is_file()
        or not (confirmation_analysis_path.parent / "confirmation_complete").is_file()
    ):
        raise ValueError(f"positive pilot lacks confirmation evidence: {candidate}")
    confirmation_protocol = load_json(confirmation_protocol_path)
    if confirmation_protocol.get("manifest_sha256") != canonical_hash(
        confirmation_protocol
    ):
        raise ValueError(f"confirmation protocol SHA mismatch: {candidate}")
    if confirmation_protocol.get("selected_candidate") != candidate:
        raise ValueError(f"confirmation protocol candidate mismatch: {candidate}")
    confirmation = load_json(confirmation_analysis_path)
    if confirmation.get("schema_version") != expected_confirmation_schema:
        raise ValueError(f"unexpected confirmation analysis schema: {candidate}")
    if confirmation.get("protocol_manifest_sha256") != confirmation_protocol[
        "manifest_sha256"
    ]:
        raise ValueError(f"confirmation analysis binding mismatch: {candidate}")
    hashes[f"{candidate}_confirmation_protocol"] = file_hash(
        confirmation_protocol_path
    )
    hashes[f"{candidate}_confirmation_analysis"] = file_hash(
        confirmation_analysis_path
    )
    confirmation_passes = confirmation.get("passes") is True
    score = None
    if confirmation_passes:
        summaries = confirmation["metrics"]
        lower_bounds = [float(summaries[name]["bootstrap_95ci"][0]) for name in metrics]
        means = [float(summaries[name]["mean"]) for name in metrics]
        score = {
            "minimum_bootstrap_95ci_lower_bound": min(lower_bounds),
            "mean_four_metric_oriented_gain": sum(means) / len(means),
        }
    return (
        {
            "candidate": candidate,
            "pilot_passes": True,
            "confirmation_status": "complete",
            "confirmation_passes": confirmation_passes,
            "eligible": confirmation_passes,
            "selection_score": score,
        },
        hashes,
    )


def audit(args: argparse.Namespace) -> dict[str, Any]:
    protocol = load_json(args.protocol)
    if protocol.get("schema_version") != "mal_tls_self_algorithm_selection_protocol_v2":
        raise ValueError("unexpected self-algorithm selection protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("self-algorithm selection protocol SHA mismatch")
    if protocol["implementation_sha256"]["audit_mal_tls_self_algorithm_selection.py"] != file_hash(
        Path(__file__)
    ):
        raise ValueError("self-algorithm selection audit implementation drift")
    metrics = protocol["selection_rule"]["metrics"]
    geometry, geometry_hashes = candidate_record(
        candidate="mal_tls_geometry_preserving_adapter",
        pilot_analysis_path=args.geometry_pilot_analysis,
        branch_root=args.geometry_branch_root,
        confirmation_protocol_path=args.geometry_confirmation_protocol,
        confirmation_analysis_path=args.geometry_confirmation_analysis,
        expected_confirmation_schema=protocol[
            "candidate_confirmation_analysis_schema"
        ]["mal_tls_geometry_preserving_adapter"],
        expected_pilot_schema=protocol["candidate_pilot_analysis_schema"][
            "mal_tls_geometry_preserving_adapter"
        ],
        expected_pilot_manifest_sha256=protocol[
            "candidate_protocol_manifest_sha256"
        ]["mal_tls_geometry_preserving_adapter"],
        metrics=metrics,
    )
    counterfactual, counterfactual_hashes = candidate_record(
        candidate="mal_tls_counterfactual_conflict_gate",
        pilot_analysis_path=args.counterfactual_pilot_analysis,
        branch_root=args.counterfactual_branch_root,
        confirmation_protocol_path=args.counterfactual_confirmation_protocol,
        confirmation_analysis_path=args.counterfactual_confirmation_analysis,
        expected_confirmation_schema=protocol[
            "candidate_confirmation_analysis_schema"
        ]["mal_tls_counterfactual_conflict_gate"],
        expected_pilot_schema=protocol["candidate_pilot_analysis_schema"][
            "mal_tls_counterfactual_conflict_gate"
        ],
        expected_pilot_manifest_sha256=protocol[
            "candidate_protocol_manifest_sha256"
        ]["mal_tls_counterfactual_conflict_gate"],
        metrics=metrics,
    )
    records = [geometry, counterfactual]
    selected = rank_eligible(
        records, protocol["selection_rule"]["exact_tie_priority"]
    )
    result: dict[str, Any] = {
        "schema_version": "mal_tls_self_algorithm_selection_audit_v1",
        "status": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "input_file_sha256": {
            **geometry_hashes,
            **counterfactual_hashes,
        },
        "global_incumbent": "caeos_pairwise",
        "candidate_records": records,
        "selected_mal_tls_component": (
            selected["candidate"] if selected is not None else None
        ),
        "selection_score": (
            selected["selection_score"] if selected is not None else None
        ),
        "decision": (
            "retain_caeos_pairwise_without_confirmed_mal_tls_component"
            if selected is None
            else "retain_caeos_pairwise_with_selected_confirmed_mal_tls_component"
        ),
        "claim_boundary": protocol["claim_boundary"],
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--geometry-pilot-analysis", type=Path, required=True)
    parser.add_argument("--geometry-branch-root", type=Path, required=True)
    parser.add_argument("--geometry-confirmation-protocol", type=Path, required=True)
    parser.add_argument("--geometry-confirmation-analysis", type=Path, required=True)
    parser.add_argument("--counterfactual-pilot-analysis", type=Path, required=True)
    parser.add_argument("--counterfactual-branch-root", type=Path, required=True)
    parser.add_argument("--counterfactual-confirmation-protocol", type=Path, required=True)
    parser.add_argument("--counterfactual-confirmation-analysis", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "audit.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "audit_complete").touch()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
