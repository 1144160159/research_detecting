from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


DESIGN_FILE_SHA256 = (
    "55498ee30545d7ac9e73a103daba5e2d319d4de844c63e0939ebc0039ef3b31d"
)
DESIGN_MANIFEST_SHA256 = (
    "5c2ca061200c5ba837154970ee4413914e88149e3427386ca34295b868183027"
)
PILOT_PROTOCOL_FILE_SHA256 = (
    "00411a25500270d9773d4a63750628bb5c98e23e48c9885aded49e42f8d47720"
)
PILOT_PROTOCOL_MANIFEST_SHA256 = (
    "3486d4e70c5d4a9c694ae93ef2f6af1f8bd0287efcd246c621a78837d2162310"
)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def classify_activation(
    *,
    design: dict[str, Any],
    pilot_protocol: dict[str, Any],
    confirmation: dict[str, Any] | None,
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
) -> dict[str, Any] | None:
    require_canonical(
        design,
        "strict_v4_comp_cross_suite_confirmation_design_v1",
        "cross-suite design",
    )
    require_canonical(
        pilot_protocol,
        "strict_v4_comp_confirmation_protocol_v1",
        "pilot protocol",
    )
    activation_gate = design.get("activation_gate", {})
    if (
        design.get("state")
        != (
            "conditionally_frozen_before_pilot_completion_and_"
            "cross_suite_outputs"
        )
        or design.get("execution_admitted_at_freeze") is not False
        or design.get("confirmation_universe", {}).get("paired_task_count")
        != 306
        or activation_gate.get("required_pilot_protocol_manifest_sha256")
        != pilot_protocol.get("manifest_sha256")
    ):
        raise ValueError("frozen cross-suite activation boundary required")
    if confirmation is None:
        return None

    require_canonical(
        confirmation,
        "strict_v4_comp_confirmation_v1",
        "pilot confirmation",
    )
    validation = confirmation.get("validation", {})
    evidence = confirmation.get("input_evidence", {})
    decision = confirmation.get("decision", {})
    if (
        confirmation.get("state") != "fresh_seed_confirmation_complete"
        or validation.get("passes") is not True
        or validation.get("paired_task_count") != 18
        or validation.get("seeds") != [139, 149, 163]
        or validation.get("scenario_count") != 6
        or validation.get("split_fingerprint_pair_checks") != 18
        or validation.get(
            "unknown_or_test_labels_used_for_candidate_routing"
        )
        is not False
        or validation.get(
            "unknown_or_test_labels_used_for_candidate_thresholds"
        )
        is not False
        or evidence.get("protocol_manifest_sha256")
        != pilot_protocol.get("manifest_sha256")
        or evidence.get("protocol_file_sha256")
        != PILOT_PROTOCOL_FILE_SHA256
        or not isinstance(decision.get("passes"), bool)
        or confirmation.get("claim_boundary", {}).get(
            "cross_suite_expansion_required_after_pilot_pass"
        )
        is not True
    ):
        raise ValueError("complete canonical 18-task pilot confirmation required")

    passes = bool(decision["passes"])
    result: dict[str, Any] = {
        "schema_version": "strict_v4_comp_cross_suite_activation_v1",
        "state": (
            "positive_activation"
            if passes
            else "negative_not_required_retain_pairwise"
        ),
        "pilot_decision_passes": passes,
        "action": (
            "create_cross_suite_execution_protocol"
            if passes
            else "write_not_required_and_retain_pairwise"
        ),
        "cross_suite_execution_admitted": passes,
        "validation": {
            "pilot_integrity_passes": True,
            "paired_task_count": 18,
            "seed_count": 3,
            "scenario_count": 6,
            "split_fingerprint_pair_checks": 18,
            "unknown_or_test_labels_used_for_activation": False,
            "partial_metrics_used_for_activation": False,
        },
        "input_manifest_sha256": {
            "cross_suite_design": design["manifest_sha256"],
            "pilot_protocol": pilot_protocol["manifest_sha256"],
            "pilot_confirmation": confirmation["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": implementation_sha256,
        "claim_boundary": {
            "positive_activation_is_not_cross_suite_effect": True,
            "positive_activation_is_not_candidate_selection": True,
            "negative_activation_preserves_pairwise_incumbent": True,
            "no_pilot_partial_metrics_are_read": True,
            "no_unknown_or_test_labels_are_used_for_new_selection": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--design",
        type=Path,
        default=Path(
            "results/strict_v4_comp_cross_suite_confirmation_design_v1/"
            "design_protocol.json"
        ),
    )
    parser.add_argument(
        "--pilot-protocol",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_v1/protocol.json"),
    )
    parser.add_argument(
        "--pilot-confirmation",
        type=Path,
        default=Path(
            "results/strict_v4_comp_confirmation_v1/confirmation.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_comp_cross_suite_confirmation_v1/"
            "activation_decision.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    design_path = resolve(args.design)
    pilot_protocol_path = resolve(args.pilot_protocol)
    confirmation_path = resolve(args.pilot_confirmation)
    output_path = resolve(args.output)
    if (
        file_hash(design_path) != DESIGN_FILE_SHA256
        or file_hash(pilot_protocol_path) != PILOT_PROTOCOL_FILE_SHA256
    ):
        raise ValueError("exact frozen cross-suite design and pilot required")
    design = load(design_path)
    pilot_protocol = load(pilot_protocol_path)
    if (
        design.get("manifest_sha256") != DESIGN_MANIFEST_SHA256
        or pilot_protocol.get("manifest_sha256")
        != PILOT_PROTOCOL_MANIFEST_SHA256
    ):
        raise ValueError("frozen activation inputs drifted")
    confirmation = load(confirmation_path) if confirmation_path.is_file() else None
    input_paths = [design_path, pilot_protocol_path]
    if confirmation is not None:
        input_paths.append(confirmation_path)
    result = classify_activation(
        design=design,
        pilot_protocol=pilot_protocol,
        confirmation=confirmation,
        input_file_sha256={
            str(path.relative_to(root)): file_hash(path) for path in input_paths
        },
        implementation_sha256={
            str(Path(__file__).resolve().relative_to(root)): file_hash(
                Path(__file__).resolve()
            )
        },
    )
    if result is None:
        if output_path.exists():
            raise ValueError("pending activation must not retain a formal decision")
        print("state=pending_pilot_confirmation")
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        existing = load(output_path)
        if existing != result:
            raise ValueError("existing activation decision is immutable")
    else:
        temporary = output_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output_path)
    print(f"state={result['state']}")
    print(f"manifest_sha256={result['manifest_sha256']}")
    print(f"file_sha256={file_hash(output_path)}")


if __name__ == "__main__":
    main()
