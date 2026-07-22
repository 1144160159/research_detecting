from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_final_efficiency_protocol_v2 import file_hash


def replace_option(arguments: Sequence[str], option: str, value: str) -> list[str]:
    result = list(arguments)
    if option in result:
        index = result.index(option)
        if index + 1 >= len(result):
            raise ValueError(f"option has no value: {option}")
        result[index + 1] = value
    else:
        result.extend([option, value])
    return result


def provenance_arguments(
    path: Path, suite: str, scenario: str, expected_trainer: str
) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    task = payload.get("task", {})
    command = payload.get("command")
    if (
        task.get("suite") != suite
        or task.get("scenario") != scenario
        or task.get("seed") != 7
    ):
        raise ValueError(f"source provenance task mismatch: {path}")
    if not isinstance(command, list) or len(command) < 3:
        raise ValueError(f"source provenance command is invalid: {path}")
    if Path(str(command[1])).name != expected_trainer:
        raise ValueError(f"unexpected source trainer: {path}")
    return [str(value) for value in command[2:]]


def seed191_cache_path(readiness: dict[str, Any], suite: str) -> str:
    records = readiness["seed191_training_sentinels"]["artifacts"].get(suite, [])
    if len(records) != 1 or records[0].get("ready") is not True:
        raise ValueError(f"seed191 cache is not uniquely ready: {suite}")
    return str(records[0]["path"])


def _step(role: str, command: list[str], expected: Sequence[Path]) -> dict[str, Any]:
    return {
        "role": role,
        "command": command,
        "expected_files": [str(path) for path in expected],
    }


def create_plan(
    protocol: dict[str, Any],
    coverage: dict[str, Any],
    readiness: dict[str, Any],
    *,
    protocol_file_sha256: str,
    coverage_file_sha256: str,
    readiness_file_sha256: str,
    protocol_path: Path,
    candidate_source_root: Path,
    comparator_source_root: Path,
    output_root: Path,
    python: str,
) -> dict[str, Any]:
    if protocol.get("schema_version") != "strict_v4_final_efficiency_protocol_v2":
        raise ValueError("unexpected efficiency protocol schema")
    if protocol.get("manifest_sha256") != canonical_hash(protocol):
        raise ValueError("efficiency protocol SHA mismatch")
    implementations = protocol.get("implementation_sha256", {})
    if implementations.get("efficiency_execution_plan_creator") != file_hash(Path(__file__)):
        raise ValueError("active execution plan creator SHA mismatch")
    executor_path = Path(__file__).with_name("execute_strict_v4_final_efficiency_plan_v2.py")
    if implementations.get("efficiency_execution_plan_executor") != file_hash(executor_path):
        raise ValueError("active execution plan executor SHA mismatch")
    if coverage.get("schema_version") != "strict_v4_coverage_manifest_v2":
        raise ValueError("unexpected coverage schema")
    if coverage.get("manifest_sha256") != protocol.get("coverage_manifest_sha256"):
        raise ValueError("coverage does not match efficiency protocol")
    if readiness.get("schema_version") != "strict_v4_final_efficiency_cache_readiness_v1":
        raise ValueError("unexpected cache readiness schema")
    if readiness.get("gates", {}).get("formal_timing_allowed") is not True:
        raise ValueError("formal timing cache gate is closed")
    registry = coverage.get("scenario_registry")
    if not isinstance(registry, dict) or sum(item["count"] for item in registry.values()) != 102:
        raise ValueError("execution plan requires 102 frozen scenarios")
    sentinels = protocol["training_calibration_benchmark"]["sentinel_scenarios"]
    repetitions = int(protocol["training_calibration_benchmark"]["clean_process_repetitions"])
    if repetitions != 3 or set(sentinels) != set(registry):
        raise ValueError("training sentinel registry mismatch")

    training_blocks = []
    for suite in sorted(registry):
        scenario = str(sentinels[suite])
        candidate_provenance = (
            candidate_source_root / suite / f"{scenario}_seed7" / "provenance.json"
        )
        comparator_provenance = (
            comparator_source_root
            / suite
            / f"{scenario}_seed7_opendetect"
            / "provenance.json"
        )
        candidate_base = provenance_arguments(
            candidate_provenance, suite, scenario, "train_hybrid_open_set.py"
        )
        comparator_base = provenance_arguments(
            comparator_provenance, suite, scenario, "train_neural_open_set.py"
        )
        cache = seed191_cache_path(readiness, suite)
        for repetition in range(repetitions):
            block_root = output_root / "training" / suite / scenario / f"rep{repetition}"
            commands = {}
            candidate_capture = block_root / "candidate_capture"
            candidate_args = replace_option(candidate_base, "--csv", cache)
            candidate_args = replace_option(candidate_args, "--seed", "191")
            candidate_args = replace_option(
                candidate_args, "--output-dir", str(block_root / "candidate_run")
            )
            commands["candidate"] = _step(
                "candidate_training_capture",
                [
                    python,
                    "capture_pairwise_runtime.py",
                    "--trainer",
                    "train_hybrid_open_set.py",
                    "--capture-dir",
                    str(candidate_capture),
                    "--",
                    *candidate_args,
                ],
                [
                    candidate_capture / "capture_manifest.json",
                    candidate_capture / "equivalence.json",
                    candidate_capture / "pairwise_runtime.joblib",
                ],
            )
            comparator_capture = block_root / "comparator_capture"
            comparator_args = replace_option(comparator_base, "--csv", cache)
            comparator_args = replace_option(comparator_args, "--seed", "191")
            comparator_args = replace_option(comparator_args, "--device", "cuda")
            comparator_args = replace_option(
                comparator_args, "--output-dir", str(block_root / "comparator_run")
            )
            commands["comparator"] = _step(
                "comparator_training_capture",
                [
                    python,
                    "capture_opendetect_training_runtime.py",
                    "--trainer",
                    "train_neural_open_set.py",
                    "--capture-dir",
                    str(comparator_capture),
                    "--",
                    *comparator_args,
                ],
                [
                    comparator_capture / "capture_manifest.json",
                    comparator_capture / "equivalence.json",
                    comparator_capture / "opendetect_runtime.joblib",
                ],
            )
            order = ["candidate", "comparator"] if repetition % 2 == 0 else ["comparator", "candidate"]
            training_blocks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "repetition": repetition,
                    "method_order": order,
                    "steps": [commands[role] for role in order],
                }
            )

    inference_blocks = []
    for suite in sorted(registry):
        for scenario in registry[suite]["scenarios"]:
            candidate_source = candidate_source_root / suite / f"{scenario}_seed7"
            comparator_source = (
                comparator_source_root / suite / f"{scenario}_seed7_opendetect"
            )
            candidate_args = provenance_arguments(
                candidate_source / "provenance.json",
                suite,
                scenario,
                "train_hybrid_open_set.py",
            )
            block_root = output_root / "inference" / suite / scenario
            candidate_capture = block_root / "candidate_capture"
            candidate_args = replace_option(
                candidate_args, "--output-dir", str(block_root / "candidate_run")
            )
            native_capture = block_root / "comparator_native_capture"
            cpu_capture = block_root / "comparator_cpu_capture"
            native_output = block_root / "native_primary" / "efficiency_metrics.json"
            cpu_output = block_root / "cpu_normalized_secondary" / "efficiency_metrics.json"
            candidate_standalone = block_root / "candidate_standalone_benchmark.json"
            native_standalone = block_root / "comparator_native_standalone_benchmark.json"
            cpu_standalone = block_root / "comparator_cpu_standalone_benchmark.json"
            inference_blocks.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "steps": [
                        _step(
                            "candidate_inference_capture",
                            [
                                python,
                                "capture_pairwise_runtime.py",
                                "--trainer",
                                "train_hybrid_open_set.py",
                                "--capture-dir",
                                str(candidate_capture),
                                "--",
                                *candidate_args,
                            ],
                            [candidate_capture / "capture_manifest.json", candidate_capture / "equivalence.json"],
                        ),
                        _step(
                            "comparator_native_capture",
                            [
                                python,
                                "capture_opendetect_runtime.py",
                                "--source-run",
                                str(comparator_source),
                                "--capture-dir",
                                str(native_capture),
                                "--device",
                                "cuda",
                                "--absolute-tolerance",
                                "1e-12",
                                "--equivalence-mode",
                                "same_device_shadow",
                            ],
                            [native_capture / "capture_manifest.json", native_capture / "equivalence.json"],
                        ),
                        _step(
                            "comparator_cpu_capture",
                            [
                                python,
                                "capture_opendetect_runtime.py",
                                "--source-run",
                                str(comparator_source),
                                "--capture-dir",
                                str(cpu_capture),
                                "--device",
                                "cpu",
                                "--absolute-tolerance",
                                "1e-12",
                                "--equivalence-mode",
                                "same_device_shadow",
                            ],
                            [cpu_capture / "capture_manifest.json", cpu_capture / "equivalence.json"],
                        ),
                        _step(
                            "candidate_standalone_benchmark",
                            [
                                python,
                                "benchmark_pairwise_runtime.py",
                                "--runtime",
                                str(candidate_capture / "pairwise_runtime.joblib"),
                                "--inputs",
                                str(candidate_capture / "benchmark_inputs.npz"),
                                "--output",
                                str(candidate_standalone),
                                "--batch-sizes",
                                "1,64,512",
                                "--warmups",
                                "5",
                                "--repetitions",
                                "30",
                            ],
                            [candidate_standalone],
                        ),
                        _step(
                            "comparator_native_standalone_benchmark",
                            [
                                python,
                                "benchmark_opendetect_runtime.py",
                                "--runtime",
                                str(native_capture / "opendetect_runtime.joblib"),
                                "--inputs",
                                str(native_capture / "benchmark_inputs.npz"),
                                "--output",
                                str(native_standalone),
                                "--batch-sizes",
                                "1,64,512",
                                "--warmups",
                                "5",
                                "--repetitions",
                                "30",
                            ],
                            [native_standalone],
                        ),
                        _step(
                            "comparator_cpu_standalone_benchmark",
                            [
                                python,
                                "benchmark_opendetect_runtime.py",
                                "--runtime",
                                str(cpu_capture / "opendetect_runtime.joblib"),
                                "--inputs",
                                str(cpu_capture / "benchmark_inputs.npz"),
                                "--output",
                                str(cpu_standalone),
                                "--batch-sizes",
                                "1,64,512",
                                "--warmups",
                                "5",
                                "--repetitions",
                                "30",
                            ],
                            [cpu_standalone],
                        ),
                        _step(
                            "native_primary_benchmark",
                            [
                                python,
                                "run_strict_v4_final_efficiency_v2.py",
                                "--protocol",
                                str(protocol_path),
                                "--candidate-capture",
                                str(candidate_capture),
                                "--comparator-capture",
                                str(native_capture),
                                "--measurement-mode",
                                "native_primary",
                                "--output",
                                str(native_output),
                            ],
                            [native_output],
                        ),
                        _step(
                            "cpu_normalized_secondary_benchmark",
                            [
                                python,
                                "run_strict_v4_final_efficiency_v2.py",
                                "--protocol",
                                str(protocol_path),
                                "--candidate-capture",
                                str(candidate_capture),
                                "--comparator-capture",
                                str(cpu_capture),
                                "--measurement-mode",
                                "cpu_normalized_secondary",
                                "--output",
                                str(cpu_output),
                            ],
                            [cpu_output],
                        ),
                    ],
                }
            )

    plan = {
        "schema_version": "strict_v4_final_efficiency_execution_plan_v2",
        "status": "frozen_before_formal_efficiency_execution",
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "input_file_sha256": {
            "protocol": protocol_file_sha256,
            "coverage": coverage_file_sha256,
            "cache_readiness": readiness_file_sha256,
        },
        "output_root": str(output_root),
        "formal_metrics_observed_at_plan_freeze": len(
            list(output_root.rglob("efficiency_metrics.json"))
        )
        if output_root.exists()
        else 0,
        "training_blocks": training_blocks,
        "inference_blocks": inference_blocks,
        "expected_training_blocks": 21,
        "expected_inference_blocks": 102,
        "exclusive_gpu_required": True,
        "implementation_sha256": {
            "efficiency_execution_plan_creator": implementations[
                "efficiency_execution_plan_creator"
            ],
            "efficiency_execution_plan_executor": implementations[
                "efficiency_execution_plan_executor"
            ],
            "efficiency_summarizer": implementations["efficiency_summarizer"],
        },
        "unknown_or_test_labels_used_for_planning": False,
    }
    if plan["formal_metrics_observed_at_plan_freeze"] != 0:
        raise ValueError("execution plan must be frozen before formal metrics")
    if len(training_blocks) != 21 or len(inference_blocks) != 102:
        raise ValueError("execution plan block count mismatch")
    plan["manifest_sha256"] = canonical_hash(plan)
    return plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--cache-readiness", type=Path, required=True)
    parser.add_argument("--candidate-source-root", type=Path, required=True)
    parser.add_argument("--comparator-source-root", type=Path, required=True)
    parser.add_argument("--formal-output-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--python", required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    readiness = json.loads(args.cache_readiness.read_text(encoding="utf-8"))
    plan = create_plan(
        protocol,
        coverage,
        readiness,
        protocol_file_sha256=file_hash(args.protocol),
        coverage_file_sha256=file_hash(args.coverage),
        readiness_file_sha256=file_hash(args.cache_readiness),
        protocol_path=args.protocol.resolve(),
        candidate_source_root=args.candidate_source_root.resolve(),
        comparator_source_root=args.comparator_source_root.resolve(),
        output_root=args.formal_output_root.resolve(),
        python=args.python,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "execution_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"manifest_sha256": plan["manifest_sha256"], "training_blocks": 21, "inference_blocks": 102}, sort_keys=True))


if __name__ == "__main__":
    main()
