import copy
import json
from pathlib import Path

import pytest

from create_strict_v4_classical_main_baseline_protocol import (
    MAIN_BASELINES,
    SOURCE_SUMMARY_SHA256,
    create_protocol,
    validate_source_summary,
)
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = (
    PROJECT_ROOT
    / "results"
    / "strict_v4_mahalanobis_pp_full102_seed7"
    / "summary.json"
)


def load_summary():
    return json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))


def test_protocol_freezes_exact_seven_baselines_from_authoritative_summary():
    summary = load_summary()
    protocol = create_protocol(
        summary,
        summary_path=SUMMARY_PATH,
        summary_file_sha256=file_hash(SUMMARY_PATH),
        implementation_sha256="a" * 64,
    )
    expected = [item["method"] for item in MAIN_BASELINES]
    assert protocol["main_table"]["baseline_count"] == 7
    assert protocol["main_table"]["method_order"] == expected
    assert protocol["comprehensive_appendix"]["method_count"] == 29
    assert protocol["source_evidence"]["scenario_count"] == 102
    assert protocol["source_evidence"]["artifact_checks"] == 612
    assert (
        protocol["self_algorithm_boundary"][
            "self_algorithm_results_must_not_change_main_baseline_membership"
        ]
        is True
    )
    assert protocol["manifest_sha256"] == canonical_hash(protocol)


def test_source_summary_sha_drift_is_rejected():
    with pytest.raises(ValueError, match="file SHA drifted"):
        validate_source_summary(load_summary(), "0" * 64)
    assert file_hash(SUMMARY_PATH) == SOURCE_SUMMARY_SHA256


def test_missing_selected_method_is_rejected_even_with_claimed_source_sha():
    summary = copy.deepcopy(load_summary())
    summary["overall"] = [
        row for row in summary["overall"] if row["method"] != "opendetect"
    ]
    summary["overall"].append(copy.deepcopy(summary["overall"][0]))
    summary["overall"][-1]["method"] = "replacement_method"
    with pytest.raises(ValueError, match="missing frozen main baselines"):
        validate_source_summary(summary, SOURCE_SUMMARY_SHA256)


def test_duplicate_method_row_is_rejected():
    summary = copy.deepcopy(load_summary())
    summary["overall"][-1] = copy.deepcopy(summary["overall"][0])
    with pytest.raises(ValueError, match="duplicate overall method row"):
        validate_source_summary(summary, SOURCE_SUMMARY_SHA256)
