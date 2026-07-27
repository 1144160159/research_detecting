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
    geometry_protocol: dict[str, Any],
    counterfactual_protocol: dict[str, Any],
    *,
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_confirmation_analyses: int,
) -> dict[str, Any]:
    expected = (
        (geometry_protocol, "mal_tls_geometry_preserving_adapter_protocol_v1"),
        (
            counterfactual_protocol,
            "mal_tls_counterfactual_conflict_gate_protocol_v1",
        ),
    )
    for payload, schema in expected:
        if payload.get("schema_version") != schema:
            raise ValueError(f"unexpected self-algorithm protocol schema: {schema}")
        if payload.get("manifest_sha256") != canonical_hash(payload):
            raise ValueError(f"self-algorithm protocol SHA mismatch: {schema}")
        if payload.get("metrics_observed_at_freeze") != 0:
            raise ValueError("self-algorithm pilot protocol was not result-free")
    if observed_confirmation_analyses != 0:
        raise ValueError("selection protocol must freeze before confirmation analyses")
    protocol: dict[str, Any] = {
        "schema_version": "mal_tls_self_algorithm_selection_protocol_v2",
        "status": "frozen_before_pilot_and_confirmation_results",
        "global_incumbent": "caeos_pairwise",
        "candidate_protocol_manifest_sha256": {
            "mal_tls_geometry_preserving_adapter": geometry_protocol[
                "manifest_sha256"
            ],
            "mal_tls_counterfactual_conflict_gate": counterfactual_protocol[
                "manifest_sha256"
            ],
        },
        "candidate_confirmation_analysis_schema": {
            "mal_tls_geometry_preserving_adapter": (
                "mal_tls_geometry_adapter_confirmation_analysis_v1"
            ),
            "mal_tls_counterfactual_conflict_gate": (
                "mal_tls_counterfactual_conflict_gate_confirmation_analysis_v1"
            ),
        },
        "candidate_pilot_analysis_schema": {
            "mal_tls_geometry_preserving_adapter": (
                "mal_tls_geometry_preserving_adapter_analysis_v1"
            ),
            "mal_tls_counterfactual_conflict_gate": (
                "mal_tls_counterfactual_conflict_gate_analysis_v1"
            ),
        },
        "eligibility": {
            "pilot_gate_must_pass": True,
            "reserved_seed_confirmation_gate_must_pass": True,
            "development_only_candidate_cannot_be_selected": True,
        },
        "selection_rule": {
            "primary": "maximize_minimum_four_metric_bootstrap_95ci_lower_bound",
            "secondary": "maximize_mean_of_four_metric_mean_oriented_gains",
            "exact_tie_priority": [
                "mal_tls_geometry_preserving_adapter",
                "mal_tls_counterfactual_conflict_gate",
            ],
            "metrics": ["unknown_auroc", "unknown_aupr", "unknown_fpr95", "oscr"],
            "result_dependent_ensembling_forbidden": True,
        },
        "claim_boundary": {
            "selected_component_applies_to_mal_tls_only": True,
            "global_incumbent_remains_caeos_pairwise": True,
            "no_component_selected_when_no_confirmation_passes": True,
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "confirmation_analyses_observed_at_freeze": observed_confirmation_analyses,
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry-protocol", type=Path, required=True)
    parser.add_argument("--counterfactual-protocol", type=Path, required=True)
    parser.add_argument("--geometry-confirmation-analysis", type=Path, required=True)
    parser.add_argument("--counterfactual-confirmation-analysis", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    geometry = json.loads(args.geometry_protocol.read_text(encoding="utf-8"))
    counterfactual = json.loads(args.counterfactual_protocol.read_text(encoding="utf-8"))
    observed = sum(
        path.is_file()
        for path in (
            args.geometry_confirmation_analysis,
            args.counterfactual_confirmation_analysis,
        )
    )
    implementations = {
        name: file_hash(args.project_root / name)
        for name in (
            "create_mal_tls_self_algorithm_selection_protocol.py",
            "audit_mal_tls_self_algorithm_selection.py",
        )
    }
    protocol = create_protocol(
        geometry,
        counterfactual,
        input_file_sha256={
            "geometry_protocol": file_hash(args.geometry_protocol),
            "counterfactual_protocol": file_hash(args.counterfactual_protocol),
        },
        implementation_sha256=implementations,
        observed_confirmation_analyses=int(observed),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(protocol["manifest_sha256"])


if __name__ == "__main__":
    main()
