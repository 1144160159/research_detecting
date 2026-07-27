import copy
import json
from pathlib import Path

import pytest

from audit_strict_v4_incumbent_vs_main_baselines import (
    CLASSICAL_PROTOCOL_FILE_SHA256,
    FINAL_DECISION_FILE_SHA256,
    FULL102_SUMMARY_FILE_SHA256,
    OPTIMAL_DECISION_FILE_SHA256,
    create_audit,
    validate_sources,
)
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "full102": ROOT / "results/strict_v4_full103_seed7/summary.json",
    "classical": (
        ROOT
        / "results/strict_v4_classical_main_baseline_protocol_v1/protocol.json"
    ),
    "final": ROOT / "results/strict_v4_final_algorithm/decision.json",
    "optimal": ROOT / "results/strict_v4_optimal_self_algorithm/decision.json",
}


def sources():
    return {
        key: json.loads(path.read_text(encoding="utf-8"))
        for key, path in PATHS.items()
    }


def validation_arguments(values):
    return {
        "full102": values["full102"],
        "full102_file_sha256": FULL102_SUMMARY_FILE_SHA256,
        "classical": values["classical"],
        "classical_file_sha256": CLASSICAL_PROTOCOL_FILE_SHA256,
        "final_decision": values["final"],
        "final_decision_file_sha256": FINAL_DECISION_FILE_SHA256,
        "optimal_decision": values["optimal"],
        "optimal_decision_file_sha256": OPTIMAL_DECISION_FILE_SHA256,
    }


def test_audit_quantifies_pairwise_against_exact_seven_main_baselines():
    values = sources()
    audit = create_audit(
        **validation_arguments(values),
        full102_path=PATHS["full102"],
        classical_path=PATHS["classical"],
        final_decision_path=PATHS["final"],
        optimal_decision_path=PATHS["optimal"],
        implementation_sha256="a" * 64,
    )
    assert audit["summary"]["baseline_count"] == 7
    assert audit["summary"]["opendetect_win_count"] == 4
    assert audit["summary"]["opendetect_loss_metrics"] == ["unknown_fpr95"]
    assert audit["summary"]["strict_five_metric_dominance_count"] == 3
    assert (
        audit["unconfirmed_development_challenger"][
            "must_not_replace_incumbent"
        ]
        is True
    )
    assert audit["manifest_sha256"] == canonical_hash(audit)


def test_all_authoritative_input_file_hashes_match_frozen_constants():
    assert file_hash(PATHS["full102"]) == FULL102_SUMMARY_FILE_SHA256
    assert file_hash(PATHS["classical"]) == CLASSICAL_PROTOCOL_FILE_SHA256
    assert file_hash(PATHS["final"]) == FINAL_DECISION_FILE_SHA256
    assert file_hash(PATHS["optimal"]) == OPTIMAL_DECISION_FILE_SHA256


def test_full102_file_sha_drift_is_rejected():
    values = sources()
    arguments = validation_arguments(values)
    arguments["full102_file_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="full102 summary file SHA drifted"):
        validate_sources(**arguments)


def test_cross_summary_metric_mismatch_is_rejected():
    values = sources()
    classical = copy.deepcopy(values["classical"])
    baseline = next(
        item
        for item in classical["main_table"]["baselines"]
        if item["method"] == "opendetect"
    )
    baseline["overall_evidence"]["unknown_auroc"] += 0.01
    classical["manifest_sha256"] = canonical_hash(classical)
    values["classical"] = classical
    with pytest.raises(ValueError, match="cross-summary metric mismatch"):
        validate_sources(**validation_arguments(values))
