from __future__ import annotations

from copy import deepcopy

from audit_mdr_caeos_no_eligible_weight import audit
from create_strict_v4_external_confirmation_protocol import canonical_hash
from finalize_mdr_caeos_no_eligible_weight import finalize


def fixture():
    scenarios = {"suite": [f"scenario_{index}" for index in range(14)]}
    design = {
        "schema_version": "strict_v4_mdr_caeos_design_v2",
        "mechanism": {
            "training_augmentation_weight_grid": [0.125, 0.25, 0.5]
        },
        "pilot": {
            "scenarios": scenarios,
            "expansion_gate": {
                "clean_known_macro_f1_mean_degradation_maximum": 0.01,
                "clean_known_macro_f1_worst_degradation_maximum": 0.03,
            },
        },
    }
    design["manifest_sha256"] = canonical_hash(design)
    protocol = {
        "schema_version": (
            "strict_v4_mdr_caeos_pilot_execution_protocol_v2"
        ),
        "design_manifest_sha256": design["manifest_sha256"],
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    manifests = []
    hashes = []
    for scenario in scenarios["suite"]:
        for weight in (0.125, 0.25, 0.5):
            manifests.append(
                {
                    "schema_version": (
                        "strict_v4_mdr_caeos_runtime_capture_v1"
                    ),
                    "state": "complete",
                    "task": {"suite": "suite", "scenario": scenario},
                    "weight": weight,
                    "roundtrip": {"passes": True},
                    "known_validation_profile": {
                        "schema_version": (
                            "strict_v4_mdr_known_validation_profile_v1"
                        ),
                        "record_count": 15,
                        "known_validation_labels_used": True,
                        "unknown_or_test_labels_used": False,
                        "clean_delta": -0.04,
                        "corrupted_minimax_macro_f1": 0.7 - weight,
                    },
                }
            )
            hashes.append(f"sha-{scenario}-{weight}")
    integrity = {
        "schema_version": (
            "strict_v4_mdr_caeos_capture_integrity_audit_v1"
        ),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "design_manifest_sha256": design["manifest_sha256"],
        "observed_capture_count": 42,
        "passes": True,
    }
    integrity["manifest_sha256"] = canonical_hash(integrity)
    return protocol, design, integrity, manifests, hashes


def test_no_eligible_weight_produces_auditable_negative_branch() -> None:
    protocol, design, integrity, manifests, hashes = fixture()
    rejection, summary = finalize(
        protocol,
        design,
        integrity,
        manifests,
        hashes,
        selector_file_sha256="selector-sha",
        finalizer_file_sha256="finalizer-sha",
    )
    assert rejection["selected_weight"] is None
    assert all(row["eligible"] is False for row in rejection["rows"])
    assert summary["decision"]["expand_to_full102_confirmation"] is False
    value = audit(
        protocol,
        design,
        integrity,
        rejection,
        summary,
        manifests,
        hashes,
        selector_file_sha256="selector-sha",
        finalizer_file_sha256="finalizer-sha",
        auditor_file_sha256="auditor-sha",
        evaluation_count=0,
    )
    assert value["checks"]["all_weights_ineligible"] is True
    assert value["passes"] is True
    assert value["manifest_sha256"] == canonical_hash(value)


def test_negative_branch_rejects_any_eligible_weight() -> None:
    protocol, design, integrity, manifests, hashes = fixture()
    candidate = deepcopy(manifests)
    for manifest in candidate:
        if manifest["weight"] == 0.25:
            manifest["known_validation_profile"]["clean_delta"] = 0.0
    try:
        finalize(
            protocol,
            design,
            integrity,
            candidate,
            hashes,
            selector_file_sha256="selector-sha",
            finalizer_file_sha256="finalizer-sha",
        )
    except ValueError as error:
        assert str(error) == (
            "MDR rejection branch requires zero eligible weights"
        )
    else:
        raise AssertionError("eligible weight must block rejection branch")
