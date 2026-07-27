from __future__ import annotations

import copy

import pytest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_medaf_tabular_design import (
    create_design,
    select_scenarios,
)


def fixtures():
    audit = {
        "schema_version": "strict_v4_medaf_baseline_admission_audit_v2",
        "decision": {
            "official_source_snapshot_admitted": True,
            "native_medaf_strict_v4_execution_admitted": False,
            "named_tabular_adapter_candidate": True,
        },
    }
    audit["manifest_sha256"] = canonical_hash(audit)
    coverage = {
        "schema_version": "strict_v4_coverage_manifest_v2",
        "scenario_registry": {
            f"suite_{index}": {
                "scenarios": [
                    f"scenario_{index}_{scenario}"
                    for scenario in range(4)
                ]
            }
            for index in range(7)
        },
    }
    coverage["manifest_sha256"] = canonical_hash(coverage)
    return audit, coverage


def test_design_is_deterministic_zero_result_and_42_reports() -> None:
    audit, coverage = fixtures()
    first = create_design(
        audit,
        coverage,
        input_file_sha256={"audit": "a", "coverage": "b"},
        implementation_sha256={"model": "c", "trainer": "d"},
        result_count_at_freeze=0,
    )
    second = create_design(
        audit,
        coverage,
        input_file_sha256={"audit": "a", "coverage": "b"},
        implementation_sha256={"model": "c", "trainer": "d"},
        result_count_at_freeze=0,
    )
    assert first == second
    assert first["pilot"]["suite_count"] == 7
    assert first["pilot"]["scenario_count"] == 14
    assert first["pilot"]["expected_reports"] == 42
    assert first["execution_boundary"]["pilot_execution_admitted"] is False
    assert first["candidate_result_count_at_freeze"] == 0
    assert first["manifest_sha256"] == canonical_hash(first)


def test_selection_uses_manifest_and_commit_not_effect_values() -> None:
    _, coverage = fixtures()
    first = select_scenarios(coverage)
    changed = copy.deepcopy(coverage)
    changed["manifest_sha256"] = "different-coverage"
    second = select_scenarios(changed)
    assert first != second
    assert all(len(values) == 2 for values in first.values())


def test_design_rejects_results_or_native_admission() -> None:
    audit, coverage = fixtures()
    with pytest.raises(ValueError, match="zero model results"):
        create_design(
            audit,
            coverage,
            input_file_sha256={},
            implementation_sha256={},
            result_count_at_freeze=1,
        )
    native = copy.deepcopy(audit)
    native["decision"]["native_medaf_strict_v4_execution_admitted"] = True
    native["manifest_sha256"] = canonical_hash(native)
    with pytest.raises(ValueError, match="admission audit"):
        create_design(
            native,
            coverage,
            input_file_sha256={},
            implementation_sha256={},
            result_count_at_freeze=0,
        )
