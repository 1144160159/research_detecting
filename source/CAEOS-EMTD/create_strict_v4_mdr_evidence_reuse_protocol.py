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


def build_sources(
    confirmation_protocol: Dict[str, Any], capture_root: Path
) -> list[Dict[str, Any]]:
    sources = []
    for task in confirmation_protocol["confirmation"]["tasks"]:
        suite = str(task["suite"])
        scenario = str(task["scenario"])
        training_seed = int(task["training_seed"])
        corruption_seed = int(task["corruption_seed"])
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
                f"invalid MDR capture: {suite}/{scenario}/seed{training_seed}"
            )
        sources.append(
            {
                "suite": suite,
                "scenario": scenario,
                "training_seed": training_seed,
                "corruption_seed": corruption_seed,
                "capture_dir": str(capture_dir.resolve()),
                "capture_manifest_file_sha256": file_hash(manifest_path),
                "runtime_artifact_sha256": manifest[
                    "runtime_artifact_sha256"
                ],
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
        raise ValueError("exactly 306 unique MDR captures required")
    return sources


def implementation_hashes(
    project_root: Path, relatives: Iterable[str]
) -> Dict[str, str]:
    output = {}
    for relative in sorted(set(relatives)):
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing optimization file: {relative}")
        output[relative] = file_hash(path)
    return output


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
    observed_outputs: int,
) -> Dict[str, Any]:
    require_canonical(
        design,
        "strict_v4_mdr_evidence_reuse_design_v1",
        "MDR evidence-reuse design",
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
    if int(observed_outputs) != 0:
        raise ValueError("optimization protocol must freeze before outputs")
    if (
        selection.get("selected_algorithm") != "mdr_caeos_v1"
        or selection.get("mdr_confirmation_passes") is not True
        or selection.get("protocol_manifest_sha256")
        != confirmation_protocol["manifest_sha256"]
        or selection.get("summary_manifest_sha256")
        != confirmation_summary["manifest_sha256"]
        or confirmation_summary.get("decision", {}).get("passes") is not True
        or confirmation_audit.get("passes") is not True
    ):
        raise ValueError("positive canonical MDR confirmation is required")
    required = {
        "create_strict_v4_mdr_evidence_reuse_protocol.py",
        "evaluate_mdr_evidence_reuse.py",
        "run_strict_v4_mdr_evidence_reuse.py",
        "summarize_strict_v4_mdr_evidence_reuse.py",
        "audit_strict_v4_mdr_evidence_reuse.py",
        "scripts/wait_and_run_strict_v4_mdr_evidence_reuse.sh",
        "caeos/mdr_evidence_reuse_runtime.py",
        "caeos/mdr_runtime.py",
        "caeos/pairwise_runtime.py",
    }
    if not required.issubset(implementation_sha256):
        raise ValueError("optimization implementation hashes incomplete")
    identities = {
        (
            str(source["suite"]),
            str(source["scenario"]),
            int(source["training_seed"]),
        )
        for source in sources
    }
    scenario_blocks = {
        (str(source["suite"]), str(source["scenario"]))
        for source in sources
    }
    training_seeds = sorted(
        {int(source["training_seed"]) for source in sources}
    )
    if (
        len(sources) != 306
        or len(identities) != 306
        or len(scenario_blocks) != 102
        or len(training_seeds) != 3
    ):
        raise ValueError("306 captures in 102 three-seed blocks required")
    value: Dict[str, Any] = {
        "schema_version": (
            "strict_v4_mdr_evidence_reuse_protocol_v1"
        ),
        "status": (
            "frozen_after_positive_mdr_confirmation_before_optimization_outputs"
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
        "conditions": list(
            design["formal_equivalence"]["conditions"]
        ),
        "fixed_severity": confirmation_protocol["confirmation"][
            "fixed_severity"
        ],
        "coverage_manifest_sha256": confirmation_protocol[
            "coverage_manifest_sha256"
        ],
        "equivalence": design["formal_equivalence"],
        "benchmark": design["benchmark"],
        "decision": design["decision"],
        "sources": sources,
        "source_count": len(sources),
        "scenario_block_count": 102,
        "training_seeds": training_seeds,
        "expected_condition_count": 1836,
        "formal_output_count_at_freeze": 0,
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
    values = {name: load(path) for name, path in paths.items()}
    relatives = [
        "create_strict_v4_mdr_evidence_reuse_protocol.py",
        "evaluate_mdr_evidence_reuse.py",
        "run_strict_v4_mdr_evidence_reuse.py",
        "summarize_strict_v4_mdr_evidence_reuse.py",
        "audit_strict_v4_mdr_evidence_reuse.py",
        "scripts/wait_and_run_strict_v4_mdr_evidence_reuse.sh",
        "caeos/mdr_evidence_reuse_runtime.py",
        "caeos/mdr_runtime.py",
        "caeos/pairwise_runtime.py",
    ]
    observed = (
        len(list(args.run_root.glob("**/optimization.json")))
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
        sources=build_sources(
            values["confirmation_protocol"], args.capture_root
        ),
        implementation_sha256=implementation_hashes(
            args.project_root, relatives
        ),
        input_file_sha256={
            name: file_hash(path) for name, path in paths.items()
        },
        observed_outputs=observed,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
