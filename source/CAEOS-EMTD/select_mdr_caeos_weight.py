from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def select(
    design: Dict[str, Any],
    manifests: List[Dict[str, Any]],
    manifest_file_sha256: List[str],
) -> Dict[str, Any]:
    if (
        design.get("schema_version") != "strict_v4_mdr_caeos_design_v2"
        or design.get("manifest_sha256") != canonical_hash(design)
    ):
        raise ValueError("canonical MDR v2 design required")
    expected_scenarios = {
        (suite, scenario)
        for suite, scenarios in design["pilot"]["scenarios"].items()
        for scenario in scenarios
    }
    expected_weights = {
        float(value)
        for value in design["mechanism"][
            "training_augmentation_weight_grid"
        ]
    }
    expected = {
        (suite, scenario, weight)
        for suite, scenario in expected_scenarios
        for weight in expected_weights
    }
    observed = set()
    rows_by_weight: Dict[float, List[Dict[str, float]]] = {
        weight: [] for weight in expected_weights
    }
    for manifest in manifests:
        if (
            manifest.get("schema_version")
            != "strict_v4_mdr_caeos_runtime_capture_v1"
            or manifest.get("state") != "complete"
            or manifest.get("roundtrip", {}).get("passes") is not True
        ):
            raise ValueError("invalid MDR runtime capture")
        profile = manifest.get("known_validation_profile", {})
        if (
            profile.get("schema_version")
            != "strict_v4_mdr_known_validation_profile_v1"
            or profile.get("record_count") != 15
            or profile.get("unknown_or_test_labels_used") is not False
        ):
            raise ValueError("invalid MDR known-validation profile")
        task = manifest.get("task", {})
        identity = (
            str(task.get("suite")),
            str(task.get("scenario")),
            float(manifest["weight"]),
        )
        if identity in observed:
            raise ValueError("duplicate MDR capture identity")
        observed.add(identity)
        rows_by_weight[identity[2]].append(
            {
                "clean_delta": float(profile["clean_delta"]),
                "corrupted_minimax": float(
                    profile["corrupted_minimax_macro_f1"]
                ),
            }
        )
    if observed != expected:
        raise ValueError(
            f"MDR capture universe mismatch: missing={len(expected-observed)} "
            f"extra={len(observed-expected)}"
        )

    rows = []
    mean_limit = -float(
        design["pilot"]["expansion_gate"][
            "clean_known_macro_f1_mean_degradation_maximum"
        ]
    )
    worst_limit = -float(
        design["pilot"]["expansion_gate"][
            "clean_known_macro_f1_worst_degradation_maximum"
        ]
    )
    for weight in sorted(expected_weights):
        values = rows_by_weight[weight]
        clean = np.asarray([row["clean_delta"] for row in values])
        robust = np.asarray(
            [row["corrupted_minimax"] for row in values]
        )
        row = {
            "weight": weight,
            "scenario_count": len(values),
            "clean_delta_mean": float(clean.mean()),
            "clean_delta_minimum": float(clean.min()),
            "corrupted_minimax_mean": float(robust.mean()),
            "corrupted_minimax_minimum": float(robust.min()),
        }
        row["eligible"] = bool(
            row["clean_delta_mean"] >= mean_limit - 1e-12
            and row["clean_delta_minimum"] >= worst_limit - 1e-12
        )
        rows.append(row)
    eligible = [row for row in rows if row["eligible"]]
    if not eligible:
        raise ValueError("no MDR weight satisfies the frozen clean tolerance")
    selected = max(
        eligible,
        key=lambda row: (
            row["corrupted_minimax_mean"],
            row["corrupted_minimax_minimum"],
            row["clean_delta_mean"],
            -row["weight"],
        ),
    )
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_caeos_weight_selection_v1",
        "state": "selected_on_known_validation_only",
        "design_manifest_sha256": design["manifest_sha256"],
        "selection_rule": (
            "maximize cross-scenario mean then minimum corrupted minimax "
            "Macro-F1 subject to frozen mean/worst clean tolerances"
        ),
        "rows": rows,
        "selected_weight": selected["weight"],
        "selected_row": selected,
        "capture_manifest_count": len(manifests),
        "capture_manifest_file_sha256": sorted(manifest_file_sha256),
        "known_validation_labels_used": True,
        "unknown_or_test_labels_used": False,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(args.capture_root.rglob("capture_manifest.json"))
    value = select(
        load(args.design),
        [load(path) for path in paths],
        [file_hash(path) for path in paths],
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
