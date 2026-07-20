from __future__ import annotations

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--superseded-manifest", type=Path, required=True)
    parser.add_argument("--failure-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    old = json.loads(args.superseded_manifest.read_text(encoding="utf-8"))
    if old.get("schema_version") != "strict_v4_full103_coverage_manifest_v1":
        raise ValueError("unexpected superseded coverage manifest schema")
    if old.get("manifest_sha256") != canonical_hash(old):
        raise ValueError("superseded coverage manifest SHA mismatch")
    failure_text = args.failure_log.read_text(encoding="utf-8", errors="replace")
    expected_error = "unknown classes not found: ['Uploading_Attack']"
    if expected_error not in failure_text:
        raise ValueError("failure log does not prove the Uploading_Attack cache error")

    payload: dict[str, Any] = deepcopy(old)
    payload["schema_version"] = "strict_v4_coverage_manifest_v2"
    payload["status"] = "coverage_corrected_before_summary"
    payload["scenario_inference_units"] = 102
    scenarios = payload["scenario_registry"]["cic_iot2023"]["scenarios"]
    if scenarios.count("uploading_attack") != 1:
        raise ValueError("superseded manifest does not contain uploading_attack once")
    scenarios.remove("uploading_attack")
    payload["scenario_registry"]["cic_iot2023"]["count"] = 32
    payload["expected_runs"] = {
        "pairwise_caeos": 102,
        "mlp_openmax": 102,
        "fixed_fusion_reports": 102,
    }
    payload["superseded_manifest_sha256"] = old["manifest_sha256"]
    payload["coverage_correction"] = {
        "excluded_suite": "cic_iot2023",
        "excluded_scenario": "uploading_attack",
        "source_label": "Uploading_Attack",
        "reason": "source label absent from the frozen group-supported cache",
        "failure_log_sha256": file_hash(args.failure_log),
        "performed_after_partial_coverage_results": True,
        "performed_before_metric_summary_or_baseline_results": True,
        "result_metrics_used_for_decision": False,
    }
    payload["coverage_run_implementation_sha256"] = deepcopy(
        old["implementation_sha256"]
    )
    payload["post_correction_implementation_sha256"] = {
        relative: file_hash(project_root / relative)
        for relative in payload["implementation_sha256"]
    }
    payload["post_correction_implementation_sha256"][
        "create_strict_v4_coverage_correction.py"
    ] = file_hash(Path(__file__))
    payload.pop("manifest_sha256", None)
    payload["manifest_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "schema_version": payload["schema_version"],
        "scenario_inference_units": payload["scenario_inference_units"],
        "cic_iot2023_scenarios": payload["scenario_registry"]["cic_iot2023"]["count"],
        "superseded_manifest_sha256": payload["superseded_manifest_sha256"],
        "manifest_sha256": payload["manifest_sha256"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
