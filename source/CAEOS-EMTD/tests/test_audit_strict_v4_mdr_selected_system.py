from copy import deepcopy

from create_strict_v4_external_confirmation_protocol import canonical_hash
from audit_strict_v4_mdr_selected_system import evaluate_audit


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def values(efficiency=True):
    protocol = canonical(
        {"schema_version": "strict_v4_mdr_selected_system_protocol_v1"}
    )
    recomputed = {
        "benchmark_count": 306,
        "scenario_block_count": 102,
        "failure_count": 0,
        "scenario_blocks": [],
        "raw_per_capture_ratios": [],
        "ratio_inference": {},
        "suite_equal_secondary_summary": {},
        "resource_reporting": {},
        "deployability_decision": {"passes": True},
        "strict_efficiency_decision": {"passes": efficiency},
        "_records": [
            {
                "unknown_or_test_labels_used_for_benchmark_selection": (
                    False
                )
            }
        ],
    }
    summary = canonical(
        {
            "schema_version": "strict_v4_mdr_selected_system_summary_v1",
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            **{
                key: value
                for key, value in recomputed.items()
                if key != "_records"
            },
        }
    )
    return protocol, summary, recomputed


def test_audit_separates_deployability_and_efficiency():
    protocol, summary, recomputed = values(efficiency=False)
    result = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=True,
        benchmark_hashes_match=True,
    )
    assert result["passes"] is True
    assert result["deployability_gate_passes"] is True
    assert result["strict_efficiency_superiority_gate_passes"] is False
    assert (
        result["claim_tiers"]["multidimensional_comprehensive_sota_supported"]
        is False
    )


def test_audit_rejects_recomputation_drift():
    protocol, summary, recomputed = values()
    drifted = deepcopy(recomputed)
    drifted["benchmark_count"] = 305
    result = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=drifted,
        implementation_hashes_match=True,
        benchmark_hashes_match=True,
    )
    assert result["passes"] is False


def test_audit_passes_all_claim_tiers_when_all_gates_pass():
    protocol, summary, recomputed = values()
    result = evaluate_audit(
        protocol=protocol,
        summary=summary,
        recomputed=recomputed,
        implementation_hashes_match=True,
        benchmark_hashes_match=True,
    )
    assert result["passes"] is True
    assert result["strict_efficiency_superiority_gate_passes"] is True
    assert (
        result["claim_tiers"]["multidimensional_comprehensive_sota_supported"]
        is True
    )
