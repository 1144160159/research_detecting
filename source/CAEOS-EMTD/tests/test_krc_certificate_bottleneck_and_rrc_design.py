from __future__ import annotations

import json
from pathlib import Path

from audit_krc_known_certificate_bottleneck import (
    clopper_pearson_upper,
    summarize_records,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_rrc_csr_fallback_design import create_design


def record(
    identity: str,
    seed: int,
    auroc: float,
    *,
    active: int = 0,
    trials: int = 2500,
) -> dict:
    return {
        "identity": identity,
        "training_seed": seed,
        "known_class_count": 32,
        "calibration_known_macro_f1": 0.62,
        "calibration_error_detection_auroc": auroc,
        "source_safety_active_rate": active / trials,
        "source_safety_active_rate_upper_95pct": (
            clopper_pearson_upper(active, trials)
        ),
        "source_safety_clean_delta": 0.0,
        "source_prediction_array_equal_pairwise": True,
        "source_probability_max_absolute_difference": 0.0,
        "source_inactive_risk_max_absolute_difference": 0.0,
    }


def test_clopper_upper_is_conservative_and_validates_counts() -> None:
    assert 0.0 < clopper_pearson_upper(0, 2500) < 0.01
    assert clopper_pearson_upper(4, 2500) < 0.01
    assert clopper_pearson_upper(2500, 2500) == 1.0


def test_summary_separates_absolute_f1_from_direct_rrc_gates() -> None:
    rows = [
        record("suite/eligible", 647, 0.70),
        record("suite/eligible", 653, 0.71, active=1),
        record("suite/eligible", 659, 0.72, active=4),
        record("suite/ineligible", 647, 0.67),
        record("suite/ineligible", 653, 0.72),
        record("suite/ineligible", 659, 0.72),
        record("suite/partial", 647, 0.75),
    ]
    summary = summarize_records(rows)
    assert summary["observed_capture_count"] == 7
    assert summary["complete_three_seed_scenario_count"] == 2
    assert summary["calibration_known_macro_f1"][
        "passes_absolute_0_9_count"
    ] == 0
    assert summary["rrc_diagnostic_eligible_scenario_count"] == 1
    assert summary["rrc_diagnostic_eligible_identities"] == [
        "suite/eligible"
    ]


def write_canonical(path: Path, value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def test_rrc_design_quarantines_diagnostic_identities(
    tmp_path: Path,
) -> None:
    identities = [
        f"suite{index // 20}/scenario{index:03d}" for index in range(102)
    ]
    development = identities[:14]
    diagnostic_identities = [identities[0], *identities[14:19]]
    protocol_path = tmp_path / "protocol.json"
    diagnostic_path = tmp_path / "diagnostic.json"
    output_path = tmp_path / "design.json"
    protocol = write_canonical(
        protocol_path,
        {
            "schema_version": (
                "strict_v4_krc_csr_confirmation_protocol_v1"
            ),
            "source_registry": [
                {
                    "suite": identity.split("/", 1)[0],
                    "scenario": identity.split("/", 1)[1],
                }
                for identity in identities
            ],
            "development_scenario_identities": development,
        },
    )
    write_canonical(
        diagnostic_path,
        {
            "schema_version": (
                "strict_v4_krc_certificate_bottleneck_audit_v1"
            ),
            "passes": True,
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "data_use_boundary": {
                "test_effect_metrics_read": False,
                "observed_identities_become_development_only_for_rrc": (
                    diagnostic_identities
                ),
            },
        },
    )
    design = create_design(
        Path(__file__).resolve().parents[1],
        protocol_path,
        diagnostic_path,
        output_path,
    )
    assert design["execution_admitted"] is False
    assert design["data_isolation"]["overlap_count"] == 1
    assert design["confirmation"]["heldout_scenario_count"] == 83
    assert design["confirmation"]["capture_count"] == 249
    assert design["confirmation"]["evaluation_count"] == 1494
