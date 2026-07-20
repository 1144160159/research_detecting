from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def select_weight(
    candidates: list[tuple[float, dict[str, Any]]],
    clean_tolerance: float,
) -> dict[str, Any]:
    if not candidates:
        raise ValueError("no modality-dropout candidates were supplied")
    fingerprint = None
    rows = []
    for weight, metrics in candidates:
        current_fingerprint = metrics.get("split_metadata", {}).get(
            "split_fingerprint"
        )
        if fingerprint is None:
            fingerprint = current_fingerprint
        elif current_fingerprint != fingerprint:
            raise ValueError("candidate split fingerprints differ")
        corruption = metrics.get("corruption_protocol", {}).get(
            "test_corruption", {}
        )
        if corruption.get("kind") != "none":
            raise ValueError("weight selection inputs must use a clean test condition")
        validation = metrics.get("model_selection", {}).get(
            "validation_scores", {}
        )
        field = validation.get("field_dropout_validation", {})
        if field.get("uses_known_validation_labels_only") is not True:
            raise ValueError("candidate lacks known-validation-only evidence")
        if field.get("unknown_or_test_labels_used") is not False:
            raise ValueError("candidate validation evidence leakage guard failed")
        clean_delta = float(validation.get("clean_delta_from_baseline"))
        objective = float(field.get("minimax_objective"))
        row = {
            "weight": float(weight),
            "clean_validation_macro_f1": float(validation["selected"]),
            "clean_delta_from_baseline": clean_delta,
            "corrupted_validation_mean_macro_f1": float(field["mean_macro_f1"]),
            "corrupted_validation_minimum_macro_f1": float(
                field["minimum_macro_f1"]
            ),
            "corrupted_validation_minimax_objective": objective,
            "eligible": clean_delta >= -float(clean_tolerance) - 1e-12,
        }
        rows.append(row)
    eligible = [row for row in rows if row["eligible"]]
    if not eligible:
        raise ValueError("no candidate satisfies the clean-validation tolerance")
    selected = max(
        eligible,
        key=lambda row: (
            row["corrupted_validation_minimax_objective"],
            row["corrupted_validation_minimum_macro_f1"],
            row["clean_validation_macro_f1"],
            -row["weight"],
        ),
    )
    return {
        "schema_version": "modality_dropout_validation_selection_v1",
        "state": "selected_on_known_validation_only",
        "selection_rule": "maximize 0.5 * corrupted-mean F1 + 0.5 * corrupted-minimum F1 subject to clean F1 delta >= -tolerance",
        "clean_tolerance": float(clean_tolerance),
        "split_fingerprint": fingerprint,
        "unknown_or_test_labels_used_for_selection": False,
        "rows": rows,
        "selected_weight": selected["weight"],
        "selected_row": selected,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Select field-dropout weight from known validation")
    parser.add_argument(
        "--candidate",
        action="append",
        required=True,
        help="WEIGHT=metrics.json",
    )
    parser.add_argument("--clean-tolerance", type=float, default=0.002)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidates = []
    for value in args.candidate:
        weight, path = value.split("=", 1)
        candidates.append(
            (float(weight), json.loads(Path(path).read_text(encoding="utf-8")))
        )
    result = select_weight(candidates, args.clean_tolerance)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["selected_row"], sort_keys=True))


if __name__ == "__main__":
    main()
