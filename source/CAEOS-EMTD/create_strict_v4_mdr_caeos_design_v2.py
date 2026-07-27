from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from select_mdr_caeos_weight import load


def revise(
    v1: Dict[str, Any],
    *,
    v1_file_sha256: str,
    implementation_sha256: Dict[str, str],
    result_count_at_revision: int,
) -> Dict[str, Any]:
    if (
        v1.get("schema_version") != "strict_v4_mdr_caeos_design_v1"
        or v1.get("manifest_sha256") != canonical_hash(v1)
    ):
        raise ValueError("canonical MDR v1 design required")
    if int(result_count_at_revision) != 0:
        raise ValueError("MDR design revision requires zero candidate results")
    value = {
        key: item
        for key, item in v1.items()
        if key not in {"schema_version", "manifest_sha256"}
    }
    value.update(
        {
            "schema_version": "strict_v4_mdr_caeos_design_v2",
            "status": "frozen_before_candidate_results",
            "supersedes_design_manifest_sha256": v1["manifest_sha256"],
            "supersedes_design_file_sha256": v1_file_sha256,
            "revision": {
                "reason": (
                    "make the configured robust classifier importable for "
                    "runtime serialization and bind the complete pilot "
                    "execution implementation"
                ),
                "algorithm_formula_changed": False,
                "seeds_changed": False,
                "weight_grid_changed": False,
                "scenario_or_gate_changed": False,
                "candidate_results_observed": 0,
            },
            "implementation_sha256": implementation_sha256,
            "candidate_result_count_at_freeze": 0,
        }
    )
    value["execution_boundary"] = {
        "execution_admitted": False,
        "missing_before_execution": [
            "canonical pilot execution protocol",
            "resource-idle watcher activation",
        ],
        "no_training_started_by_design_freeze": True,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1-design", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--implementation", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    implementations = {}
    for item in args.implementation:
        name, path = item.split("=", 1)
        implementations[name] = file_hash(Path(path))
    result_count = (
        sum(1 for _ in args.result_root.rglob("evaluation.json"))
        if args.result_root.exists()
        else 0
    )
    value = revise(
        load(args.v1_design),
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
