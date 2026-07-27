from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash


def load_json(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def revise(
    v1: Dict[str, Any],
    *,
    v1_file_sha256: str,
    implementation_sha256: Dict[str, str],
    result_count_at_revision: int,
) -> Dict[str, Any]:
    if (
        v1.get("schema_version") != "strict_v4_csr_caeos_design_v1"
        or v1.get("manifest_sha256") != canonical_hash(v1)
        or v1.get("candidate_result_count_at_freeze") != 0
    ):
        raise ValueError("canonical zero-result CSR v1 design required")
    if int(result_count_at_revision) != 0:
        raise ValueError("CSR v2 revision requires zero candidate results")
    required = {
        "routing_module",
        "runtime_module",
        "design_creator_v1",
        "design_creator_v2",
        "routing_test",
        "runtime_test",
    }
    if set(implementation_sha256) != required:
        raise ValueError("complete CSR runtime implementation binding required")
    value = {
        key: item
        for key, item in v1.items()
        if key not in {
            "schema_version",
            "manifest_sha256",
            "implementation_sha256",
            "execution_boundary",
        }
    }
    value.update(
        {
            "schema_version": "strict_v4_csr_caeos_design_v2",
            "status": "frozen_before_candidate_results",
            "supersedes_design_manifest_sha256": v1["manifest_sha256"],
            "supersedes_design_file_sha256": v1_file_sha256,
            "revision": {
                "reason": (
                    "bind the deployable risk-only runtime and its tests"
                ),
                "algorithm_formula_changed": False,
                "seeds_scenarios_weight_or_gates_changed": False,
                "candidate_results_observed": 0,
            },
            "implementation_sha256": implementation_sha256,
            "execution_boundary": {
                "execution_admitted": False,
                "missing_before_execution": [
                    "runtime capture implementation",
                    "canonical pilot execution protocol",
                    "resumable runner",
                    "independent summarizer and auditor",
                    "resource-idle watcher",
                ],
                "no_training_started_by_design_freeze": True,
            },
            "candidate_result_count_at_freeze": 0,
        }
    )
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-design", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--routing-module", type=Path, required=True)
    parser.add_argument("--runtime-module", type=Path, required=True)
    parser.add_argument("--design-creator-v1", type=Path, required=True)
    parser.add_argument("--routing-test", type=Path, required=True)
    parser.add_argument("--runtime-test", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result_count = (
        sum(1 for _ in args.result_root.rglob("evaluation.json"))
        if args.result_root.exists()
        else 0
    )
    implementations = {
        "routing_module": file_hash(args.routing_module),
        "runtime_module": file_hash(args.runtime_module),
        "design_creator_v1": file_hash(args.design_creator_v1),
        "design_creator_v2": file_hash(Path(__file__)),
        "routing_test": file_hash(args.routing_test),
        "runtime_test": file_hash(args.runtime_test),
    }
    value = revise(
        load_json(args.v1_design),
        v1_file_sha256=file_hash(args.v1_design),
        implementation_sha256=implementations,
        result_count_at_revision=result_count,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(value["manifest_sha256"])


if __name__ == "__main__":
    main()
