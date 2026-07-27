from __future__ import annotations

import copy

from audit_strict_v4_comp_cross_suite_confirmation import build_audit
from create_strict_v4_external_confirmation_protocol import canonical_hash
from test_strict_v4_comp_cross_suite_summary import (
    protocol,
    records,
    summarize,
)


def hashes(rows):
    return {
        f"task_{index}": f"{index + 1:064x}"
        for index in range(len(rows))
    }


def audit(value, summary, rows):
    return build_audit(
        protocol=value,
        summary=summary,
        records=rows,
        task_record_sha256=hashes(rows),
        input_file_sha256={"protocol": "a" * 64, "summary": "b" * 64},
        auditor_sha256="c" * 64,
    )


def test_audit_independently_reconciles_positive_summary() -> None:
    value = protocol()
    rows = records(value)
    summary = summarize(value, rows)
    result = audit(value, summary, rows)

    assert result["integrity"]["passes"] is True
    assert result["effect"]["passes"] is True
    assert result["selection"]["selected_algorithm"] == "caeos_comp"
    assert result["manifest_sha256"] == canonical_hash(result)


def test_audit_accepts_scientifically_negative_complete_result() -> None:
    value = protocol()
    rows = records(value)
    rows = copy.deepcopy(rows)
    rows[0]["evaluation"]["caeos_comp"]["unknown_fpr95"] = 0.60
    rows[0]["manifest_sha256"] = canonical_hash(rows[0])
    summary = summarize(value, rows)
    result = audit(value, summary, rows)

    assert result["integrity"]["passes"] is True
    assert result["effect"]["passes"] is False
    assert result["selection"]["selected_algorithm"] == "pairwise"


def test_audit_detects_recanonicalized_decision_tampering() -> None:
    value = protocol()
    rows = records(value)
    summary = summarize(value, rows)
    summary = copy.deepcopy(summary)
    summary["decision"]["passes"] = False
    summary["manifest_sha256"] = canonical_hash(summary)
    result = audit(value, summary, rows)

    assert result["integrity"]["passes"] is False
    assert (
        result["integrity"]["checks"][
            "decision_checks_independently_reconcile"
        ]
        is False
    )
    assert result["selection"]["selected_algorithm"] == "pairwise"


def test_audit_detects_task_file_hash_mismatch() -> None:
    value = protocol()
    rows = records(value)
    summary = summarize(value, rows)
    summary = copy.deepcopy(summary)
    summary["input_evidence"]["task_record_sha256"]["task_0"] = "f" * 64
    summary["manifest_sha256"] = canonical_hash(summary)
    result = audit(value, summary, rows)

    assert result["integrity"]["passes"] is False
    assert result["integrity"]["checks"]["task_file_sha_binding"] is False
