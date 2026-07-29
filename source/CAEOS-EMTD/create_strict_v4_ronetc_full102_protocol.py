from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from run_nested_gate_matrix import (
    CICIDS2017_SCENARIOS,
    CIC_IOT2023_SCENARIOS,
    CIC_TON_IOT_SCENARIOS,
    EDGE_IIOT_SCENARIOS,
    NF_CSE_SCENARIOS,
    NF_UNSW_SCENARIOS,
    USTC_TFC2016_SCENARIOS,
)


SUITES = {
    "nf_unsw": NF_UNSW_SCENARIOS,
    "cicids2017": CICIDS2017_SCENARIOS,
    "cic_iot2023": CIC_IOT2023_SCENARIOS,
    "cic_ton_iot": CIC_TON_IOT_SCENARIOS,
    "edge_iiot": EDGE_IIOT_SCENARIOS,
    "nf_cse": NF_CSE_SCENARIOS,
    "ustc_tfc2016": USTC_TFC2016_SCENARIOS,
}
SEED = 7
MODEL = "ronetc"
REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "provenance.json")
CACHE_ARGUMENTS = {
    "nf_unsw": ("--nf-unsw-csv", "--nf-unsw-max-per-class", 5000),
    "cicids2017": (
        "--cicids2017-csv",
        "--cicids2017-max-per-class",
        5000,
    ),
    "cic_iot2023": (
        "--cic-iot2023-csv",
        "--cic-iot2023-max-per-class",
        1000,
    ),
    "cic_ton_iot": (
        "--cic-ton-iot-csv",
        "--cic-ton-iot-max-per-class",
        1000,
    ),
    "edge_iiot": ("--edge-iiot-csv", "--edge-iiot-max-per-class", 1000),
    "nf_cse": ("--nf-cse-csv", "--nf-cse-max-per-class", 1000),
    "ustc_tfc2016": ("--ustc-csv", "--ustc-max-per-class", 3000),
}


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bound_cache_inputs(path: Path) -> dict[str, dict[str, Any]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("baseline manifest must be a JSON object")
    claimed = manifest.get("manifest_sha256")
    payload = dict(manifest)
    payload.pop("manifest_sha256", None)
    if (
        manifest.get("schema_version") != "strict_v4_baseline_manifest_v2"
        or claimed != canonical_hash(payload)
        or manifest.get("seed") != SEED
        or manifest.get("scenario_inference_units") != 102
    ):
        raise ValueError("invalid strict-v4 baseline manifest")
    caches = manifest.get("cache_artifacts", {})
    if set(caches) != set(CACHE_ARGUMENTS):
        raise ValueError("baseline cache suite coverage is not exact")
    for suite, evidence in caches.items():
        csv_path = Path(evidence["path"])
        sidecar_path = Path(f"{csv_path}.json")
        if (
            not csv_path.is_file()
            or not sidecar_path.is_file()
            or file_hash(csv_path) != evidence.get("sha256")
            or file_hash(sidecar_path) != evidence.get("sidecar_sha256")
        ):
            raise ValueError(f"baseline cache hash mismatch for {suite}")
    return caches


def build_tasks(run_root: Path) -> list[dict[str, Any]]:
    tasks = []
    for suite, scenarios in SUITES.items():
        for scenario, unknown_classes in scenarios.items():
            output_dir = run_root / suite / f"{scenario}_seed{SEED}_{MODEL}"
            tasks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "unknown_classes": unknown_classes,
                    "model": MODEL,
                    "seed": SEED,
                    "output_dir": str(output_dir),
                    "required_artifacts": list(REQUIRED_ARTIFACTS),
                }
            )
    identities = {
        (task["suite"], task["scenario"], task["model"], task["seed"])
        for task in tasks
    }
    if len(tasks) != 102 or len(identities) != 102:
        raise ValueError("RoNeTC protocol requires 102 unique strict-v4 tasks")
    return tasks


def build_protocol(
    project_root: Path,
    full_summary: Path,
    coverage_manifest: Path,
    baseline_manifest: Path,
    run_root: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    full_summary = full_summary.resolve()
    coverage_manifest = coverage_manifest.resolve()
    baseline_manifest = baseline_manifest.resolve()
    run_root = run_root.resolve()
    cache_inputs = bound_cache_inputs(baseline_manifest)
    implementation = {
        name: file_hash(project_root / name)
        for name in (
            "create_strict_v4_ronetc_full102_protocol.py",
            "run_neural_baseline_matrix.py",
            "train_neural_open_set.py",
            "caeos/ronetc.py",
            "summarize_strict_v4_ronetc_full102.py",
            "audit_strict_v4_ronetc_full102.py",
        )
    }
    tasks = build_tasks(run_root)
    existing_results = [
        str(Path(task["output_dir"]) / artifact)
        for task in tasks
        for artifact in REQUIRED_ARTIFACTS
        if (Path(task["output_dir"]) / artifact).exists()
    ]
    if existing_results:
        raise ValueError(
            "RoNeTC protocol must be frozen before results exist: "
            f"{existing_results[:3]}"
        )

    command = [
        "python",
        "run_neural_baseline_matrix.py",
        "--suite",
        "strict_v4_primary",
        "--scenarios",
        "all",
        "--models",
        MODEL,
        "--seeds",
        str(SEED),
        "--workers",
        "1",
    ]
    for suite in SUITES:
        csv_argument, maximum_argument, maximum = CACHE_ARGUMENTS[suite]
        command.extend(
            [
                csv_argument,
                cache_inputs[suite]["path"],
                maximum_argument,
                str(maximum),
            ]
        )
    command.extend(["--output-root", str(run_root)])
    protocol: dict[str, Any] = {
        "schema_version": "strict_v4_ronetc_full102_protocol_v1",
        "state": "frozen_zero_result",
        "purpose": (
            "Add the closest domain-nearest evidential traffic baseline to the "
            "strict-v4 102-scenario evidence table without expanding the "
            "classical seven-method main table."
        ),
        "baseline_scope": {
            "primary_domain_nearest": ["opendetect", "ronetc"],
            "opendetect_reuses_bound_full102_result": True,
            "ronetc_requires_fresh_full102_execution": True,
            "secondary_legacy39_only": ["arpl", "cade"],
            "secondary_methods_do_not_support_strict_v4_claim": True,
        },
        "source_evidence_sha256": {
            "strict_v4_full102_summary": file_hash(full_summary),
            "strict_v4_coverage_manifest": file_hash(coverage_manifest),
            "strict_v4_baseline_manifest_v2": file_hash(
                baseline_manifest
            ),
        },
        "implementation_sha256": implementation,
        "universe": {
            "suite_count": 7,
            "scenario_count": 102,
            "task_count": 102,
            "seed": SEED,
            "model": MODEL,
            "suite_scenario_counts": {
                suite: len(scenarios) for suite, scenarios in SUITES.items()
            },
        },
        "tasks": tasks,
        "command": command,
        "execution_gate": {
            "final_self_algorithm_selection_must_be_terminal": True,
            "krc_rrc_pug_training_and_capture_process_count": 0,
            "gpu_compute_process_count": 0,
            "load1_not_above_25pct_logical_cpus_for_three_polls": True,
            "result_root_must_remain_empty_before_launch": True,
        },
        "evaluation_contract": {
            "same_seed7_cache_and_split_protocol_as_bound_full102_summary": True,
            "unknown_test_samples_never_used_for_fit_selection_or_threshold": True,
            "known_validation_only_threshold": True,
            "required_artifacts": list(REQUIRED_ARTIFACTS),
            "metrics": [
                "known_macro_f1",
                "unknown_auroc",
                "unknown_aupr",
                "unknown_fpr95",
                "oscr",
            ],
            "development_comparison_target": "opendetect",
            "future_comprehensive_comparison_target": (
                "final_self_algorithm"
            ),
            "scenario_complete_before_aggregation": True,
            "suite_balanced_reporting": True,
        },
        "analysis_contract": {
            "opendetect_root": str(
                project_root
                / "runs/strict_v4_full103_independent_baselines_seed7"
            ),
            "baseline_manifest": str(baseline_manifest),
            "full103_summary": str(full_summary),
            "required_outputs_after_execution": [
                "summary.json",
                "summary.md",
                "audit.json",
                "execution_complete.json",
            ],
            "summary_implementation": (
                "summarize_strict_v4_ronetc_full102.py"
            ),
            "independent_audit_implementation": (
                "audit_strict_v4_ronetc_full102.py"
            ),
        },
        "paired_input_contract": {
            "source": "strict_v4_baseline_manifest_v2.cache_artifacts",
            "suite_count": 7,
            "csv_sha256": {
                suite: evidence["sha256"]
                for suite, evidence in cache_inputs.items()
            },
            "sidecar_sha256": {
                suite: evidence["sidecar_sha256"]
                for suite, evidence in cache_inputs.items()
            },
            "postselection_corruption_cache_is_not_used": True,
        },
        "claim_boundary": {
            "seed7_is_development_screen": True,
            "authorizes_comprehensive_sota_before_execution": False,
            "authorizes_algorithm_selection": False,
            "authorizes_replacing_classical_main_seven": False,
            "arpl_or_cade_legacy39_numbers_are_not_strict_v4_results": True,
        },
        "formal_output_counts_at_freeze": {
            "metrics": 0,
            "scores": 0,
            "provenance": 0,
            "summary": 0,
            "audit": 0,
            "completion": 0,
        },
    }
    protocol["manifest_sha256"] = canonical_hash(protocol)
    return protocol


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze the strict-v4 RoNeTC full102 zero-result protocol."
    )
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--full-summary", type=Path, required=True)
    parser.add_argument("--coverage-manifest", type=Path, required=True)
    parser.add_argument("--baseline-manifest", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    protocol = build_protocol(
        args.project_root,
        args.full_summary,
        args.coverage_manifest,
        args.baseline_manifest,
        args.run_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(protocol, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "manifest_sha256": protocol["manifest_sha256"],
                "tasks": len(protocol["tasks"]),
            }
        )
    )


if __name__ == "__main__":
    main()
