from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str) -> dict:
    with (ROOT / "configs" / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def test_feature_views_reference_frozen_schema_without_identity_leakage() -> None:
    schema = load("unified_multimodal_v4.schema.json")
    views = load("unified_multimodal_v5.feature_views.json")
    columns = {item["name"] for item in schema["columns"]}
    targets = set(views["target_columns"])
    forbidden = set(views["default_forbidden_model_features"])
    audit_only = set(views["audit_only_columns"])

    assert views["source_csv_schema"] == schema["schema_version"]
    assert targets <= columns
    assert forbidden <= columns
    assert audit_only <= columns
    assert targets.isdisjoint(forbidden)

    model_columns: set[str] = set()
    derived_columns: set[str] = set()
    for modality in views["modalities"].values():
        for key, values in modality.items():
            if not key.endswith("columns"):
                continue
            if key == "derived_from_existing_columns":
                derived_columns.update(values)
            else:
                model_columns.update(values)

    assert model_columns <= columns
    assert model_columns.isdisjoint(targets)
    assert model_columns.isdisjoint(forbidden)
    assert model_columns.isdisjoint(audit_only)
    assert {
        "initiator_relative_direction_seq",
        "signed_packet_length_seq",
        "directional_burst_count",
        "modality_missingness_mask",
    } <= derived_columns
    assert {"port_a", "port_b", "endpoint_a_hash", "endpoint_b_hash"} <= forbidden
    assert views["selection_gate"][
        "unknown_test_features_or_labels_visible_during_selection"
    ] is False
