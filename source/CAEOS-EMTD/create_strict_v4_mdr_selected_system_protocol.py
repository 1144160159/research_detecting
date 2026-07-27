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
    output = {}
    for relative in relatives:
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing MDR selected-system implementation: {relative}"
            )
        output[relative] = file_hash(path)
    for relative in (
        "capture_mdr_caeos_runtime.py",
        "caeos/mdr_runtime.py",
        "caeos/pairwise_runtime.py",
    ):
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(
                f"missing MDR selected-system runtime source: {relative}"
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
        manifest = load(manifest_path)
        artifact = capture_dir / str(manifest.get("runtime_artifact", ""))
        inputs = capture_dir / str(manifest.get("evaluation_inputs", ""))
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
            or file_hash(artifact) != manifest.get("runtime_artifact_sha256")
            or file_hash(inputs) != manifest.get("evaluation_inputs_sha256")
        ):
            raise ValueError(
                "invalid MDR confirmation capture for selected-system "
                f"benchmark: {suite}/{scenario}/seed{training_seed}"
            )
        sources.append(
            {
                "suite": suite,
                "scenario": scenario,
                "training_seed": training_seed,
                "capture_dir": str(capture_dir.resolve()),
                "capture_manifest_file_sha256": file_hash(manifest_path),
                "mdr_runtime_sha256": manifest["runtime_artifact_sha256"],
                "evaluation_inputs_sha256": manifest[
                    "evaluation_inputs_sha256"
                ],
            }
        )
    identities = {
        (item["suite"], item["scenario"], item["training_seed"])
        for item in sources
    }
    if len(sources) != 306 or len(identities) != 306:
        raise ValueError("exactly 306 unique MDR captures are required")
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
    sources: list[Dict[str, Any]],
    implementation_sha256: Dict[str, str],
    input_file_sha256: Dict[str, str],
    observed_benchmarks: int,
) -> Dict[str, Any]:
    require_canonical(
        design,
        "strict_v4_mdr_selected_system_design_v1",
        "MDR selected-system design",
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
    if int(observed_benchmarks) != 0:
        raise ValueError("selected-system protocol must freeze before outputs")
    if (
        selection.get("selected_algorithm") != "mdr_caeos_v1"
        or selection.get("mdr_confirmation_passes") is not True
        or selection.get("protocol_manifest_sha256")
        != confirmation_protocol["manifest_sha256"]
        or selection.get("summary_manifest_sha256")
        != confirmation_summary["manifest_sha256"]
        or confirmation_summary.get("decision", {}).get("passes")
        is not True
        or confirmation_audit.get("passes") is not True
        or confirmation_audit.get("protocol_manifest_sha256")
        != confirmation_protocol["manifest_sha256"]
        or confirmation_audit.get("summary_manifest_sha256")
        != confirmation_summary["manifest_sha256"]
    ):
        raise ValueError("positive canonical MDR confirmation is required")
    identities = {
        (item["suite"], item["scenario"], int(item["training_seed"]))
        for item in sources
    }
    blocks: Dict[tuple[str, str], set[int]] = {}
    for item in sources:
        key = (str(item["suite"]), str(item["scenario"]))
        blocks.setdefault(key, set()).add(int(item["training_seed"]))
    if (
        len(sources) != 306
        or len(identities) != 306
        or len(blocks) != 102
        or any(seeds != {347, 349, 353} for seeds in blocks.values())
    ):
        raise ValueError("selected-system source universe must contain 306 captures")
    required = set(design["required_implementation"])
    if not required.issubset(implementation_sha256):
        raise ValueError("selected-system implementation hashes are incomplete")
    inference = design["same_hardware_inference"]
    if (
        inference["batch_sizes"] != [1, 64, 512]
        or int(inference["warmup_repetitions"]) != 5
        or int(inference["timed_repetitions"]) != 30
    ):
        raise ValueError("selected-system benchmark design drifted")
    value: Dict[str, Any] = {
        "schema_version": "strict_v4_mdr_selected_system_protocol_v1",
        "status": (
            "frozen_after_positive_mdr_confirmation_before_system_outputs"
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
        "benchmark": {
            "batch_sizes": list(inference["batch_sizes"]),
            "warmup_repetitions": int(inference["warmup_repetitions"]),
            "timed_repetitions": int(inference["timed_repetitions"]),
            "method_order": "alternate_by_timed_repetition",
            "exact_batch_construction": (
                "cycle_source_rows_in_original_order_without_label_use"
            ),
            "same_inputs_and_process_required": True,
            "gpu_used": False,
        },
        "aggregation": design["aggregation"],
        "deployability_gate": design["deployability_gate"],
        "strict_efficiency_superiority_gate": design[
            "strict_efficiency_superiority_gate"
        ],
        "training_and_artifact_cost": design["training_and_artifact_cost"],
        "sources": sources,
        "source_count": len(sources),
        "scenario_block_count": len(blocks),
        "training_seeds": [347, 349, 353],
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
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--confirmation-protocol", type=Path, required=True)
    parser.add_argument("--confirmation-summary", type=Path, required=True)
    parser.add_argument("--confirmation-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    paths = {
        "design": args.design,
        "selection": args.selection,
        "confirmation_protocol": args.confirmation_protocol,
        "confirmation_summary": args.confirmation_summary,
        "confirmation_audit": args.confirmation_audit,
    }
    design = load(args.design)
    confirmation_protocol = load(args.confirmation_protocol)
    observed = (
        len(list(args.run_root.glob("**/benchmark.json")))
        if args.run_root.exists()
        else 0
    )
    value = create_protocol(
        project_root=args.project_root,
        run_root=args.run_root,
        design=design,
        selection=load(args.selection),
        confirmation_protocol=confirmation_protocol,
        confirmation_summary=load(args.confirmation_summary),
        confirmation_audit=load(args.confirmation_audit),
        sources=build_sources(confirmation_protocol, args.capture_root),
        implementation_sha256=verify_implementation(
            args.project_root, design["required_implementation"]
        ),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
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
