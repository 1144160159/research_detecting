from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from caeos.pairwise_runtime import snap_to_reference_ties
from capture_pairwise_runtime import build_runtime, run_and_capture


def parse_arguments() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(
        description="Diagnose repeated Pairwise runtime inference without producing formal evidence"
    )
    parser.add_argument("--trainer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("trainer_arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    trainer_arguments = list(args.trainer_arguments)
    if trainer_arguments and trainer_arguments[0] == "--":
        trainer_arguments = trainer_arguments[1:]
    if not trainer_arguments:
        raise ValueError("trainer arguments are required after --")
    return args, trainer_arguments


def max_abs(left: np.ndarray, right: np.ndarray) -> float:
    return float(
        np.max(
            np.abs(
                np.asarray(left, dtype=np.float64)
                - np.asarray(right, dtype=np.float64)
            )
        )
    )


def main() -> None:
    args, trainer_arguments = parse_arguments()
    captured, phase_timings, wall_seconds = run_and_capture(
        str(args.trainer.resolve()), trainer_arguments
    )
    runtime = build_runtime(captured)
    component_runs = []
    output_runs = []
    tail_runs = []
    for _ in range(3):
        components, probability = runtime.component_values(captured["raw_test_views"])
        component_runs.append(components)
        output_runs.append(runtime.predict(captured["raw_test_views"]))
        stabilized = {
            name: snap_to_reference_ties(
                values, runtime.tail_calibrator.reference[name]
            )
            for name, values in components.items()
        }
        tail_runs.append(runtime.tail_calibrator.transform(stabilized))

    component_differences = {}
    stabilized_differences = {}
    tail_differences = {}
    for name in sorted(component_runs[0]):
        component_differences[name] = max(
            max_abs(component_runs[0][name], component_runs[index][name])
            for index in (1, 2)
        )
        stabilized = [
            snap_to_reference_ties(
                run[name], runtime.tail_calibrator.reference[name]
            )
            for run in component_runs
        ]
        stabilized_differences[name] = max(
            max_abs(stabilized[0], stabilized[index]) for index in (1, 2)
        )
        tail_differences[name] = max(
            max_abs(tail_runs[0][name], tail_runs[index][name])
            for index in (1, 2)
        )

    report = {
        "schema_version": "strict_v4_pairwise_runtime_repeatability_diagnostic_v1",
        "formal_evidence": False,
        "selected_risk": runtime.selected_risk,
        "test_count": int(len(output_runs[0]["risk"])),
        "capture_wall_seconds": wall_seconds,
        "phase_timings": phase_timings,
        "prediction_array_equal": all(
            np.array_equal(output_runs[0]["prediction"], output_runs[index]["prediction"])
            for index in (1, 2)
        ),
        "risk_max_absolute_difference": max(
            max_abs(output_runs[0]["risk"], output_runs[index]["risk"])
            for index in (1, 2)
        ),
        "component_max_absolute_difference": max(component_differences.values()),
        "stabilized_component_max_absolute_difference": max(
            stabilized_differences.values()
        ),
        "tail_score_max_absolute_difference": max(tail_differences.values()),
        "component_differences": component_differences,
        "stabilized_component_differences": stabilized_differences,
        "tail_score_differences": tail_differences,
        "unknown_or_test_labels_used_for_runtime_fitting_or_selection": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
