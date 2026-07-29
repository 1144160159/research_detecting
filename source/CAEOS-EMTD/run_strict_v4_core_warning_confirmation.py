from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any


def canonical_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def verify_protocol(
    project_root: Path, protocol_path: Path
) -> dict[str, Any]:
    protocol = load(protocol_path)
    declared = protocol.get("manifest_sha256")
    body = dict(protocol)
    body.pop("manifest_sha256", None)
    if not isinstance(declared, str) or canonical_hash(body) != declared:
        raise ValueError("protocol canonical manifest mismatch")
    if protocol.get("status") != "frozen_zero_result_before_fresh_confirmation":
        raise ValueError("protocol is not a zero-result frozen execution protocol")
    for relative, expected in protocol["implementation_sha256"].items():
        path = project_root / relative
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"implementation hash drifted: {relative}")
    return protocol


def run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    print(json.dumps({"command": command}, ensure_ascii=False), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def prepare_caches(
    *,
    python: str,
    project_root: Path,
    protocol: dict[str, Any],
    env: dict[str, str],
) -> None:
    cache_root = project_root / protocol["data"]["cache_root"]
    cache_root.mkdir(parents=True, exist_ok=True)
    maximum = int(protocol["data"]["cache_max_per_class"])
    source = str(protocol["data"]["source_csv"])
    config = str(protocol["data"]["config"])
    for seed in protocol["seeds"]:
        output = cache_root / f"seed{seed}_max{maximum}.csv"
        sidecar = output.with_suffix(output.suffix + ".json")
        if output.is_file() and sidecar.is_file():
            metadata = load(sidecar)
            if (
                int(metadata.get("seed", -1)) == int(seed)
                and int(metadata.get("max_per_class", -1)) == maximum
                and metadata.get("source_sha256")
                == protocol["data"]["source_csv_sha256"]
                and metadata.get("config_sha256")
                == protocol["data"]["config_sha256"]
                and metadata.get("output_sha256") == file_hash(output)
            ):
                continue
            raise ValueError(f"cache provenance drifted: {output}")
        if output.exists() or sidecar.exists():
            raise ValueError(f"partial cache exists: {output}")
        run(
            [
                python,
                "prepare_stratified_cache.py",
                "--csv",
                source,
                "--config",
                config,
                "--max-per-class",
                str(maximum),
                "--seed",
                str(seed),
                "--output",
                str(output),
            ],
            cwd=project_root,
            env=env,
        )


def run_confirmation(
    *,
    python: str,
    project_root: Path,
    protocol_path: Path,
    protocol: dict[str, Any],
    env: dict[str, str],
) -> dict[str, Any]:
    prepare_caches(
        python=python,
        project_root=project_root,
        protocol=protocol,
        env=env,
    )
    run_root = project_root / protocol["execution"]["run_root"]
    result_root = project_root / protocol["execution"]["result_root"]
    cache_root = project_root / protocol["data"]["cache_root"]
    result_root.mkdir(parents=True, exist_ok=True)
    candidate = protocol["algorithm"]["candidate"]
    run(
        [
            python,
            "run_nested_gate_matrix.py",
            "--suite",
            "cicids2017",
            "--scenarios",
            ",".join(protocol["scenarios"]),
            "--seeds",
            ",".join(str(value) for value in protocol["seeds"]),
            "--workers",
            str(protocol["execution"]["workers"]),
            "--model-jobs",
            str(protocol["execution"]["model_jobs"]),
            "--estimators",
            str(protocol["execution"]["estimators"]),
            "--risk-selection",
            protocol["algorithm"]["risk_selection"],
            "--pseudo-unknown-max-alpha",
            str(candidate["maximum_alpha"]),
            "--pseudo-unknown-min-fold-gain",
            str(candidate["minimum_fold_gain"]),
            "--boundary-hard-pseudo-fraction",
            str(candidate["hard_pseudo_fraction"]),
            "--boundary-interpolation",
            str(candidate["interpolation"]),
            "--boundary-max-per-task",
            str(candidate["max_per_task"]),
            "--boundary-training-objective",
            str(candidate["training_objective"]),
            "--risk-policy-name",
            protocol["algorithm"]["risk_policy_name"],
            "--cicids2017-cache-dir",
            str(cache_root),
            "--cicids2017-max-per-class",
            str(protocol["data"]["cache_max_per_class"]),
            "--output-root",
            str(run_root),
        ],
        cwd=project_root,
        env=env,
    )
    metrics = list(run_root.rglob("metrics.json"))
    failures = list(run_root.rglob("failure.json"))
    if len(metrics) != protocol["expected_task_count"] or failures:
        raise RuntimeError(
            f"task coverage invalid: metrics={len(metrics)} "
            f"failures={len(failures)}"
        )

    evaluation_path = result_root / "evaluation.json"
    run(
        [
            python,
            "evaluate_strict_v4_benign_calibrated_warning.py",
            "--run-root",
            str(run_root),
            "--suites",
            "cicids2017",
            "--validation-benign-fpr-budget",
            str(
                protocol["development_selection"][
                    "selected_validation_benign_fpr_budget"
                ]
            ),
            "--alert-mode",
            protocol["algorithm"]["alert_mode"],
            "--seeds",
            ",".join(str(value) for value in protocol["seeds"]),
            "--output",
            str(evaluation_path),
        ],
        cwd=project_root,
        env=env,
    )
    audit_path = result_root / "audit.json"
    run(
        [
            python,
            "audit_strict_v4_core_warning_confirmation.py",
            "--project-root",
            str(project_root),
            "--protocol",
            str(protocol_path),
            "--evaluation",
            str(evaluation_path),
            "--output",
            str(audit_path),
        ],
        cwd=project_root,
        env=env,
    )
    audit = load(audit_path)
    completion: dict[str, Any] = {
        "schema_version": "strict_v4_core_warning_confirmation_completion_v1",
        "state": "complete",
        "integrity_passes": bool(audit["integrity_passes"]),
        "eligible_basic_warning_claim": bool(
            audit["eligible_basic_warning_claim"]
        ),
        "eligible_full_open_set_claim": bool(
            audit["eligible_full_open_set_claim"]
        ),
        "bindings": {
            "protocol_file_sha256": file_hash(protocol_path),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "evaluation_file_sha256": file_hash(evaluation_path),
            "evaluation_manifest_sha256": load(evaluation_path)[
                "manifest_sha256"
            ],
            "audit_file_sha256": file_hash(audit_path),
            "audit_manifest_sha256": audit["manifest_sha256"],
        },
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    completion_path = result_root / "completion.json"
    completion_path.write_text(
        json.dumps(completion, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return completion


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--python", required=True)
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    protocol_path = args.protocol.resolve()
    protocol = verify_protocol(project_root, protocol_path)
    env = dict(os.environ)
    env.update(
        {
            str(key): str(value)
            for key, value in protocol["execution"]["thread_limits"].items()
        }
    )
    completion = run_confirmation(
        python=str(args.python),
        project_root=project_root,
        protocol_path=protocol_path,
        protocol=protocol,
        env=env,
    )
    print(json.dumps(completion, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
