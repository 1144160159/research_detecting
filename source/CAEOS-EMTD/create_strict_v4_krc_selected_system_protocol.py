from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from create_strict_v4_krc_external_malicious_execution_protocol import (
    validate_positive_confirmation,
)


IMPLEMENTATION = (
    "create_strict_v4_krc_selected_system_protocol.py",
    "benchmark_krc_selected_system_runtime.py",
    "summarize_strict_v4_krc_selected_system.py",
    "audit_strict_v4_krc_selected_system.py",
    "run_strict_v4_krc_selected_system.py",
    "create_strict_v4_krc_external_malicious_execution_protocol.py",
    "summarize_strict_v4_mdr_selected_system.py",
    "create_strict_v4_external_confirmation_protocol.py",
    "capture_pairwise_runtime.py",
    "caeos/krc_csr_runtime.py",
    "caeos/csr_exact_replay_runtime.py",
    "caeos/csr_runtime.py",
    "caeos/pairwise_runtime.py",
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if (
        value.get("schema_version") != schema
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError(f"canonical {label} required")


def verify_implementation(
    project_root: Path, relatives: Iterable[str] = IMPLEMENTATION
) -> Dict[str, str]:
    output = {}
    for relative in relatives:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing KRC selected-system implementation: {relative}"
            )
        output[relative] = file_hash(path)
    return dict(sorted(output.items()))


def build_sources(
    confirmation_protocol: Dict[str, Any], capture_root: Path
) -> list[Dict[str, Any]]:
    sources = []
    for task in confirmation_protocol["confirmation"]["tasks"]:
        suite = str(task["suite"])
        scenario = str(task["scenario"])
        training_seed = int(task["training_seed"])
        capture_dir = (
            capture_root / suite / scenario / f"seed{training_seed}"
        )
        manifest_path = capture_dir / "capture_manifest.json"
        execution_path = capture_dir / "capture_execution.json"
        manifest = load(manifest_path)
        execution = load(execution_path)
        artifact = capture_dir / str(manifest.get("runtime_artifact", ""))
        inputs = capture_dir / str(manifest.get("evaluation_inputs", ""))
        task_identity = {"suite": suite, "scenario": scenario}
        if (
            manifest.get("schema_version")
            != "strict_v4_krc_csr_runtime_capture_v1"
            or manifest.get("state") != "complete"
            or manifest.get("algorithm") != "krc_csr_caeos_v1"
            or manifest.get("manifest_sha256") != canonical_hash(manifest)
            or manifest.get("task") != task_identity
            or int(manifest.get("training_seed", -1)) != training_seed
            or manifest.get("roundtrip", {}).get("passes") is not True
            or execution.get("schema_version")
            != "strict_v4_krc_csr_capture_execution_v1"
            or execution.get("state") != "complete"
            or execution.get("task") != task_identity
            or int(execution.get("training_seed", -1)) != training_seed
            or execution.get("manifest_sha256")
            != canonical_hash(execution)
            or execution.get("capture_manifest_file_sha256")
            != file_hash(manifest_path)
            or execution.get(
                "unknown_or_test_labels_used_for_cost_selection"
            )
            is not False
            or not artifact.is_file()
            or not inputs.is_file()
            or file_hash(artifact) != manifest.get("runtime_artifact_sha256")
            or file_hash(inputs) != manifest.get("evaluation_inputs_sha256")
        ):
            raise ValueError(
                "invalid KRC confirmation capture for selected-system "
                f"benchmark: {suite}/{scenario}/seed{training_seed}"
            )
        wall_seconds = float(execution["total_capture_wall_seconds"])
        if wall_seconds <= 0.0:
            raise ValueError("positive full KRC capture wall time required")
        sources.append(
            {
                "suite": suite,
                "scenario": scenario,
                "training_seed": training_seed,
                "capture_dir": str(capture_dir.resolve()),
                "capture_manifest_file_sha256": file_hash(manifest_path),
                "capture_execution_file_sha256": file_hash(execution_path),
                "krc_runtime_sha256": manifest[
                    "runtime_artifact_sha256"
                ],
                "evaluation_inputs_sha256": manifest[
                    "evaluation_inputs_sha256"
                ],
                "total_capture_wall_seconds": wall_seconds,
            }
        )
    identities = {
        (item["suite"], item["scenario"], item["training_seed"])
        for item in sources
    }
    if len(sources) != 306 or len(identities) != 306:
        raise ValueError("exactly 306 unique KRC captures are required")
    return sources


def zero_output_counts(result_root: Path) -> Dict[str, int]:
    counts = {
        "benchmarks": (
            len(list(result_root.glob("**/benchmark.json")))
            if result_root.exists()
            else 0
        ),
        "summary": int((result_root / "summary.json").is_file()),
        "audit": int((result_root / "audit.json").is_file()),
        "completion": int((result_root / "execution_complete").is_file()),
    }
    if any(counts.values()):
        raise ValueError(
            "KRC selected-system protocol requires a zero-result root"
        )
    return counts


def create_protocol(
    *,
    project_root: Path,
    result_root: Path,
    downstream_design_path: Path,
    confirmation_protocol_path: Path,
    confirmation_summary_path: Path,
    confirmation_audit_path: Path,
    capture_root: Path,
) -> Dict[str, Any]:
    downstream = load(downstream_design_path)
    confirmation_protocol = load(confirmation_protocol_path)
    confirmation_summary = load(confirmation_summary_path)
    confirmation_audit = load(confirmation_audit_path)
    require_canonical(
        downstream,
        "strict_v4_krc_downstream_sota_design_v1",
        "KRC downstream design",
    )
    validate_positive_confirmation(
        confirmation_protocol,
        confirmation_summary,
        confirmation_audit,
    )
    if (
        downstream["input_manifest_sha256"]["krc_confirmation_protocol"]
        != confirmation_protocol["manifest_sha256"]
        or downstream["activation_gate"]["confirmation_selection"]
        != "krc_csr_caeos_v1"
    ):
        raise ValueError("KRC downstream/confirmation binding mismatch")
    sources = build_sources(confirmation_protocol, capture_root)
    identities = {
        (item["suite"], item["scenario"], item["training_seed"])
        for item in sources
    }
    blocks: Dict[tuple[str, str], set[int]] = {}
    for item in sources:
        key = (str(item["suite"]), str(item["scenario"]))
        blocks.setdefault(key, set()).add(int(item["training_seed"]))
    if (
        len(identities) != 306
        or len(blocks) != 102
        or any(seeds != {647, 653, 659} for seeds in blocks.values())
    ):
        raise ValueError("KRC selected-system source matrix drifted")
    design = downstream["selected_system_and_efficiency"]
    if (
        design["batch_sizes"] != [1, 64, 512]
        or int(design["warmup_repetitions"]) != 5
        or int(design["timed_repetitions"]) != 30
        or int(design["scenario_block_count"]) != 102
        or int(design["bootstrap_repetitions"]) != 10000
    ):
        raise ValueError("KRC selected-system benchmark design drifted")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_krc_selected_system_protocol_v1",
        "status": (
            "admitted_after_positive_krc_confirmation_before_benchmarks"
        ),
        "execution_admitted": True,
        "selected_algorithm": "krc_csr_caeos_v1",
        "comparator": "embedded_pairwise",
        "benchmark": {
            "batch_sizes": list(design["batch_sizes"]),
            "warmup_repetitions": int(design["warmup_repetitions"]),
            "timed_repetitions": int(design["timed_repetitions"]),
            "method_order": "alternate_by_timed_repetition",
            "exact_batch_construction": (
                "cycle_source_rows_in_original_order_without_label_use"
            ),
            "same_inputs_and_process_required": True,
            "gpu_used": False,
            "exclusive_machine_preflight_required": True,
        },
        "aggregation": {
            "unit": (
                "scenario_after_averaging_three_training_seeds_first"
            ),
            "scenario_block_count": 102,
            "bootstrap_repetitions": int(
                design["bootstrap_repetitions"]
            ),
            "bootstrap_seed": int(design["bootstrap_seed"]),
            "suite_equal_secondary_summary": True,
        },
        "deployability_gate": design["deployability_gate"],
        "strict_efficiency_superiority_gate": design[
            "strict_efficiency_superiority_over_each_comparator"
        ],
        "sources": sources,
        "source_count": len(sources),
        "scenario_block_count": len(blocks),
        "training_seeds": [647, 653, 659],
        "expected_benchmark_count": 306,
        "output_counts_at_freeze": zero_output_counts(result_root),
        "paths": {
            "project_root": str(project_root.resolve()),
            "result_root": str(result_root.resolve()),
        },
        "input_manifest_sha256": {
            "downstream_design": downstream["manifest_sha256"],
            "confirmation_protocol": confirmation_protocol[
                "manifest_sha256"
            ],
            "confirmation_summary": confirmation_summary["manifest_sha256"],
            "confirmation_audit": confirmation_audit["manifest_sha256"],
        },
        "input_file_sha256": {
            "downstream_design": file_hash(downstream_design_path),
            "confirmation_protocol": file_hash(confirmation_protocol_path),
            "confirmation_summary": file_hash(confirmation_summary_path),
            "confirmation_audit": file_hash(confirmation_audit_path),
        },
        "implementation_sha256": verify_implementation(project_root),
        "claim_boundary": {
            "deployability_pass_does_not_imply_efficiency_sota": True,
            "efficiency_failure_preserves_accuracy_result": True,
            "fit_cost_uses_full_capture_subprocess_wall_time": True,
            "no_metric_scenario_suite_seed_or_component_splicing": True,
            "must_not_overlap_accuracy_or_external_training": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--downstream-design", type=Path, required=True)
    parser.add_argument(
        "--confirmation-protocol", type=Path, required=True
    )
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_protocol(
        project_root=args.project_root.resolve(),
        result_root=args.result_root.resolve(),
        downstream_design_path=args.downstream_design.resolve(),
        confirmation_protocol_path=args.confirmation_protocol.resolve(),
        confirmation_summary_path=args.confirmation_summary.resolve(),
        confirmation_audit_path=args.confirmation_audit.resolve(),
        capture_root=args.capture_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
