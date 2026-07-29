from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path

from run_nested_gate_matrix import (
    CIC_IOT2023_SCENARIOS,
    CIC_TON_IOT_SCENARIOS,
    CICIDS2017_SCENARIOS,
    DOH_SCENARIOS,
    EDGE_IIOT_SCENARIOS,
    HIKARI_SCENARIOS,
    MAL_TLS_SCENARIOS,
    NF_CSE_SCENARIOS,
    NF_UNSW_SCENARIOS,
    USTC_TFC2016_SCENARIOS,
    build_run_provenance,
    freeze_or_validate_provenance,
)


MODEL_DEFAULT_EPOCHS = {
    "closr": 100,
    "hcrp_osd": 100,
    "cade": 250,
    "opendetect": 100,
    "ronetc": 100,
    "sieve": 100,
    "nci": 35,
    "energy_cea": 35,
    "nci_cea": 35,
    "palm": 500,
    "m3s_upd": 30,
}

SUPPORTED_MODELS = {
    "mlp",
    "arpl",
    "hcrp_osd",
    "supcon",
    "closr",
    "cade",
    "opendetect",
    "ronetc",
    "foss",
    "sieve",
    "nci",
    "energy_cea",
    "nci_cea",
    "palm",
    "m3s_upd",
    "classical_ood",
    "efc",
}


@dataclass(frozen=True)
class Experiment:
    suite: str
    scenario: str
    unknown_classes: str
    model: str
    seed: int
    output_dir: str


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run resumable neural open-set baseline matrices")
    parser.add_argument(
        "--suite",
        choices=(
            "doh",
            "mal_tls",
            "hikari",
            "nf_unsw",
            "cicids2017",
            "cic_iot2023",
            "cic_ton_iot",
            "edge_iiot",
            "nf_cse",
            "ustc_tfc2016",
            "legacy",
            "extended",
            "strict_v3",
            "strict_v4",
            "strict_v4_primary",
            "all",
        ),
        required=True,
    )
    parser.add_argument("--scenarios", default="all")
    parser.add_argument("--models", default="mlp")
    parser.add_argument("--seeds", default="7")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--epochs",
        type=int,
        default=0,
        help="Positive override; zero uses each baseline's paper-aligned budget",
    )
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--tao-stage1-adapter", action="store_true")
    parser.add_argument("--tao-blood-estimators", type=int, default=50)
    parser.add_argument("--efc-jobs", type=int, default=8)
    parser.add_argument("--doh-max-per-class", type=int, default=4000)
    parser.add_argument("--mal-max-per-class", type=int, default=300)
    parser.add_argument("--hikari-max-per-class", type=int, default=2000)
    parser.add_argument("--nf-unsw-max-per-class", type=int, default=1500)
    parser.add_argument("--cicids2017-max-per-class", type=int, default=5000)
    parser.add_argument("--cic-iot2023-max-per-class", type=int, default=1000)
    parser.add_argument("--cic-ton-iot-max-per-class", type=int, default=1000)
    parser.add_argument("--edge-iiot-max-per-class", type=int, default=1000)
    parser.add_argument("--nf-cse-max-per-class", type=int, default=1000)
    parser.add_argument("--ustc-max-per-class", type=int, default=3000)
    parser.add_argument("--doh-csv", default="/opt/data/private/wangwt/ParkAttackKE/datasets/DoHBrw2020/caeos_multiclass_balanced_seed7.csv")
    parser.add_argument("--mal-csv", default="/opt/data/private/wangwt/ParkAttackKE/datasets/Mal_TLS2023/data/malicious_TLS.csv")
    parser.add_argument("--hikari-csv", default="/opt/data/private/wangwt/ParkAttackKE/datasets/HIKARI2021/HIKARI2021_model.csv")
    parser.add_argument(
        "--nf-unsw-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/"
            "NF-UNSW-NB15-v2/fe6cb615d161452c_MOHANAD_A4706/data/"
            "NF-UNSW-NB15-v2.csv"
        ),
    )
    parser.add_argument("--nf-unsw-cache-dir", default="")
    parser.add_argument(
        "--cicids2017-csv",
        default="caches/strict_v3/cicids2017/source/cicids2017_strict.csv",
    )
    parser.add_argument("--cicids2017-cache-dir", default="")
    parser.add_argument("--cic-iot2023-csv", default="")
    parser.add_argument("--cic-iot2023-cache-dir", default="")
    parser.add_argument(
        "--cic-ton-iot-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CIC-ToN-IoT/"
            "a40a412453292fe6_MOHANAD_A4706/data/CIC-ToN-IoT.csv"
        ),
    )
    parser.add_argument("--cic-ton-iot-cache-dir", default="")
    parser.add_argument(
        "--edge-iiot-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/EdgeIIoT/"
            "Edge-IIoTset dataset/Selected dataset for ML and DL/"
            "ML-EdgeIIoT-dataset.csv"
        ),
    )
    parser.add_argument("--edge-iiot-cache-dir", default="")
    parser.add_argument(
        "--nf-cse-csv",
        default=(
            "/opt/data/private/wangwt/ParkAttackKE/datasets/cic/"
            "NF-CSE-CIC-IDS2018-v2/b3427ed8ad063a09_MOHANAD_A4706/data/"
            "NF-CSE-CIC-IDS2018-v2.csv"
        ),
    )
    parser.add_argument("--nf-cse-cache-dir", default="")
    parser.add_argument(
        "--ustc-csv",
        default="caches/ustc_tfc2016/ustc_tfc2016_nfstream.csv",
    )
    parser.add_argument("--ustc-cache-dir", default="")
    parser.add_argument("--output-root", default="runs/neural_baseline_matrix")
    return parser.parse_args()


def _seed_cache(cache_dir: str, seed: int | None, maximum: int, fallback: str) -> str:
    if not cache_dir or seed is None:
        return fallback
    cached = Path(cache_dir) / f"seed{seed}_max{maximum}.csv"
    if not cached.exists():
        raise FileNotFoundError(f"missing stratified cache: {cached}")
    return str(cached)


def suite_settings(suite: str, args: argparse.Namespace, seed: int | None = None):
    maximum = {
        "nf_unsw": getattr(args, "nf_unsw_max_per_class", 1500),
        "cicids2017": getattr(args, "cicids2017_max_per_class", 5000),
        "cic_iot2023": getattr(args, "cic_iot2023_max_per_class", 1000),
        "cic_ton_iot": getattr(args, "cic_ton_iot_max_per_class", 1000),
        "edge_iiot": getattr(args, "edge_iiot_max_per_class", 1000),
        "nf_cse": getattr(args, "nf_cse_max_per_class", 1000),
        "ustc_tfc2016": getattr(args, "ustc_max_per_class", 3000),
    }
    csv_paths = {
        "nf_unsw": _seed_cache(
            getattr(args, "nf_unsw_cache_dir", ""), seed, maximum["nf_unsw"],
            getattr(args, "nf_unsw_csv", ""),
        ),
        "cicids2017": _seed_cache(
            getattr(args, "cicids2017_cache_dir", ""), seed,
            maximum["cicids2017"], getattr(args, "cicids2017_csv", ""),
        ),
        "cic_iot2023": _seed_cache(
            getattr(args, "cic_iot2023_cache_dir", ""), seed,
            maximum["cic_iot2023"], getattr(args, "cic_iot2023_csv", ""),
        ),
        "cic_ton_iot": _seed_cache(
            getattr(args, "cic_ton_iot_cache_dir", ""), seed,
            maximum["cic_ton_iot"], getattr(args, "cic_ton_iot_csv", ""),
        ),
        "edge_iiot": _seed_cache(
            getattr(args, "edge_iiot_cache_dir", ""), seed, maximum["edge_iiot"],
            getattr(args, "edge_iiot_csv", ""),
        ),
        "nf_cse": _seed_cache(
            getattr(args, "nf_cse_cache_dir", ""), seed, maximum["nf_cse"],
            getattr(args, "nf_cse_csv", ""),
        ),
        "ustc_tfc2016": _seed_cache(
            getattr(args, "ustc_cache_dir", ""), seed,
            maximum["ustc_tfc2016"], getattr(args, "ustc_csv", ""),
        ),
    }
    return {
        "doh": (DOH_SCENARIOS, args.doh_csv, "configs/dohbrw2020_multiclass.json", "benign", "capture_grouped", args.doh_max_per_class),
        "mal_tls": (MAL_TLS_SCENARIOS, args.mal_csv, "configs/mal_tls2023.json", "benign", "fingerprint_grouped", args.mal_max_per_class),
        "hikari": (HIKARI_SCENARIOS, args.hikari_csv, "configs/hikari2021.json", "Benign", "fingerprint_grouped", args.hikari_max_per_class),
        "nf_unsw": (NF_UNSW_SCENARIOS, csv_paths["nf_unsw"], "configs/nf_unsw_nb15.json", "Benign", "fingerprint_grouped", maximum["nf_unsw"]),
        "cicids2017": (CICIDS2017_SCENARIOS, csv_paths["cicids2017"], "configs/cicids2017_strict.json", "Benign", "capture_grouped", maximum["cicids2017"]),
        "cic_iot2023": (CIC_IOT2023_SCENARIOS, csv_paths["cic_iot2023"], "configs/cic_iot2023_strict.json", "Benign", "capture_grouped", maximum["cic_iot2023"]),
        "cic_ton_iot": (CIC_TON_IOT_SCENARIOS, csv_paths["cic_ton_iot"], "configs/cic_ton_iot_strict.json", "Benign", "fingerprint_grouped", maximum["cic_ton_iot"]),
        "edge_iiot": (EDGE_IIOT_SCENARIOS, csv_paths["edge_iiot"], "configs/edge_iiot.json", "Normal", "fingerprint_grouped", maximum["edge_iiot"]),
        "nf_cse": (NF_CSE_SCENARIOS, csv_paths["nf_cse"], "configs/nf_cse_cic_ids2018_v2.json", "Benign", "fingerprint_grouped", maximum["nf_cse"]),
        "ustc_tfc2016": (USTC_TFC2016_SCENARIOS, csv_paths["ustc_tfc2016"], "configs/ustc_tfc2016_nfstream.json", "Benign", "capture_grouped", maximum["ustc_tfc2016"]),
    }[suite]


def build_experiments(args: argparse.Namespace) -> list[Experiment]:
    if args.suite == "legacy":
        suites = ("doh", "mal_tls", "hikari")
    elif args.suite == "extended":
        suites = ("edge_iiot", "nf_cse", "ustc_tfc2016")
    elif args.suite == "strict_v3":
        suites = ("nf_unsw", "cicids2017")
    elif args.suite == "strict_v4":
        suites = ("cic_ton_iot", "cic_iot2023")
    elif args.suite == "strict_v4_primary":
        suites = (
            "nf_unsw",
            "cicids2017",
            "cic_iot2023",
            "cic_ton_iot",
            "edge_iiot",
            "nf_cse",
            "ustc_tfc2016",
        )
    elif args.suite == "all":
        suites = (
            "doh", "mal_tls", "hikari", "nf_unsw", "cicids2017", "edge_iiot", "nf_cse",
            "ustc_tfc2016", "cic_iot2023", "cic_ton_iot",
        )
    else:
        suites = (args.suite,)
    scenario_maps = {
        "doh": DOH_SCENARIOS,
        "mal_tls": MAL_TLS_SCENARIOS,
        "hikari": HIKARI_SCENARIOS,
        "nf_unsw": NF_UNSW_SCENARIOS,
        "cicids2017": CICIDS2017_SCENARIOS,
        "cic_iot2023": CIC_IOT2023_SCENARIOS,
        "cic_ton_iot": CIC_TON_IOT_SCENARIOS,
        "edge_iiot": EDGE_IIOT_SCENARIOS,
        "nf_cse": NF_CSE_SCENARIOS,
        "ustc_tfc2016": USTC_TFC2016_SCENARIOS,
    }
    requested = (
        None
        if args.scenarios == "all"
        else {value.strip() for value in args.scenarios.split(",") if value.strip()}
    )
    if requested is not None:
        known_scenarios = set().union(*(scenario_maps[suite] for suite in suites))
        unknown = requested - known_scenarios
        if not requested or unknown:
            raise ValueError(
                f"unknown or empty --scenarios selection: {sorted(unknown or requested)}"
            )
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    models = [value.strip() for value in args.models.split(",") if value.strip()]
    if not seeds:
        raise ValueError("--seeds must contain at least one integer")
    if len(seeds) != len(set(seeds)):
        raise ValueError("--seeds must not contain duplicates")
    if not models:
        raise ValueError("--models must contain at least one model")
    if len(models) != len(set(models)):
        raise ValueError("--models must not contain duplicates")
    unknown_models = sorted(set(models) - SUPPORTED_MODELS)
    if unknown_models:
        raise ValueError(f"unknown --models values: {unknown_models}")
    experiments = []
    for suite in suites:
        scenarios, *_ = suite_settings(suite, args)
        for scenario, unknown_classes in scenarios.items():
            if requested is not None and scenario not in requested:
                continue
            for model in models:
                for seed in seeds:
                    output_dir = str(Path(args.output_root) / suite / f"{scenario}_seed{seed}_{model}")
                    experiments.append(Experiment(suite, scenario, unknown_classes, model, seed, output_dir))
    if not experiments:
        raise ValueError("experiment selection produced zero experiments")
    return experiments


def command_for(experiment: Experiment, args: argparse.Namespace) -> list[str]:
    _, csv_path, config, benign, split, maximum = suite_settings(
        experiment.suite, args, experiment.seed
    )
    epochs = (
        args.epochs
        if args.epochs > 0
        else MODEL_DEFAULT_EPOCHS.get(experiment.model, 35)
    )
    if experiment.model == "m3s_upd":
        return [
            sys.executable,
            "train_m3s_upd_strict_v2.py",
            "--csv", csv_path,
            "--config", config,
            "--unknown-classes", experiment.unknown_classes,
            "--benign-class", benign,
            "--split-strategy", split,
            "--max-per-class", str(maximum),
            "--epochs", str(epochs),
            "--patience", str(args.patience),
            "--seed", str(experiment.seed),
            "--output-dir", experiment.output_dir,
        ]
    if experiment.model == "foss":
        return [
            sys.executable,
            "train_foss_open_set.py",
            "--csv", csv_path,
            "--config", config,
            "--unknown-classes", experiment.unknown_classes,
            "--benign-class", benign,
            "--split-strategy", split,
            "--max-per-class", str(maximum),
            "--foss-trees", "30",
            "--foss-subsample-size", "100",
            "--foss-candidate-dimensions", "5",
            "--foss-min-samples", "1",
            "--seed", str(experiment.seed),
            "--output-dir", experiment.output_dir,
        ]
    if experiment.model == "classical_ood":
        return [
            sys.executable,
            "train_classical_ood.py",
            "--csv", csv_path,
            "--config", config,
            "--unknown-classes", experiment.unknown_classes,
            "--benign-class", benign,
            "--split-strategy", split,
            "--max-per-class", str(maximum),
            "--known-acceptance", "0.95",
            "--detector-max-samples", "5000",
            "--isolation-trees", "200",
            "--ocsvm-nu", "0.05",
            "--lof-neighbors", "20",
            "--pca-components", "64",
            "--seed", str(experiment.seed),
            "--output-dir", experiment.output_dir,
        ]
    if experiment.model == "efc":
        return [
            sys.executable,
            "train_efc_open_set.py",
            "--csv", csv_path,
            "--config", config,
            "--unknown-classes", experiment.unknown_classes,
            "--benign-class", benign,
            "--split-strategy", split,
            "--max-per-class", str(maximum),
            "--known-acceptance", "0.95",
            "--pseudocounts", "0.5",
            "--cutoff-quantile", "0.95",
            "--n-bins", "30",
            "--jobs", str(getattr(args, "efc_jobs", 8)),
            "--seed", str(experiment.seed),
            "--output-dir", experiment.output_dir,
        ]
    if experiment.model == "sieve":
        return [
            sys.executable,
            "train_sieve_open_set.py",
            "--csv", csv_path,
            "--config", config,
            "--unknown-classes", experiment.unknown_classes,
            "--benign-class", benign,
            "--split-strategy", split,
            "--max-per-class", str(maximum),
            "--epochs", str(epochs),
            "--patience", str(args.patience),
            "--batch-size", "256",
            "--num-workers", "4",
            "--seed", str(experiment.seed),
            "--output-dir", experiment.output_dir,
        ]
    command = [
        sys.executable, "train_neural_open_set.py", "--csv", csv_path,
        "--config", config, "--unknown-classes", experiment.unknown_classes,
        "--benign-class", benign, "--split-strategy", split,
        "--max-per-class", str(maximum), "--model", experiment.model,
        "--epochs", str(epochs), "--patience", str(args.patience),
        "--batch-size", "512", "--num-workers", "4", "--seed", str(experiment.seed),
        "--output-dir", experiment.output_dir,
    ]
    if experiment.model == "mlp":
        command.extend(
            [
                "--hidden-dim", "128",
                "--embedding-dim", "64",
                "--learning-rate", "1e-3",
                "--weight-decay", "1e-4",
                "--sampling", "weighted",
                "--nci-alpha", "0.0001",
                "--cea-percentile", "99.9",
                "--cea-addition-coefficient", "10",
                "--cea-threshold-caution-coefficient", "1.1",
                "--scale-percentile", "85",
                "--scale-temperature", "1",
            ]
        )
        if getattr(args, "tao_stage1_adapter", False):
            command.extend(
                [
                    "--tao-stage1-adapter",
                    "--tao-blood-estimators",
                    str(getattr(args, "tao_blood_estimators", 50)),
                    "--tao-pca-variance-ratio",
                    "0.95",
                    "--tao-alpha",
                    "0.6",
                ]
            )
    elif experiment.model == "hcrp_osd":
        command.extend(
            [
                "--hidden-dim", "32",
                "--embedding-dim", "64",
                "--learning-rate", "1e-3",
                "--weight-decay", "1e-4",
                "--temperature", "1",
                "--radius-weight", "0.1",
                "--batch-size", "512",
                "--sampling", "weighted",
            ]
        )
    elif experiment.model == "closr":
        command.extend(
            [
                "--hidden-dim", "1024",
                "--embedding-dim", "64",
                "--learning-rate", "1e-5",
                "--weight-decay", "0.0403709",
                "--batch-size", "4096",
                "--sampling", "weighted",
            ]
        )
    elif experiment.model == "cade":
        command.extend(
            [
                "--cade-hidden", "64,32,16",
                "--embedding-dim", "16",
                "--learning-rate", "1e-4",
                "--weight-decay", "0",
                "--cade-contrast-weight", "0.1",
                "--cade-margin", "10",
                "--cade-similar-ratio", "0.25",
                "--cade-classifier-hidden", "30",
                "--cade-classifier-dropout", "0.2",
                "--cade-classifier-epochs", "30",
                "--cade-classifier-batch-size", "256",
                "--cade-classifier-lr", "1e-3",
                "--cade-mad-threshold", "3.5",
                "--sampling", "natural",
            ]
        )
    elif experiment.model == "opendetect":
        command.extend(
            [
                "--hidden-dim", "256",
                "--embedding-dim", "128",
                "--learning-rate", "1e-3",
                "--weight-decay", "0",
                "--temperature", "1",
                "--open-detect-generative-weight", "0.005",
                "--open-detect-reset-epochs", "50,80",
                "--batch-size", "128",
                "--sampling", "natural",
            ]
        )
    elif experiment.model == "ronetc":
        command.extend(
            [
                "--hidden-dim", "128",
                "--embedding-dim", "64",
                "--learning-rate", "1e-3",
                "--weight-decay", "0",
                "--ronetc-annealing-epochs", "10",
                "--batch-size", "256",
                "--sampling", "natural",
            ]
        )
    elif experiment.model == "palm":
        command.extend(
            [
                "--hidden-dim", "128",
                "--embedding-dim", "128",
                "--weight-decay", "1e-6",
                "--palm-training-views", "2",
                "--palm-prototypes-per-class", "6",
                "--palm-assignment-top-k", "5",
                "--palm-prototype-momentum", "0.999",
                "--palm-temperature", "0.1",
                "--palm-assignment-epsilon", "0.05",
                "--palm-sinkhorn-iterations", "3",
                "--palm-prototype-contrast-weight", "1",
                "--palm-learning-rate", "0.5",
                "--palm-momentum", "0.9",
                "--batch-size", "512",
                "--sampling", "natural",
            ]
        )
    elif experiment.model in {"nci", "energy_cea", "nci_cea"}:
        command.extend(
            [
                "--hidden-dim", "128",
                "--embedding-dim", "64",
                "--learning-rate", "1e-3",
                "--weight-decay", "1e-4",
                "--sampling", "weighted",
            ]
        )
        if experiment.model in {"nci", "nci_cea"}:
            command.extend(["--nci-alpha", "0.0001"])
        if experiment.model in {"energy_cea", "nci_cea"}:
            command.extend(
                [
                    "--cea-percentile", "99.9",
                    "--cea-addition-coefficient", "10",
                    "--cea-threshold-caution-coefficient", "1.1",
                ]
            )
    return command


def run_one(experiment: Experiment, args: argparse.Namespace) -> dict[str, object]:
    output_dir = Path(experiment.output_dir)
    metrics_path = output_dir / "metrics.json"
    scores_path = output_dir / "scores.npz"
    output_dir.mkdir(parents=True, exist_ok=True)
    command = command_for(experiment, args)
    provenance = build_run_provenance(experiment, command)
    if freeze_or_validate_provenance(
        output_dir,
        provenance,
        (metrics_path, scores_path),
    ):
        return {
            **asdict(experiment),
            "status": "skipped",
            "elapsed_seconds": 0.0,
            "command": command,
            "parameter_fingerprint": provenance["parameter_fingerprint"],
        }
    started = time.perf_counter()
    with (output_dir / "run.log").open("w", encoding="utf-8") as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, text=True, check=False)
    elapsed = time.perf_counter() - started
    status = "completed" if completed.returncode == 0 and metrics_path.exists() and scores_path.exists() else "failed"
    return {
        **asdict(experiment),
        "status": status,
        "return_code": completed.returncode,
        "elapsed_seconds": elapsed,
        "command": command,
        "parameter_fingerprint": provenance["parameter_fingerprint"],
    }


def write_manifest(
    output_root: Path,
    args: argparse.Namespace,
    experiments: list[Experiment],
    results: list[dict[str, object]],
    state: str,
) -> dict[str, object]:
    total = len(experiments)
    manifest = {
        "state": state,
        "arguments": vars(args),
        "number_of_experiments": total,
        "reported": len(results),
        "pending": total - len(results),
        "completed": sum(result["status"] == "completed" for result in results),
        "skipped": sum(result["status"] == "skipped" for result in results),
        "failed": sum(result["status"] == "failed" for result in results),
        "runs": sorted(
            results,
            key=lambda value: (
                value["suite"],
                value["scenario"],
                value["model"],
                value["seed"],
            ),
        ),
    }
    temporary = output_root / "manifest.json.tmp"
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    temporary.replace(output_root / "manifest.json")
    return manifest


def main() -> None:
    args = parse_arguments()
    experiments = build_experiments(args)
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    write_manifest(output_root, args, experiments, results, "running")
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_one, experiment, args): experiment for experiment in experiments}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            write_manifest(output_root, args, experiments, results, "running")
            print(f"{result['status']}: {result['suite']}/{result['scenario']} model={result['model']} seed={result['seed']} elapsed={result['elapsed_seconds']:.1f}s", flush=True)
    manifest = write_manifest(output_root, args, experiments, results, "complete")
    if manifest["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
