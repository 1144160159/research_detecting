from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from create_strict_v4_external_confirmation_protocol import (
    canonical_hash,
    file_hash,
)


SEEDS = (269, 271, 277)
PUG_POLICY = "strict_v4_pug_confirmation_v1"
SUITE_SPECS: dict[str, dict[str, Any]] = {
    "edge_iiot": {
        "source": (
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/"
            "Edge-IIoTset dataset/Selected dataset for ML and DL/"
            "ML-EdgeIIoT-dataset.csv"
        ),
        "config": "configs/edge_iiot.json",
        "maximum": 1000,
        "cache_flag": "--edge-iiot-cache-dir",
        "maximum_flag": "--edge-iiot-max-per-class",
    },
    "nf_cse": {
        "source": (
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/"
            "NF-CSE-CIC-IDS2018-v2/b3427ed8ad063a09_MOHANAD_A4706/data/"
            "NF-CSE-CIC-IDS2018-v2.csv"
        ),
        "config": "configs/nf_cse_cic_ids2018_v2.json",
        "maximum": 1000,
        "cache_flag": "--nf-cse-cache-dir",
        "maximum_flag": "--nf-cse-max-per-class",
    },
    "ustc_tfc2016": {
        "source": (
            "/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/"
            "ustc_tfc2016/ustc_tfc2016_nfstream.csv"
        ),
        "config": "configs/ustc_tfc2016_nfstream.json",
        "maximum": 3000,
        "cache_flag": "--ustc-cache-dir",
        "maximum_flag": "--ustc-max-per-class",
    },
    "nf_unsw": {
        "source": (
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/"
            "NF-UNSW-NB15-v2/fe6cb615d161452c_MOHANAD_A4706/data/"
            "NF-UNSW-NB15-v2.csv"
        ),
        "config": "configs/nf_unsw_nb15.json",
        "maximum": 5000,
        "cache_flag": "--nf-unsw-cache-dir",
        "maximum_flag": "--nf-unsw-max-per-class",
    },
    "cicids2017": {
        "source": (
            "/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD/caches/"
            "strict_v3/cicids2017/source/cicids2017_strict.csv"
        ),
        "config": "configs/cicids2017_strict.json",
        "maximum": 5000,
        "cache_flag": "--cicids2017-cache-dir",
        "maximum_flag": "--cicids2017-max-per-class",
    },
    "cic_ton_iot": {
        "source": (
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/"
            "a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv"
        ),
        "config": "configs/cic_ton_iot_strict.json",
        "maximum": 1000,
        "cache_flag": "--cic-ton-iot-cache-dir",
        "maximum_flag": "--cic-ton-iot-max-per-class",
    },
    "cic_iot2023": {
        "source": (
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/"
            "CIC_IOT_Dataset2023/CIC_IOT_Dataset2023_PCAP/CSV/CSV"
        ),
        "maximum": 1000,
        "cache_flag": "--cic-iot2023-cache-dir",
        "maximum_flag": "--cic-iot2023-max-per-class",
    },
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def source_path(suite: str) -> Path:
    key = f"CAEOS_PUG_SOURCE_{suite.upper()}"
    return Path(os.environ.get(key, str(SUITE_SPECS[suite]["source"])))


def cache_path(cache_root: Path, suite: str, seed: int) -> Path:
    maximum = int(SUITE_SPECS[suite]["maximum"])
    return cache_root / suite / f"seed{seed}_max{maximum}.csv"


def require_file_pair(path: Path) -> None:
    sidecar = Path(f"{path}.json")
    if not path.is_file() or path.stat().st_size <= 0:
        raise ValueError(f"cache is absent or empty: {path}")
    if not sidecar.is_file() or sidecar.stat().st_size <= 0:
        raise ValueError(f"cache sidecar is absent or empty: {sidecar}")


def run_logged(command: list[str], log_path: Path, root: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8", newline="\n") as log:
        log.write("$ " + " ".join(command) + "\n")
        log.flush()
        subprocess.run(
            command,
            cwd=root,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )


def prepare_caches(
    root: Path,
    cache_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    python = sys.executable
    for seed in SEEDS:
        for suite, spec in SUITE_SPECS.items():
            source = source_path(suite)
            if not source.exists():
                raise FileNotFoundError(f"source is absent: {source}")
            output = cache_path(cache_root, suite, seed)
            output.parent.mkdir(parents=True, exist_ok=True)
            log = result_root / "logs" / f"cache_{suite}_seed{seed}.log"
            if suite == "cic_iot2023":
                raw = (
                    cache_root
                    / "cic_iot2023_raw"
                    / f"seed{seed}_max1000.csv"
                )
                raw.parent.mkdir(parents=True, exist_ok=True)
                if not raw.is_file() or not Path(f"{raw}.json").is_file():
                    run_logged(
                        [
                            python,
                            "prepare_cic_iot2023_strict.py",
                            "--input-dir",
                            str(source),
                            "--output",
                            str(raw),
                            "--seed",
                            str(seed),
                            "--max-per-class",
                            "1000",
                            "--group-rows",
                            "1000",
                            "--expected-source-files",
                            "309",
                        ],
                        log,
                        root,
                    )
                require_file_pair(raw)
                if not output.is_file() or not Path(f"{output}.json").is_file():
                    run_logged(
                        [
                            python,
                            "prepare_group_supported_cache.py",
                            "--input",
                            str(raw),
                            "--output",
                            str(output),
                            "--label-column",
                            "Attack",
                            "--group-column",
                            "CaptureGroup",
                            "--minimum-groups",
                            "3",
                        ],
                        log,
                        root,
                    )
            elif not output.is_file() or not Path(f"{output}.json").is_file():
                run_logged(
                    [
                        python,
                        "prepare_stratified_cache.py",
                        "--csv",
                        str(source),
                        "--config",
                        str(root / str(spec["config"])),
                        "--max-per-class",
                        str(spec["maximum"]),
                        "--chunksize",
                        "50000",
                        "--seed",
                        str(seed),
                        "--output",
                        str(output),
                    ],
                    log,
                    root,
                )
            require_file_pair(output)

    entries: dict[str, Any] = {}
    for suite in SUITE_SPECS:
        for seed in SEEDS:
            path = cache_path(cache_root, suite, seed)
            sidecar = Path(f"{path}.json")
            entries[f"{suite}/seed{seed}"] = {
                "csv": path.relative_to(root).as_posix(),
                "csv_file_sha256": file_hash(path),
                "sidecar_file_sha256": file_hash(sidecar),
                "source": str(source_path(suite)),
            }
    manifest: dict[str, Any] = {
        "schema_version": "strict_v4_pug_cross_suite_cache_manifest_v1",
        "state": "all_seed_specific_caches_complete",
        "seed_count": 3,
        "suite_count": 7,
        "cache_count": 21,
        "entries": entries,
    }
    manifest["manifest_sha256"] = canonical_hash(manifest)
    output = result_root / "cache_manifest.json"
    if output.exists() and load(output) != manifest:
        raise ValueError("existing cache manifest is immutable")
    if not output.exists():
        temporary = output.with_suffix(".json.tmp")
        with temporary.open(
            "w", encoding="utf-8", newline="\n"
        ) as destination:
            destination.write(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            )
        temporary.replace(output)
    return manifest


def suite_scenarios(protocol: dict[str, Any], suite: str) -> list[str]:
    scenarios = protocol["confirmation_universe"]["scenarios_by_suite"][suite]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError(f"frozen scenarios are absent for {suite}")
    return [str(value) for value in scenarios]


def suite_cache_arguments(cache_root: Path, suite: str) -> list[str]:
    spec = SUITE_SPECS[suite]
    return [
        str(spec["cache_flag"]),
        str(cache_root / suite),
        str(spec["maximum_flag"]),
        str(spec["maximum"]),
    ]


def build_candidate_command(
    protocol: dict[str, Any],
    root: Path,
    cache_root: Path,
    candidate_root: Path,
    suite: str,
) -> list[str]:
    controls = protocol["execution_controls"]
    return [
        sys.executable,
        str(root / "run_nested_gate_matrix.py"),
        "--suite",
        suite,
        "--scenarios",
        ",".join(suite_scenarios(protocol, suite)),
        "--seeds",
        ",".join(map(str, SEEDS)),
        "--workers",
        str(controls["workers"]),
        "--model-jobs",
        str(controls["model_jobs"]),
        "--estimators",
        str(controls["estimators"]),
        "--risk-selection",
        str(controls["candidate_risk_selection"]),
        "--pseudo-unknown-max-alpha",
        str(controls["pseudo_unknown_max_alpha"]),
        "--pseudo-unknown-min-fold-gain",
        str(controls["pseudo_unknown_min_fold_gain"]),
        "--boundary-hard-pseudo-fraction",
        str(controls["boundary_hard_pseudo_fraction"]),
        "--boundary-interpolation",
        str(controls["boundary_interpolation"]),
        "--boundary-max-per-task",
        str(controls["boundary_max_per_task"]),
        "--boundary-training-objective",
        str(controls["boundary_training_objective"]),
        "--risk-policy-name",
        str(controls["candidate_policy_name"]),
        "--output-root",
        str(candidate_root),
        *suite_cache_arguments(cache_root, suite),
    ]


def build_opendetect_command(
    protocol: dict[str, Any],
    root: Path,
    cache_root: Path,
    opendetect_root: Path,
    suite: str,
) -> list[str]:
    controls = protocol["execution_controls"]
    return [
        sys.executable,
        str(root / "run_neural_baseline_matrix.py"),
        "--suite",
        suite,
        "--scenarios",
        ",".join(suite_scenarios(protocol, suite)),
        "--models",
        "opendetect",
        "--seeds",
        ",".join(map(str, SEEDS)),
        "--workers",
        str(controls["workers"]),
        "--epochs",
        str(controls["opendetect_epochs"]),
        "--patience",
        "10",
        "--output-root",
        str(opendetect_root),
        *suite_cache_arguments(cache_root, suite),
    ]


def validate_suite_artifacts(
    protocol: dict[str, Any],
    candidate_root: Path,
    opendetect_root: Path,
    suite: str,
) -> None:
    missing: list[str] = []
    for scenario in suite_scenarios(protocol, suite):
        for seed in SEEDS:
            candidate = candidate_root / suite / f"{scenario}_seed{seed}"
            opendetect = (
                opendetect_root
                / suite
                / f"{scenario}_seed{seed}_opendetect"
            )
            for name in (
                "metrics.json",
                "scores.npz",
                "evidence_package.npz",
                "provenance.json",
            ):
                if not (candidate / name).is_file():
                    missing.append(str(candidate / name))
            for name in ("metrics.json", "scores.npz", "provenance.json"):
                if not (opendetect / name).is_file():
                    missing.append(str(opendetect / name))
    if missing:
        raise ValueError(
            f"{suite} has {len(missing)} missing paired artifacts; "
            f"first={missing[0]}"
        )


def copy_matrix_manifest(
    matrix_root: Path, result_root: Path, method: str, suite: str
) -> None:
    source = matrix_root / "manifest.json"
    if not source.is_file():
        raise ValueError(f"matrix manifest is absent: {source}")
    payload = load(source)
    if payload.get("state") != "complete" or payload.get("failed") != 0:
        raise ValueError(f"incomplete {method} matrix for {suite}")
    destination = result_root / "matrix_manifests" / f"{method}_{suite}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def evaluate_suite_tasks(
    protocol: dict[str, Any],
    root: Path,
    result_root: Path,
    suite: str,
) -> None:
    for scenario in suite_scenarios(protocol, suite):
        for seed in SEEDS:
            run_logged(
                [
                    sys.executable,
                    str(
                        root
                        / "evaluate_strict_v4_pug_cross_suite_confirmation.py"
                    ),
                    "--project-root",
                    str(root),
                    "--suite",
                    suite,
                    "--scenario",
                    scenario,
                    "--seed",
                    str(seed),
                ],
                result_root / "logs" / f"evaluation_{suite}.log",
                root,
            )


def verify_implementation(protocol: dict[str, Any], root: Path) -> None:
    from evaluate_strict_v4_pug_cross_suite_confirmation import (
        validate_protocol,
    )

    validate_protocol(protocol, check_implementation=False)
    if (
        protocol["execution_controls"]["candidate_policy_name"]
        != PUG_POLICY
    ):
        raise ValueError("frozen PUG policy drifted")
    for relative, expected in protocol["implementation_sha256"].items():
        path = root / relative
        if not path.is_file() or file_hash(path) != expected:
            raise ValueError(f"frozen implementation drifted: {relative}")


def write_completion(
    protocol: dict[str, Any], result_root: Path
) -> dict[str, Any]:
    summary_path = result_root / "summary.json"
    audit_path = result_root / "audit.json"
    summary = load(summary_path)
    audit = load(audit_path)
    if (
        summary.get("manifest_sha256") != canonical_hash(summary)
        or audit.get("manifest_sha256") != canonical_hash(audit)
        or audit.get("integrity", {}).get("passes") is not True
    ):
        raise ValueError("canonical summary and passing integrity audit required")
    completion: dict[str, Any] = {
        "schema_version": (
            "strict_v4_pug_cross_suite_confirmation_completion_v1"
        ),
        "state": "complete",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "summary_manifest_sha256": summary["manifest_sha256"],
        "summary_file_sha256": file_hash(summary_path),
        "audit_manifest_sha256": audit["manifest_sha256"],
        "audit_file_sha256": file_hash(audit_path),
        "effect_passes": bool(audit["effect"]["passes"]),
        "candidate_selected_by_this_stage": bool(
            audit["effect"]["passes"] and summary["decision"]["passes"]
        ),
    }
    completion["manifest_sha256"] = canonical_hash(completion)
    output = result_root / "execution_complete.json"
    if output.exists() and load(output) != completion:
        raise ValueError("existing completion record is immutable")
    if not output.exists():
        temporary = output.with_suffix(".json.tmp")
        with temporary.open(
            "w", encoding="utf-8", newline="\n"
        ) as destination:
            destination.write(
                json.dumps(completion, indent=2, sort_keys=True) + "\n"
            )
        temporary.replace(output)
    return completion


def run_confirmation(
    protocol: dict[str, Any],
    root: Path,
    run_root: Path,
    result_root: Path,
) -> dict[str, Any]:
    verify_implementation(protocol, root)
    cache_root = root / "caches/strict_v4_pug_cross_suite_confirmation_v1"
    candidate_root = run_root / "candidate"
    opendetect_root = run_root / "opendetect"
    result_root.mkdir(parents=True, exist_ok=True)
    run_root.mkdir(parents=True, exist_ok=True)
    prepare_caches(root, cache_root, result_root)

    for suite in protocol["confirmation_universe"]["scenarios_by_suite"]:
        run_logged(
            build_candidate_command(
                protocol, root, cache_root, candidate_root, suite
            ),
            result_root / "logs" / f"candidate_{suite}.log",
            root,
        )
        copy_matrix_manifest(
            candidate_root, result_root, "candidate", suite
        )
        run_logged(
            build_opendetect_command(
                protocol, root, cache_root, opendetect_root, suite
            ),
            result_root / "logs" / f"opendetect_{suite}.log",
            root,
        )
        copy_matrix_manifest(
            opendetect_root, result_root, "opendetect", suite
        )
        validate_suite_artifacts(
            protocol, candidate_root, opendetect_root, suite
        )
        evaluate_suite_tasks(protocol, root, result_root, suite)

    task_count = len(list((result_root / "tasks").rglob("*.json")))
    if task_count != 306:
        raise ValueError(f"expected 306 task records, observed {task_count}")
    run_logged(
        [
            sys.executable,
            str(root / "summarize_strict_v4_pug_cross_suite_confirmation.py"),
            "--project-root",
            str(root),
        ],
        result_root / "logs" / "summary.log",
        root,
    )
    run_logged(
        [
            sys.executable,
            str(root / "audit_strict_v4_pug_cross_suite_confirmation.py"),
            "--project-root",
            str(root),
        ],
        result_root / "logs" / "audit.log",
        root,
    )
    return write_completion(protocol, result_root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1/"
            "execution_protocol.json"
        ),
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=Path("runs/strict_v4_pug_cross_suite_confirmation_v1"),
    )
    parser.add_argument(
        "--result-root",
        type=Path,
        default=Path(
            "results/strict_v4_pug_cross_suite_confirmation_v1"
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.project_root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    protocol_path = resolve(args.protocol)
    if not protocol_path.is_file():
        print("state=pending_execution_protocol")
        return
    result_root = resolve(args.result_root)
    lock = result_root / "runner.lock.d"
    result_root.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError:
        print("state=runner_already_active")
        return
    try:
        completion = run_confirmation(
            load(protocol_path),
            root,
            resolve(args.run_root),
            result_root,
        )
        print(f"state={completion['state']}")
        print(
            "candidate_selected_by_this_stage="
            f"{completion['candidate_selected_by_this_stage']}"
        )
        print(f"manifest_sha256={completion['manifest_sha256']}")
    finally:
        lock.rmdir()


if __name__ == "__main__":
    main()
