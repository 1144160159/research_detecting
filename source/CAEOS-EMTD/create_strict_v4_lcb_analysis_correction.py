from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import canonical_hash


FROZEN_ANALYZER = "analyze_strict_v4_lcb_tail_aware_pilot.py"
CORRECTED_ANALYZER = "analyze_strict_v4_lcb_tail_aware_pilot_v2.py"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_correction(
    protocol: dict[str, Any],
    *,
    protocol_file_sha256: str,
    corrected_analyzer_sha256: str,
) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_lcb_tail_aware_pilot_protocol_v1":
        raise ValueError("unexpected LCB source protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("LCB source protocol SHA mismatch")
    frozen_sha = protocol.get("implementation_sha256", {}).get(FROZEN_ANALYZER)
    if not frozen_sha:
        raise ValueError("frozen LCB analyzer SHA is absent")
    correction: dict[str, Any] = {
        "schema_version": "strict_v4_lcb_analysis_schema_correction_v1",
        "status": "post_run_analysis_only_correction",
        "source_protocol_file_sha256": protocol_file_sha256,
        "source_protocol_manifest_sha256": protocol["manifest_sha256"],
        "frozen_analyzer": {
            "path": FROZEN_ANALYZER,
            "sha256": frozen_sha,
        },
        "corrected_analyzer": {
            "path": CORRECTED_ANALYZER,
            "sha256": corrected_analyzer_sha256,
        },
        "correction": {
            "reason": (
                "the frozen analyzer expected full CLI parameters in metrics.arguments, "
                "while the deployed schema stores a compact arguments block and the complete "
                "executed command in provenance.json"
            ),
            "allowed_change": (
                "bind the frozen policy to deployed risk_policy fields and bind all frozen "
                "runtime parameters to provenance.command"
            ),
            "training_outputs_unchanged": True,
            "scenario_set_unchanged": True,
            "candidate_parameters_unchanged": True,
            "selection_and_expansion_gates_unchanged": True,
            "test_labels_used_for_new_parameter_selection": False,
        },
    }
    correction["manifest_sha256"] = canonical_hash(correction)
    return correction


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = args.source_protocol.read_bytes()
    protocol = json.loads(raw.decode("utf-8"))
    correction = create_correction(
        protocol,
        protocol_file_sha256=hashlib.sha256(raw).hexdigest(),
        corrected_analyzer_sha256=file_hash(
            args.project_root / CORRECTED_ANALYZER
        ),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(correction, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(correction["manifest_sha256"])


if __name__ == "__main__":
    main()
