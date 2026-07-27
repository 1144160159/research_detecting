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
    "4d14ea956fc9fdfd20888330c43f5ec32a4fa4a5f065c7da12b901ddd11a5113"
)
DESIGN_MANIFEST_SHA256 = (
    "4cb8770e2c054dbdcda8bedb1f99d19b9f371ba98e9543b658c2936a31e8e693"
)
PILOT_PROTOCOL_FILE_SHA256 = (
    "3a5dcb527092ac759343671f19ce839166e905491c3fe48ee21f0e6fb921fdba"
)
PILOT_PROTOCOL_MANIFEST_SHA256 = (
    "9f6e38e819b1d3a00c6ef527c83bc9be26f9252d18668e6f7cd4d5fa51869665"
)
PILOT_SEEDS = [283, 293, 307]


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


def validate_complete_pilot_confirmation(
    confirmation: dict[str, Any],
    pilot_protocol: dict[str, Any],
) -> bool:
    require_canonical(
        confirmation,
        "strict_v4_pug_confirmation_v1",
        "pilot confirmation",
    )
    tasks = confirmation.get("tasks")
    hashes = confirmation.get("artifact_sha256")
    gate_checks = confirmation.get("gate_checks")
    decision = confirmation.get("decision", {})
    if (
        confirmation.get("protocol_manifest_sha256")
        != pilot_protocol.get("manifest_sha256")
        or confirmation.get("task_count") != 18
        or not isinstance(tasks, list)
        or len(tasks) != 18
        or not isinstance(hashes, dict)
        or len(hashes) != 126
        or not all(
            isinstance(value, str) and len(value) == 64
            for value in hashes.values()
        )
        or not isinstance(gate_checks, dict)
        or not gate_checks
        or not all(isinstance(value, bool) for value in gate_checks.values())
        or not isinstance(decision.get("passes"), bool)
        or decision.get("cross_suite_execution_admitted") is not False
        or confirmation.get("partial_metrics_aggregated") is not False
        or confirmation.get("unknown_or_test_labels_used_for_selection")
        is not False
        or not isinstance(confirmation.get("candidate_vs_pairwise"), dict)
        or not isinstance(confirmation.get("candidate_vs_opendetect"), dict)
    ):
        raise ValueError("complete canonical 18-task PUG pilot required")

    identities = {
        (task.get("suite"), task.get("scenario"), task.get("seed"))
        for task in tasks
    }
    scenarios = {
        (task.get("suite"), task.get("scenario")) for task in tasks
    }
    if (
        len(identities) != 18
        or len(scenarios) != 6
        or sorted({task.get("seed") for task in tasks}) != PILOT_SEEDS
        or any(
            task.get("unknown_or_test_labels_used_for_selection") is not False
            or not isinstance(task.get("split_fingerprint"), str)
            or not task.get("split_fingerprint")
            for task in tasks
        )
    ):
        raise ValueError("complete canonical 18-task PUG pilot required")

    passes = bool(decision["passes"])
    if (
        passes != all(gate_checks.values())
        or decision.get("selected_method")
        != ("caeos_pug" if passes else "caeos_pairwise")
    ):
        raise ValueError("PUG pilot decision is inconsistent with its gates")
    return passes


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
        "strict_v4_pug_cross_suite_confirmation_design_v1",
        "cross-suite design",
    )
    require_canonical(
        pilot_protocol,
        "strict_v4_pug_execution_protocol_v1",
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
        or activation_gate.get("required_pilot_schema")
        != "strict_v4_pug_confirmation_v1"
        or activation_gate.get("pilot_task_count") != 18
        or activation_gate.get("pilot_decision_passes_must_equal") is not True
        or activation_gate.get("pilot_selected_method_must_equal")
        != "caeos_pug"
        or activation_gate.get(
            "pilot_cross_suite_execution_admitted_must_equal"
        )
        is not False
    ):
        raise ValueError("frozen PUG cross-suite activation boundary required")
    if confirmation is None:
        return None

    passes = validate_complete_pilot_confirmation(
        confirmation, pilot_protocol
    )
    result: dict[str, Any] = {
        "schema_version": "strict_v4_pug_cross_suite_activation_v1",
        "state": (
            "positive_activation"
            if passes
            else "negative_not_required_retain_upstream_incumbent"
        ),
        "pilot_decision_passes": passes,
        "action": (
            "create_cross_suite_execution_protocol"
            if passes
            else "write_not_required_and_retain_upstream_incumbent"
        ),
        "cross_suite_execution_admitted": passes,
        "validation": {
            "pilot_integrity_passes": True,
            "paired_task_count": 18,
            "seed_count": 3,
            "scenario_count": 6,
            "artifact_sha256_count": 126,
            "split_fingerprint_pair_checks": 18,
            "unknown_or_test_labels_used_for_activation": False,
            "partial_metrics_used_for_activation": False,
        },
        "input_manifest_sha256": {
            "cross_suite_design": design["manifest_sha256"],
            "pilot_protocol": pilot_protocol["manifest_sha256"],
            "pilot_confirmation": confirmation["manifest_sha256"],
        },
        "input_file_sha256": dict(sorted(input_file_sha256.items())),
        "implementation_sha256": dict(
            sorted(implementation_sha256.items())
        ),
        "claim_boundary": {
            "positive_activation_is_not_cross_suite_effect": True,
            "positive_activation_is_not_candidate_selection": True,
            "negative_activation_preserves_upstream_incumbent": True,
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
            "results/strict_v4_pug_cross_suite_design_v1/design.json"
        ),
    )
    parser.add_argument(
        "--pilot-protocol",
        type=Path,
        default=Path(
            "results/strict_v4_pug_confirmation_v1/execution_protocol.json"
        ),
    )
    parser.add_argument(
        "--pilot-confirmation",
        type=Path,
        default=Path(
            "results/strict_v4_pug_confirmation_v1/confirmation.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/"
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
        raise ValueError("exact frozen PUG cross-suite inputs required")
    design = load(design_path)
    pilot_protocol = load(pilot_protocol_path)
    if (
        design.get("manifest_sha256") != DESIGN_MANIFEST_SHA256
        or pilot_protocol.get("manifest_sha256")
        != PILOT_PROTOCOL_MANIFEST_SHA256
    ):
        raise ValueError("frozen PUG activation inputs drifted")

    confirmation = (
        load(confirmation_path) if confirmation_path.is_file() else None
    )
    input_paths = [design_path, pilot_protocol_path]
    if confirmation is not None:
        input_paths.append(confirmation_path)
    implementation_path = Path(__file__).resolve()
    result = classify_activation(
        design=design,
        pilot_protocol=pilot_protocol,
        confirmation=confirmation,
        input_file_sha256={
            path.relative_to(root).as_posix(): file_hash(path)
            for path in input_paths
        },
        implementation_sha256={
            implementation_path.relative_to(root).as_posix(): file_hash(
                implementation_path
            )
        },
    )
    if result is None:
        if output_path.exists():
            raise ValueError(
                "pending activation must not retain a formal decision"
            )
        print("state=pending_pilot_confirmation")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        if load(output_path) != result:
            raise ValueError("existing activation decision is immutable")
    else:
        temporary = output_path.with_suffix(".json.tmp")
        with temporary.open(
            "w", encoding="utf-8", newline="\n"
        ) as destination:
            destination.write(
                json.dumps(result, indent=2, sort_keys=True) + "\n"
            )
        temporary.replace(output_path)
    print(f"state={result['state']}")
    print(f"manifest_sha256={result['manifest_sha256']}")
    print(f"file_sha256={file_hash(output_path)}")


if __name__ == "__main__":
    main()
