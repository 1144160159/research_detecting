from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from audit_opendetect_deployment_bundle import audit as audit_opendetect
from audit_pairwise_deployment_bundle import audit_capture as audit_pairwise
from audit_vgrf_deployment_bundle import audit_capture as audit_vgrf
from capture_opendetect_deployment_bundle import capture as capture_opendetect
from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)
from run_strict_v4_vgrf_selected_system_seed317 import (
    load,
    replace_value,
)


def source_roots(record: dict[str, Any]) -> dict[str, Path]:
    roots = (
        record["source_roots"]
        if record["source_mode"] == "frozen_selection_artifacts"
        else record["run_output_roots"]
    )
    return {name: Path(value) for name, value in roots.items()}


def require_active_implementation(
    protocol: dict[str, Any], project: Path, name: str
) -> Path:
    path = project / name
    expected = protocol.get("implementation_sha256", {}).get(name)
    if not path.is_file() or expected != file_hash(path):
        raise ValueError(f"active implementation SHA mismatch: {name}")
    return path


def source_pairwise_equivalence(
    source: Path, capture_dir: Path
) -> dict[str, Any]:
    manifest = load(capture_dir / "capture_manifest.json")
    expected_path = capture_dir / manifest[
        "processed_benchmark_expected_outputs"
    ]
    with (
        np.load(source / "scores.npz", allow_pickle=False) as scores,
        np.load(source / "evidence_package.npz", allow_pickle=False) as evidence,
        np.load(expected_path, allow_pickle=False) as actual,
    ):
        checks = {
            "closed_set_prediction_array_equal": bool(
                np.array_equal(
                    actual["closed_set_index"], scores["test_prediction"]
                )
            ),
            "probability_array_equal": bool(
                np.array_equal(
                    actual["probability"],
                    evidence["test_final_probability"],
                )
            ),
            "risk_array_equal": bool(
                np.array_equal(
                    actual["risk"], evidence["test_selected_risk"]
                )
            ),
            "rejection_array_equal": bool(
                np.array_equal(
                    actual["rejected"], evidence["test_rejected"]
                )
            ),
        }
    result = {
        "schema_version": (
            "strict_v4_pairwise_retraining_source_equivalence_v1"
        ),
        **checks,
        "passes": all(checks.values()),
        "source_scores_sha256": file_hash(source / "scores.npz"),
        "source_evidence_package_sha256": file_hash(
            source / "evidence_package.npz"
        ),
        "capture_manifest_sha256": file_hash(
            capture_dir / "capture_manifest.json"
        ),
    }
    if not result["passes"]:
        raise RuntimeError("Pairwise retraining differs from frozen source")
    return result


def source_vgrf_equivalence(
    source: Path, capture_dir: Path
) -> dict[str, Any]:
    manifest = load(capture_dir / "capture_manifest.json")
    expected_path = capture_dir / manifest[
        "processed_benchmark_expected_outputs"
    ]
    source_metrics = load(source / "metrics.json")
    threshold = float(source_metrics["thresholds"]["candidate"])
    with (
        np.load(source / "scores.npz", allow_pickle=False) as scores,
        np.load(expected_path, allow_pickle=False) as actual,
    ):
        source_risk = np.asarray(
            scores["test_selected_risk"], dtype=np.float64
        )
        risk_difference = float(
            np.max(np.abs(actual["risk"] - source_risk))
        )
        checks = {
            "closed_set_prediction_array_equal": bool(
                np.array_equal(
                    actual["closed_set_index"],
                    scores["test_selected_prediction"],
                )
            ),
            "source_runtime_gate_decision_equal": (
                manifest["source_runtime_compatibility"][
                    "gate_decision_equal"
                ]
                is True
            ),
            "source_runtime_probability_equal": (
                manifest["source_runtime_compatibility"][
                    "test_probability_array_equal"
                ]
                is True
            ),
        }
        diagnostics = {
            "risk_max_absolute_difference": risk_difference,
            "risk_array_equal": bool(
                np.array_equal(actual["risk"], source_risk)
            ),
            "rejection_array_equal": bool(
                np.array_equal(
                    actual["rejected"], source_risk > threshold
                )
            ),
        }
    result = {
        "schema_version": (
            "strict_v4_vgrf_retraining_source_equivalence_v1"
        ),
        **checks,
        "source_empirical_tail_diagnostics": diagnostics,
        "source_empirical_tail_difference_is_diagnostic_only": True,
        "stable_runtime_internal_risk_and_rejection_equivalence_required": True,
        "probability_source_status": (
            "verified_by_capture_source_runtime_compatibility"
        ),
        "passes": all(checks.values()),
        "source_scores_sha256": file_hash(source / "scores.npz"),
        "source_metrics_sha256": file_hash(source / "metrics.json"),
        "capture_manifest_sha256": file_hash(
            capture_dir / "capture_manifest.json"
        ),
    }
    if not result["passes"]:
        raise RuntimeError("VGRF deployment differs from frozen source")
    return result


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run_subprocess(
    command: list[str], *, project: Path, log: Path
) -> float:
    started = time.perf_counter()
    with log.open("w", encoding="utf-8") as handle:
        completed = subprocess.run(
            command,
            cwd=project,
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=False,
        )
    elapsed = time.perf_counter() - started
    if completed.returncode != 0:
        raise RuntimeError(
            f"capture subprocess failed with exit {completed.returncode}: {log}"
        )
    return elapsed


def capture_record(
    *,
    record: dict[str, Any],
    protocol: dict[str, Any],
    project: Path,
) -> dict[str, Any]:
    roots = source_roots(record)
    for method in ("pairwise", "vgrf", "opendetect"):
        if not roots[method].is_dir():
            raise FileNotFoundError(roots[method])
    deployment = {
        name: Path(value)
        for name, value in record["deployment_output_roots"].items()
    }
    pairwise_capture = deployment["pairwise_capture"]
    pairwise_capture.mkdir(parents=True, exist_ok=True)
    pairwise_manifest = pairwise_capture / "capture_manifest.json"
    pairwise_retrain = pairwise_capture.parent / "pairwise_retrain_run"
    pairwise_retrain.mkdir(parents=True, exist_ok=True)
    pairwise_provenance = load(roots["pairwise"] / "provenance.json")
    trainer_command = [str(value) for value in pairwise_provenance["command"]]
    trainer_command[0] = sys.executable
    replace_value(
        trainer_command, "--output-dir", str(pairwise_retrain.resolve())
    )
    timings: dict[str, float] = {}
    if not pairwise_manifest.is_file():
        capture_script = require_active_implementation(
            protocol, project, "capture_pairwise_deployment_bundle.py"
        )
        trainer = require_active_implementation(
            protocol, project, "train_hybrid_open_set.py"
        )
        command = [
            sys.executable,
            str(capture_script),
            "--trainer",
            str(trainer),
            "--capture-dir",
            str(pairwise_capture),
            "--",
            *trainer_command[2:],
        ]
        timings["pairwise_capture_seconds"] = run_subprocess(
            command,
            project=project,
            log=pairwise_capture / "capture.log",
        )
    pairwise_audit = audit_pairwise(pairwise_capture)
    write_json(deployment["pairwise_audit"], pairwise_audit)
    pairwise_source = source_pairwise_equivalence(
        roots["pairwise"], pairwise_capture
    )
    write_json(
        pairwise_capture / "frozen_source_equivalence.json",
        pairwise_source,
    )

    vgrf_capture = deployment["vgrf_capture"]
    vgrf_capture.mkdir(parents=True, exist_ok=True)
    vgrf_manifest = vgrf_capture / "capture_manifest.json"
    if not vgrf_manifest.is_file():
        builder = require_active_implementation(
            protocol, project, "build_vgrf_deployment_bundle.py"
        )
        parameters = protocol["vgrf_known_only_parameters"]
        command = [
            sys.executable,
            str(builder),
            "--pairwise-capture-dir",
            str(pairwise_capture),
            "--reference-run-dir",
            str(pairwise_retrain),
            "--output-dir",
            str(vgrf_capture),
            "--source-protocol-manifest-sha256",
            protocol["manifest_sha256"],
            "--shrinkage",
            str(parameters["empirical_bayes_shrinkage"]),
            "--minimum-reliability",
            str(parameters["minimum_reliability"]),
            "--risk-blend",
            str(parameters["risk_blend"]),
            "--known-rejection-quantile",
            str(parameters["known_rejection_quantile"]),
            "--minimum-f1-gain",
            str(parameters["minimum_f1_gain"]),
            "--maximum-correct-risk-increase",
            str(parameters["maximum_correct_risk_increase"]),
            "--minimum-auc-gain",
            str(parameters["minimum_auc_gain"]),
            "--minimum-separation-gain",
            str(parameters["minimum_separation_gain"]),
            "--minimum-strict-proxy-gain",
            str(parameters["minimum_strict_proxy_gain"]),
        ]
        timings["vgrf_capture_seconds"] = run_subprocess(
            command,
            project=project,
            log=vgrf_capture / "capture.log",
        )
    vgrf_audit = audit_vgrf(vgrf_capture)
    write_json(deployment["vgrf_audit"], vgrf_audit)
    vgrf_source = source_vgrf_equivalence(roots["vgrf"], vgrf_capture)
    write_json(
        vgrf_capture / "frozen_source_equivalence.json", vgrf_source
    )

    opendetect_capture = deployment["opendetect_capture"]
    opendetect_capture.mkdir(parents=True, exist_ok=True)
    opendetect_manifest = opendetect_capture / "capture_manifest.json"
    if not opendetect_manifest.is_file():
        started = time.perf_counter()
        capture_opendetect(
            roots["opendetect"],
            pairwise_capture,
            opendetect_capture,
        )
        timings["opendetect_capture_seconds"] = (
            time.perf_counter() - started
        )
    opendetect_audit = audit_opendetect(opendetect_capture)
    write_json(deployment["opendetect_audit"], opendetect_audit)
    return {
        "suite": record["suite"],
        "scenario": record["scenario"],
        "seed": int(record["seed"]),
        "timings": timings,
        "pairwise_source_equivalence": pairwise_source["passes"],
        "vgrf_source_equivalence": vgrf_source["passes"],
        "pairwise_audit_passes": pairwise_audit["passes"],
        "vgrf_audit_passes": vgrf_audit["passes"],
        "opendetect_audit_passes": opendetect_audit["passes"],
        "deployment_output_roots": record["deployment_output_roots"],
    }


def write_state(
    path: Path,
    *,
    protocol: dict[str, Any],
    results: list[dict[str, Any]],
    state: str,
) -> None:
    value = {
        "schema_version": (
            "strict_v4_vgrf_selected_system_capture_state_v1"
        ),
        "state": state,
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_source_pairs": 306,
        "reported_source_pairs": len(results),
        "results": sorted(
            results,
            key=lambda item: (
                item["suite"],
                item["scenario"],
                item["seed"],
            ),
        ),
    }
    write_json(path, value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    protocol = load(args.protocol)
    if (
        protocol.get("schema_version")
        != "strict_v4_vgrf_selected_system_execution_protocol_v1"
        or protocol.get("manifest_sha256") != canonical_hash(protocol)
        or len(protocol.get("source_registry", [])) != 306
    ):
        raise ValueError("invalid selected-system execution protocol")
    require_active_implementation(
        protocol,
        project,
        Path(__file__).name,
    )
    results: list[dict[str, Any]] = []
    write_state(
        args.state, protocol=protocol, results=results, state="running"
    )
    for record in protocol["source_registry"]:
        result = capture_record(
            record=record, protocol=protocol, project=project
        )
        results.append(result)
        write_state(
            args.state,
            protocol=protocol,
            results=results,
            state="running",
        )
        print(
            f"captured {result['suite']}/{result['scenario']}_seed"
            f"{result['seed']}",
            flush=True,
        )
    write_state(
        args.state, protocol=protocol, results=results, state="complete"
    )
    (args.state.parent / "deployment_capture_complete").touch()


if __name__ == "__main__":
    main()
