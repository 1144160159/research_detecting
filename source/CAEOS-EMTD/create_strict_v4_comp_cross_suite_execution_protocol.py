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
REQUIRED_IMPLEMENTATION_KEYS = {
    "caeos/continuous_outer_min_p.py",
    "create_strict_v4_comp_cross_suite_execution_protocol.py",
    "run_strict_v4_comp_cross_suite_confirmation.py",
    "evaluate_strict_v4_comp_cross_suite_confirmation.py",
    "summarize_strict_v4_comp_cross_suite_confirmation.py",
    "audit_strict_v4_comp_cross_suite_confirmation.py",
    "watch_strict_v4_comp_cross_suite_confirmation.py",
    "run_nested_gate_matrix.py",
    "run_neural_baseline_matrix.py",
    "train_hybrid_open_set.py",
    "train_neural_open_set.py",
    "prepare_stratified_cache.py",
    "prepare_cic_iot2023_strict.py",
    "prepare_group_supported_cache.py",
}


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


def create_execution_protocol(
    *,
    design: dict[str, Any],
    activation: dict[str, Any],
    input_file_sha256: dict[str, str],
    implementation_sha256: dict[str, str],
    observed_output_counts: dict[str, int],
) -> dict[str, Any] | None:
    require_canonical(
        design,
        "strict_v4_comp_cross_suite_confirmation_design_v1",
        "cross-suite design",
    )
    require_canonical(
        activation,
        "strict_v4_comp_cross_suite_activation_v1",
        "cross-suite activation",
    )
    if (
        activation.get("input_manifest_sha256", {}).get("cross_suite_design")
        != design.get("manifest_sha256")
    ):
        raise ValueError("activation does not bind the frozen design")
    if activation.get("state") == "negative_not_required_retain_pairwise":
        if (
            activation.get("cross_suite_execution_admitted") is not False
            or activation.get("action")
            != "write_not_required_and_retain_pairwise"
        ):
            raise ValueError("invalid negative activation")
        return None
    if (
        activation.get("state") != "positive_activation"
        or activation.get("pilot_decision_passes") is not True
        or activation.get("cross_suite_execution_admitted") is not True
        or activation.get("action")
        != "create_cross_suite_execution_protocol"
        or activation.get("validation", {}).get("pilot_integrity_passes")
        is not True
    ):
        raise ValueError("canonical positive activation required")
    if any(int(value) != 0 for value in observed_output_counts.values()):
        raise ValueError("execution protocol must freeze before task outputs")
    if set(implementation_sha256) != REQUIRED_IMPLEMENTATION_KEYS:
        raise ValueError("complete frozen execution implementation required")
    if any(
        not isinstance(value, str) or len(value) != 64
        for value in implementation_sha256.values()
    ):
        raise ValueError("implementation SHA values must be complete")

    universe = design.get("confirmation_universe", {})
    tasks = universe.get("tasks")
    if (
        universe.get("suite_count") != 7
        or universe.get("scenario_count") != 102
        or universe.get("paired_task_count") != 306
        or universe.get("fresh_seeds") != [269, 271, 277]
        or not isinstance(tasks, list)
        or len(tasks) != 306
        or len(
            {
                (task["suite"], task["scenario"], task["seed"])
                for task in tasks
            }
        )
        != 306
    ):
        raise ValueError("frozen full102x3 universe required")

    protocol: dict[str, Any] = {
        "schema_version": (
            "strict_v4_comp_cross_suite_execution_protocol_v1"
        ),
        "state": "frozen_after_positive_pilot_before_cross_suite_execution",
        "execution_admitted": True,
        "candidate": design["candidate"],
        "confirmation_universe": universe,
        "execution_controls": design["execution_controls"],
        "primary_statistics": design["primary_statistics"],
        "admission_gate": design["admission_gate"],
        "selection_policy": design["selection_policy"],
        "output_contract": {
            "run_root": "runs/strict_v4_comp_cross_suite_confirmation_v1",
            "result_root": "results/strict_v4_comp_cross_suite_confirmation_v1",
            "pairwise_comp_task_count": 306,
            "opendetect_task_count": 306,
            "summary_schema": (
                "strict_v4_comp_cross_suite_confirmation_summary_v1"
            ),
            "audit_schema": (
                "strict_v4_comp_cross_suite_confirmation_audit_v1"
            ),
            "completion_requires_summary_and_independent_audit": True,
            "partial_metrics_must_not_be_aggregated": True,
            "task_outputs_must_be_atomic_and_hash_bound": True,
        },
        "input_manifest_sha256": {
            "cross_suite_design": design["manifest_sha256"],
            "positive_activation": activation["manifest_sha256"],
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": dict(sorted(implementation_sha256.items())),
        "formal_result_counts_at_freeze": {
            name: int(value)
            for name, value in sorted(observed_output_counts.items())
        },
        "claim_boundary": {
            "positive_pilot_only_authorizes_this_execution": True,
            "protocol_creation_is_not_cross_suite_effect": True,
            "summary_pass_is_required_for_candidate_selection": True,
            "independent_audit_pass_is_required_for_candidate_selection": True,
            "external_malicious_parrot_deployment_and_efficiency_still_required": True,
            "pairwise_remains_incumbent_until_all_selection_gates_pass": True,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


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
        "--activation",
        type=Path,
        default=Path(
            "results/strict_v4_comp_cross_suite_confirmation_v1/"
            "activation_decision.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/strict_v4_comp_cross_suite_confirmation_v1/"
            "execution_protocol.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    design_path = resolve(args.design)
    activation_path = resolve(args.activation)
    output_path = resolve(args.output)
    if file_hash(design_path) != DESIGN_FILE_SHA256:
        raise ValueError("exact frozen cross-suite design required")
    if not activation_path.is_file():
        if output_path.exists():
            raise ValueError("pending activation must not retain a protocol")
        print("state=pending_activation")
        return
    activation = load(activation_path)
    if activation.get("state") == "negative_not_required_retain_pairwise":
        if output_path.exists():
            raise ValueError("negative activation must not retain a protocol")
        print("state=not_required_retain_pairwise")
        return

    implementation_paths = {
        key: root / key for key in REQUIRED_IMPLEMENTATION_KEYS
    }
    missing = [
        key for key, path in implementation_paths.items() if not path.is_file()
    ]
    if missing:
        raise ValueError(f"missing execution implementation: {missing}")
    result_root = output_path.parent
    observed_output_counts = {
        "task_metrics": len(list(result_root.glob("tasks/**/*.json"))),
        "summary": len(list(result_root.glob("summary*.json"))),
        "audit": len(list(result_root.glob("audit*.json"))),
        "completion_marker": len(list(result_root.glob("*complete*"))),
    }
    protocol = create_execution_protocol(
        design=load(design_path),
        activation=activation,
        input_file_sha256={
            str(design_path.relative_to(root)): file_hash(design_path),
            str(activation_path.relative_to(root)): file_hash(activation_path),
        },
        implementation_sha256={
            key: file_hash(path) for key, path in implementation_paths.items()
        },
        observed_output_counts=observed_output_counts,
    )
    if protocol is None:
        raise ValueError("negative activation reached protocol creation")
    result_root.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        existing = load(output_path)
        if existing != protocol:
            raise ValueError("existing execution protocol is immutable")
    else:
        temporary = output_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(protocol, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(output_path)
    print(f"manifest_sha256={protocol['manifest_sha256']}")
    print(f"file_sha256={file_hash(output_path)}")


if __name__ == "__main__":
    main()
