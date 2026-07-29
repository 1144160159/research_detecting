from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from create_strict_v4_selected_system_preconfirmation_design import (
    ALGORITHMS,
    CORRUPTION_FAMILIES,
    FUTURE_IMPLEMENTATION_FILES,
    IMPLEMENTATION_FILES,
    MAIN_METHODS,
    SCHEMA as DESIGN_SCHEMA,
)


SCHEMA = "strict_v4_selected_system_preconfirmation_design_audit_v1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def audit(
    design_path: Path, project_root: Path
) -> dict[str, Any]:
    design = load(design_path)
    universe = design.get("universe", {})
    implementations = design.get("implementation_sha256", {})
    checks = {
        "design_is_canonical": (
            design.get("schema_version") == DESIGN_SCHEMA
            and design.get("manifest_sha256") == canonical_hash(design)
        ),
        "allowed_algorithms_exact": (
            design.get("allowed_selected_algorithms") == list(ALGORITHMS)
        ),
        "universe_exact": (
            universe.get("suite_count") == 7
            and universe.get("scenario_count") == 102
            and universe.get("training_seeds") == [647, 653, 659]
            and universe.get("source_task_count") == 306
            and universe.get("selected_candidate_capture_count") == 306
            and universe.get("fresh_opendetect_capture_count") == 306
            and universe.get("classic_main_methods") == list(MAIN_METHODS)
            and universe.get("corruption_families")
            == list(CORRUPTION_FAMILIES)
            and universe.get("paired_corruption_record_count") == 1530
        ),
        "implementation_hashes_match": (
            set(implementations) == set(IMPLEMENTATION_FILES)
            and all(
                (project_root / name).is_file()
                and implementations[name] == file_hash(project_root / name)
                for name in IMPLEMENTATION_FILES
            )
        ),
        "future_implementation_inventory_exact": (
            design.get("required_future_implementation")
            == list(FUTURE_IMPLEMENTATION_FILES)
        ),
        "source_hash_inventory_complete": (
            set(design.get("source_manifest_sha256", {}))
            == {
                "classic_main_protocol",
                "krc_source_protocol",
                "absolute_corruption_protocol",
                "comparative_corruption_protocol",
                "selected_system_adapter_design",
            }
            and set(design.get("source_file_sha256", {}))
            == set(design.get("source_manifest_sha256", {}))
            and all(design.get("source_manifest_sha256", {}).values())
            and all(design.get("source_file_sha256", {}).values())
        ),
        "formal_outputs_zero": all(
            int(value) == 0
            for value in design.get(
                "formal_output_counts_at_freeze", {}
            ).values()
        ),
        "claim_boundary_conservative": (
            design.get("claim_boundary", {}).get(
                "design_is_not_execution_or_effect"
            )
            is True
            and design.get("claim_boundary", {}).get(
                "comprehensive_sota_authorized_at_freeze"
            )
            is False
        ),
    }
    result: dict[str, Any] = {
        "schema_version": SCHEMA,
        "state": "complete",
        "design_manifest_sha256": design.get("manifest_sha256"),
        "design_file_sha256": file_hash(design_path),
        "checks": checks,
        "passed": all(checks.values()),
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--design", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = audit(args.design.resolve(), args.project_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open(
        "w", encoding="utf-8", newline="\n"
    ) as handle:
        handle.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "passed": result["passed"],
                "manifest_sha256": result["manifest_sha256"],
            },
            sort_keys=True,
        )
    )
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
