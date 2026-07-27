from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_krc_external_malicious_execution_protocol import (
    validate_positive_confirmation,
)
from create_strict_v4_mdr_opendetect_efficiency_protocol import (
    build_comparators,
)


IMPLEMENTATION = (
    "create_strict_v4_krc_opendetect_efficiency_protocol.py",
    "benchmark_krc_opendetect_runtime.py",
    "summarize_strict_v4_krc_opendetect_efficiency.py",
    "audit_strict_v4_krc_opendetect_efficiency.py",
    "run_strict_v4_krc_opendetect_efficiency.py",
    "create_strict_v4_krc_external_malicious_execution_protocol.py",
    "create_strict_v4_mdr_opendetect_efficiency_protocol.py",
    "benchmark_mdr_opendetect_runtime.py",
    "summarize_strict_v4_mdr_opendetect_efficiency.py",
    "create_strict_v4_external_confirmation_protocol.py",
    "capture_pairwise_runtime.py",
    "caeos/krc_csr_runtime.py",
    "caeos/open_detect_runtime.py",
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


def verify_implementation(project_root: Path) -> Dict[str, str]:
    output = {}
    for relative in IMPLEMENTATION:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing KRC-OpenDetect implementation: {relative}"
            )
        output[relative] = file_hash(path)
    return dict(sorted(output.items()))


def build_sources(
    selected_protocol: Dict[str, Any],
    comparators: Dict[tuple[str, str], Dict[str, Any]],
) -> list[Dict[str, Any]]:
    sources = []
    for selected in selected_protocol["sources"]:
        suite = str(selected["suite"])
        scenario = str(selected["scenario"])
        training_seed = int(selected["training_seed"])
        comparator = comparators.get((suite, scenario))
        if comparator is None:
            raise ValueError(
                f"missing OpenDetect comparator: {suite}/{scenario}"
            )
        capture_dir = Path(selected["capture_dir"])
        manifest_path = capture_dir / "capture_manifest.json"
        execution_path = capture_dir / "capture_execution.json"
        manifest = load(manifest_path)
        execution = load(execution_path)
        artifact = capture_dir / str(manifest.get("runtime_artifact", ""))
        inputs = capture_dir / str(manifest.get("evaluation_inputs", ""))
        if (
            manifest.get("schema_version")
            != "strict_v4_krc_csr_runtime_capture_v1"
            or manifest.get("manifest_sha256") != canonical_hash(manifest)
            or manifest.get("roundtrip", {}).get("passes") is not True
            or file_hash(manifest_path)
            != selected["capture_manifest_file_sha256"]
            or file_hash(execution_path)
            != selected["capture_execution_file_sha256"]
            or execution.get("manifest_sha256") != canonical_hash(execution)
            or float(execution.get("total_capture_wall_seconds", -1.0))
            != float(selected["total_capture_wall_seconds"])
            or file_hash(artifact) != selected["krc_runtime_sha256"]
            or file_hash(inputs) != selected["evaluation_inputs_sha256"]
        ):
            raise ValueError(
                "KRC selected-system source drifted before OpenDetect "
                f"efficiency: {suite}/{scenario}/seed{training_seed}"
            )
        sources.append(
            {
                "suite": suite,
                "scenario": scenario,
                "training_seed": training_seed,
                "candidate": {
                    "capture_dir": str(capture_dir.resolve()),
                    "capture_manifest_file_sha256": file_hash(
                        manifest_path
                    ),
                    "capture_execution_file_sha256": file_hash(
                        execution_path
                    ),
                    "total_capture_wall_seconds": float(
                        execution["total_capture_wall_seconds"]
                    ),
                    "runtime_artifact_sha256": manifest[
                        "runtime_artifact_sha256"
                    ],
                    "runtime_artifact_bytes": int(
                        manifest["runtime_artifact_bytes"]
                    ),
                    "evaluation_inputs_sha256": manifest[
                        "evaluation_inputs_sha256"
                    ],
                },
                "comparator": dict(comparator),
            }
        )
    identities = {
        (item["suite"], item["scenario"], item["training_seed"])
        for item in sources
    }
    blocks: Dict[tuple[str, str], set[int]] = {}
    for item in sources:
        blocks.setdefault(
            (item["suite"], item["scenario"]), set()
        ).add(item["training_seed"])
    if (
        len(sources) != 306
        or len(identities) != 306
        or len(blocks) != 102
        or any(seeds != {647, 653, 659} for seeds in blocks.values())
    ):
        raise ValueError("KRC-OpenDetect source matrix is incomplete")
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
            "KRC-OpenDetect protocol requires a zero-result root"
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
    selected_protocol_path: Path,
    selected_summary_path: Path,
    selected_audit_path: Path,
    comparative_protocol_path: Path,
    comparative_run_root: Path,
) -> Dict[str, Any]:
    downstream = load(downstream_design_path)
    confirmation_protocol = load(confirmation_protocol_path)
    confirmation_summary = load(confirmation_summary_path)
    confirmation_audit = load(confirmation_audit_path)
    selected_protocol = load(selected_protocol_path)
    selected_summary = load(selected_summary_path)
    selected_audit = load(selected_audit_path)
    comparative = load(comparative_protocol_path)
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
    require_canonical(
        selected_protocol,
        "strict_v4_krc_selected_system_protocol_v1",
        "KRC selected-system protocol",
    )
    require_canonical(
        selected_summary,
        "strict_v4_krc_selected_system_summary_v1",
        "KRC selected-system summary",
    )
    require_canonical(
        selected_audit,
        "strict_v4_krc_selected_system_audit_v1",
        "KRC selected-system audit",
    )
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative protocol",
    )
    if (
        downstream["input_manifest_sha256"]["comparative_protocol"]
        != comparative["manifest_sha256"]
        or selected_protocol["input_manifest_sha256"][
            "downstream_design"
        ]
        != downstream["manifest_sha256"]
        or selected_summary.get("protocol_manifest_sha256")
        != selected_protocol["manifest_sha256"]
        or selected_audit.get("protocol_manifest_sha256")
        != selected_protocol["manifest_sha256"]
        or selected_audit.get("summary_manifest_sha256")
        != selected_summary["manifest_sha256"]
        or selected_summary.get("deployability_decision", {}).get(
            "passes"
        )
        is not True
        or selected_audit.get("passes") is not True
        or selected_audit.get("deployability_gate_passes") is not True
    ):
        raise ValueError(
            "positive KRC deployability is required before OpenDetect "
            "efficiency"
        )
    comparators = build_comparators(comparative, comparative_run_root)
    sources = build_sources(selected_protocol, comparators)
    design = downstream["selected_system_and_efficiency"]
    if (
        design["batch_sizes"] != [1, 64, 512]
        or int(design["warmup_repetitions"]) != 5
        or int(design["timed_repetitions"]) != 30
    ):
        raise ValueError("KRC-OpenDetect benchmark design drifted")
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_krc_opendetect_efficiency_protocol_v1"
        ),
        "status": (
            "admitted_after_positive_krc_deployability_before_benchmarks"
        ),
        "execution_admitted": True,
        "selected_algorithm": "krc_csr_caeos_v1",
        "comparator": "opendetect_seed137_deployment_runtime",
        "benchmark": {
            "batch_sizes": list(design["batch_sizes"]),
            "warmup_repetitions": int(design["warmup_repetitions"]),
            "timed_repetitions": int(design["timed_repetitions"]),
            "method_order": "alternate_by_timed_repetition",
            "exact_batch_construction": (
                "cycle_krc_evaluation_rows_without_label_use"
            ),
            "same_inputs_and_process_required": True,
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
        "strict_efficiency_superiority_gate": design[
            "strict_efficiency_superiority_over_each_comparator"
        ],
        "cost_policy": {
            "candidate": "full_capture_subprocess_wall_seconds",
            "opendetect": "source_metrics.training_seconds",
            "artifact_bytes_measured_from_bound_runtime_files": True,
        },
        "sources": sources,
        "source_count": len(sources),
        "scenario_block_count": 102,
        "training_seeds": [647, 653, 659],
        "comparator_seed": 137,
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
            "selected_system_protocol": selected_protocol[
                "manifest_sha256"
            ],
            "selected_system_summary": selected_summary["manifest_sha256"],
            "selected_system_audit": selected_audit["manifest_sha256"],
            "comparative_protocol": comparative["manifest_sha256"],
        },
        "input_file_sha256": {
            "downstream_design": file_hash(downstream_design_path),
            "confirmation_protocol": file_hash(confirmation_protocol_path),
            "confirmation_summary": file_hash(confirmation_summary_path),
            "confirmation_audit": file_hash(confirmation_audit_path),
            "selected_system_protocol": file_hash(selected_protocol_path),
            "selected_system_summary": file_hash(selected_summary_path),
            "selected_system_audit": file_hash(selected_audit_path),
            "comparative_protocol": file_hash(comparative_protocol_path),
        },
        "implementation_sha256": verify_implementation(project_root),
        "claim_boundary": {
            "efficiency_only_not_effectiveness": True,
            "opendetect_seed137_reuse_not_an_accuracy_claim": True,
            "same_input_arrays_do_not_imply_same_training_split": True,
            "efficiency_failure_blocks_only_tier2": True,
            "no_metric_scenario_suite_seed_or_component_splicing": True,
        },
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--downstream-design", type=Path, required=True)
    parser.add_argument(
        "--confirmation-protocol", type=Path, required=True
    )
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument(
        "--selected-system-protocol", type=Path, required=True
    )
    parser.add_argument("--selected-system-summary", type=Path, required=True)
    parser.add_argument("--selected-system-audit", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--comparative-run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = create_protocol(
        project_root=args.project_root.resolve(),
        result_root=args.result_root.resolve(),
        downstream_design_path=args.downstream_design.resolve(),
        confirmation_protocol_path=args.confirmation_protocol.resolve(),
        confirmation_summary_path=args.confirmation_summary.resolve(),
        confirmation_audit_path=args.confirmation_audit.resolve(),
        selected_protocol_path=args.selected_system_protocol.resolve(),
        selected_summary_path=args.selected_system_summary.resolve(),
        selected_audit_path=args.selected_system_audit.resolve(),
        comparative_protocol_path=args.comparative_protocol.resolve(),
        comparative_run_root=args.comparative_run_root.resolve(),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
