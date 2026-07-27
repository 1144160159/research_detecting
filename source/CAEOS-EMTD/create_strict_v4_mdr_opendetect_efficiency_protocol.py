from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


def load(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_canonical(
    value: Dict[str, Any], schema: str, label: str
) -> None:
    if value.get("schema_version") != schema:
        raise ValueError(f"unexpected {label} schema")
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError(f"{label} canonical SHA mismatch")


def verify_implementation(
    project_root: Path, relatives: Iterable[str]
) -> Dict[str, str]:
    required = set(relatives) | {
        "caeos/mdr_runtime.py",
        "caeos/open_detect_runtime.py",
    }
    output = {}
    for relative in sorted(required):
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing MDR-OpenDetect efficiency implementation: {relative}"
            )
        output[relative] = file_hash(path)
    return output


def build_comparators(
    comparative: Dict[str, Any], comparative_run_root: Path
) -> Dict[tuple[str, str], Dict[str, Any]]:
    require_canonical(
        comparative,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative corruption protocol",
    )
    output: Dict[tuple[str, str], Dict[str, Any]] = {}
    for source in comparative["source_registry"]:
        if int(source["seed"]) != 137:
            continue
        suite = str(source["suite"])
        scenario = str(source["scenario"])
        key = (suite, scenario)
        if key in output:
            raise ValueError(f"duplicate seed137 OpenDetect source: {key}")
        capture_dir = (
            comparative_run_root
            / "blocks"
            / suite
            / scenario
            / "seed137"
            / "comparator_capture"
        )
        manifest_path = capture_dir / "capture_manifest.json"
        manifest = load(manifest_path)
        artifact = capture_dir / str(
            manifest.get("deployment_artifact", "")
        )
        metrics_path = Path(source["comparator_root"]) / "metrics.json"
        metrics = load(metrics_path)
        expected_hashes = source["comparator_file_sha256"]
        split = metrics.get("split_metadata", {}).get(
            "split_fingerprint", {}
        )
        if (
            manifest.get("schema_version")
            != "strict_v4_opendetect_runtime_capture_v1"
            or manifest.get("equivalence", {}).get("passes") is not True
            or not artifact.is_file()
            or not metrics_path.is_file()
            or file_hash(artifact)
            != manifest.get("deployment_artifact_sha256")
            or file_hash(metrics_path) != expected_hashes.get("metrics.json")
            or manifest.get("source_artifact_sha256", {}).get("metrics.json")
            != expected_hashes.get("metrics.json")
            or str(Path(manifest.get("source_run", "")).resolve())
            != str(Path(source["comparator_root"]).resolve())
            or split.get("combined") != source.get("split_fingerprint")
            or not isinstance(metrics.get("training_seconds"), (int, float))
            or float(metrics["training_seconds"]) <= 0.0
        ):
            raise ValueError(
                f"invalid frozen OpenDetect runtime: {suite}/{scenario}"
            )
        output[key] = {
            "suite": suite,
            "scenario": scenario,
            "comparator_seed": 137,
            "capture_dir": str(capture_dir.resolve()),
            "capture_manifest_file_sha256": file_hash(manifest_path),
            "runtime_artifact_sha256": manifest[
                "deployment_artifact_sha256"
            ],
            "runtime_artifact_bytes": int(
                manifest["deployment_artifact_bytes"]
            ),
            "runtime_device": str(
                manifest.get("runtime_evidence", {}).get("device", "")
            ),
            "source_metrics_path": str(metrics_path.resolve()),
            "source_metrics_file_sha256": file_hash(metrics_path),
            "source_training_seconds": float(metrics["training_seconds"]),
            "source_training_seconds_field": "training_seconds",
            "split_fingerprint": str(source["split_fingerprint"]),
        }
    if len(output) != 102:
        raise ValueError("exactly 102 seed137 OpenDetect runtimes are required")
    return output


def build_sources(
    confirmation_protocol: Dict[str, Any],
    capture_root: Path,
    comparators: Dict[tuple[str, str], Dict[str, Any]],
) -> list[Dict[str, Any]]:
    sources = []
    for task in confirmation_protocol["confirmation"]["tasks"]:
        suite = str(task["suite"])
        scenario = str(task["scenario"])
        training_seed = int(task["training_seed"])
        key = (suite, scenario)
        if key not in comparators:
            raise ValueError(f"missing OpenDetect comparator for {key}")
        capture_dir = (
            capture_root / suite / scenario / f"seed{training_seed}"
        )
        manifest_path = capture_dir / "capture_manifest.json"
        execution_path = capture_dir / "capture_execution.json"
        manifest = load(manifest_path)
        execution = load(execution_path)
        artifact = capture_dir / str(manifest.get("runtime_artifact", ""))
        inputs = capture_dir / str(manifest.get("evaluation_inputs", ""))
        split = manifest.get("split_fingerprint", {})
        if (
            manifest.get("schema_version")
            != "strict_v4_mdr_caeos_runtime_capture_v1"
            or manifest.get("state") != "complete"
            or manifest.get("task")
            != {"suite": suite, "scenario": scenario}
            or int(manifest.get("training_seed", -1)) != training_seed
            or manifest.get("roundtrip", {}).get("passes") is not True
            or not artifact.is_file()
            or not inputs.is_file()
            or execution.get("schema_version")
            != "strict_v4_mdr_caeos_capture_execution_v1"
            or execution.get("manifest_sha256") != canonical_hash(execution)
            or execution.get("capture_manifest_file_sha256")
            != file_hash(manifest_path)
            or float(execution.get("total_capture_wall_seconds", -1.0))
            <= 0.0
            or file_hash(artifact) != manifest.get("runtime_artifact_sha256")
            or file_hash(inputs) != manifest.get("evaluation_inputs_sha256")
        ):
            raise ValueError(
                "invalid MDR confirmation capture for OpenDetect efficiency: "
                f"{suite}/{scenario}/seed{training_seed}"
            )
        sources.append(
            {
                "suite": suite,
                "scenario": scenario,
                "training_seed": training_seed,
                "candidate": {
                    "capture_dir": str(capture_dir.resolve()),
                    "capture_manifest_file_sha256": file_hash(manifest_path),
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
                    "split_fingerprint": split,
                },
                "comparator": dict(comparators[key]),
            }
        )
    identities = {
        (item["suite"], item["scenario"], item["training_seed"])
        for item in sources
    }
    if len(sources) != 306 or len(identities) != 306:
        raise ValueError("exactly 306 unique MDR benchmark sources required")
    blocks: Dict[tuple[str, str], set[int]] = {}
    for item in sources:
        key = (str(item["suite"]), str(item["scenario"]))
        blocks.setdefault(key, set()).add(int(item["training_seed"]))
    if (
        len(blocks) != 102
        or any(seeds != {347, 349, 353} for seeds in blocks.values())
    ):
        raise ValueError("MDR benchmark source matrix is incomplete")
    return sources


def create_protocol(
    *,
    project_root: Path,
    run_root: Path,
    design: Dict[str, Any],
    selection: Dict[str, Any],
    confirmation_protocol: Dict[str, Any],
    confirmation_summary: Dict[str, Any],
    confirmation_audit: Dict[str, Any],
    selected_system_protocol: Dict[str, Any],
    selected_system_summary: Dict[str, Any],
    selected_system_audit: Dict[str, Any],
    comparative_protocol: Dict[str, Any],
    sources: list[Dict[str, Any]],
    implementation_sha256: Dict[str, str],
    input_file_sha256: Dict[str, str],
    observed_benchmarks: int,
) -> Dict[str, Any]:
    require_canonical(
        design,
        "strict_v4_mdr_opendetect_efficiency_design_v1",
        "MDR-OpenDetect efficiency design",
    )
    require_canonical(
        selection,
        "strict_v4_final_self_algorithm_selection_v2",
        "final algorithm selection",
    )
    require_canonical(
        confirmation_protocol,
        "strict_v4_mdr_caeos_confirmation_protocol_v1",
        "MDR confirmation protocol",
    )
    require_canonical(
        confirmation_summary,
        "strict_v4_mdr_caeos_confirmation_summary_v1",
        "MDR confirmation summary",
    )
    require_canonical(
        confirmation_audit,
        "strict_v4_mdr_caeos_confirmation_audit_v1",
        "MDR confirmation audit",
    )
    require_canonical(
        selected_system_protocol,
        "strict_v4_mdr_selected_system_protocol_v1",
        "MDR selected-system protocol",
    )
    require_canonical(
        selected_system_summary,
        "strict_v4_mdr_selected_system_summary_v1",
        "MDR selected-system summary",
    )
    require_canonical(
        selected_system_audit,
        "strict_v4_mdr_selected_system_audit_v1",
        "MDR selected-system audit",
    )
    require_canonical(
        comparative_protocol,
        "strict_v4_comparative_corruption_protocol_v2",
        "comparative corruption protocol",
    )
    if int(observed_benchmarks) != 0:
        raise ValueError("efficiency protocol must freeze before outputs")
    if (
        selection.get("selected_algorithm") != "mdr_caeos_v1"
        or selection.get("mdr_confirmation_passes") is not True
        or confirmation_summary.get("decision", {}).get("passes") is not True
        or confirmation_audit.get("passes") is not True
        or selected_system_summary.get("deployability_decision", {}).get(
            "passes"
        )
        is not True
        or selected_system_audit.get("passes") is not True
        or selected_system_audit.get("deployability_gate_passes") is not True
        or selected_system_summary.get("protocol_manifest_sha256")
        != selected_system_protocol["manifest_sha256"]
        or selected_system_audit.get("protocol_manifest_sha256")
        != selected_system_protocol["manifest_sha256"]
        or selected_system_audit.get("summary_manifest_sha256")
        != selected_system_summary["manifest_sha256"]
    ):
        raise ValueError(
            "positive canonical MDR confirmation and deployability required"
        )
    selected_sources = {
        (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["training_seed"]),
        ): item
        for item in selected_system_protocol["sources"]
    }
    for item in sources:
        key = (
            str(item["suite"]),
            str(item["scenario"]),
            int(item["training_seed"]),
        )
        selected = selected_sources.get(key)
        if (
            selected is None
            or selected["capture_manifest_file_sha256"]
            != item["candidate"]["capture_manifest_file_sha256"]
            or selected["mdr_runtime_sha256"]
            != item["candidate"]["runtime_artifact_sha256"]
            or selected["evaluation_inputs_sha256"]
            != item["candidate"]["evaluation_inputs_sha256"]
        ):
            raise ValueError("selected-system MDR source binding mismatch")
    required = set(design["required_implementation"])
    if not required.issubset(implementation_sha256):
        raise ValueError("efficiency implementation hashes are incomplete")
    benchmark = design["benchmark"]
    if (
        benchmark["batch_sizes"] != [1, 64, 512]
        or int(benchmark["warmup_repetitions"]) != 5
        or int(benchmark["timed_repetitions"]) != 30
    ):
        raise ValueError("MDR-OpenDetect benchmark design drifted")
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_opendetect_efficiency_protocol_v1"
        ),
        "status": (
            "frozen_after_positive_mdr_deployability_before_efficiency_outputs"
        ),
        "selected_algorithm": "mdr_caeos_v1",
        "design_manifest_sha256": design["manifest_sha256"],
        "selection_manifest_sha256": selection["manifest_sha256"],
        "confirmation_protocol_manifest_sha256": confirmation_protocol[
            "manifest_sha256"
        ],
        "confirmation_summary_manifest_sha256": confirmation_summary[
            "manifest_sha256"
        ],
        "confirmation_audit_manifest_sha256": confirmation_audit[
            "manifest_sha256"
        ],
        "selected_system_protocol_manifest_sha256": selected_system_protocol[
            "manifest_sha256"
        ],
        "selected_system_summary_manifest_sha256": selected_system_summary[
            "manifest_sha256"
        ],
        "selected_system_audit_manifest_sha256": selected_system_audit[
            "manifest_sha256"
        ],
        "comparative_protocol_manifest_sha256": comparative_protocol[
            "manifest_sha256"
        ],
        "benchmark": {
            **benchmark,
            "exact_batch_construction": (
                "cycle_mdr_evaluation_rows_without_label_use"
            ),
            "same_inputs_and_process_required": True,
        },
        "aggregation": design["aggregation"],
        "strict_efficiency_superiority_gate": design[
            "strict_efficiency_superiority_gate"
        ],
        "cost_policy": {
            **design["cost"],
            "opendetect_source_metrics_actual_field": "training_seconds",
            "field_resolution": (
                "training_seconds is the recorded elapsed training wall time"
            ),
            "strict_fit_gate_candidate_measure": (
                "full_capture_subprocess_wall_seconds"
            ),
            "design_tightening": (
                "use complete measured capture wall instead of the frozen "
                "lower-bound diagnostic"
            ),
        },
        "sources": sources,
        "source_count": len(sources),
        "scenario_block_count": 102,
        "training_seeds": [347, 349, 353],
        "comparator_seed": 137,
        "expected_benchmark_count": 306,
        "benchmark_count_at_freeze": 0,
        "paths": {
            "project_root": str(project_root.resolve()),
            "run_root": str(run_root.resolve()),
        },
        "input_file_sha256": input_file_sha256,
        "implementation_sha256": dict(
            sorted(implementation_sha256.items())
        ),
        "claim_boundary": design["claim_boundary"],
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--comparative-run-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--confirmation-protocol", type=Path, required=True)
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument("--selected-system-protocol", type=Path, required=True)
    parser.add_argument("--selected-system-summary", type=Path, required=True)
    parser.add_argument("--selected-system-audit", type=Path, required=True)
    parser.add_argument("--comparative-protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    named_paths = {
        "design": args.design,
        "selection": args.selection,
        "confirmation_protocol": args.confirmation_protocol,
        "confirmation_summary": args.confirmation_summary,
        "confirmation_audit": args.confirmation_audit,
        "selected_system_protocol": args.selected_system_protocol,
        "selected_system_summary": args.selected_system_summary,
        "selected_system_audit": args.selected_system_audit,
        "comparative_protocol": args.comparative_protocol,
    }
    values = {name: load(path) for name, path in named_paths.items()}
    comparators = build_comparators(
        values["comparative_protocol"], args.comparative_run_root
    )
    sources = build_sources(
        values["confirmation_protocol"], args.capture_root, comparators
    )
    observed = (
        len(list(args.run_root.glob("**/benchmark.json")))
        if args.run_root.exists()
        else 0
    )
    value = create_protocol(
        project_root=args.project_root,
        run_root=args.run_root,
        design=values["design"],
        selection=values["selection"],
        confirmation_protocol=values["confirmation_protocol"],
        confirmation_summary=values["confirmation_summary"],
        confirmation_audit=values["confirmation_audit"],
        selected_system_protocol=values["selected_system_protocol"],
        selected_system_summary=values["selected_system_summary"],
        selected_system_audit=values["selected_system_audit"],
        comparative_protocol=values["comparative_protocol"],
        sources=sources,
        implementation_sha256=verify_implementation(
            args.project_root,
            values["design"]["required_implementation"],
        ),
        input_file_sha256={
            name: file_hash(path) for name, path in named_paths.items()
        },
        observed_benchmarks=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
