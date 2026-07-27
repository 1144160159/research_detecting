from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_mdr_caeos_runtime import evaluate
from select_mdr_caeos_weight import load, select
from capture_pairwise_runtime import file_hash


def weight_directory(weight: float) -> str:
    return f"weight_{float(weight):.3f}".replace(".", "p")


def validate_protocol(value: Dict[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "strict_v4_mdr_caeos_pilot_execution_protocol_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
    ):
        raise ValueError("invalid MDR pilot execution protocol")
    if value.get("execution_admitted") is not True:
        raise ValueError("MDR pilot execution is not admitted")


def validate_capture(path: Path, suite: str, scenario: str, weight: float) -> bool:
    if not path.is_file():
        return False
    value = load(path)
    if (
        value.get("schema_version")
        != "strict_v4_mdr_caeos_runtime_capture_v1"
        or value.get("state") != "complete"
        or value.get("task") != {"suite": suite, "scenario": scenario}
        or float(value.get("weight", -1.0)) != float(weight)
        or value.get("roundtrip", {}).get("passes") is not True
    ):
        raise ValueError(f"invalid existing MDR capture: {path}")
    root = path.parent
    if (
        file_hash(root / value["runtime_artifact"])
        != value["runtime_artifact_sha256"]
        or file_hash(root / value["evaluation_inputs"])
        != value["evaluation_inputs_sha256"]
    ):
        raise ValueError(f"existing MDR capture hash mismatch: {path}")
    return True


def run(
    protocol_path: Path,
    run_root: Path,
    result_root: Path,
    project_root: Path,
) -> Dict[str, int]:
    protocol = load(protocol_path)
    validate_protocol(protocol)
    design_path = project_root / protocol["design_path"]
    design = load(design_path)
    if design["manifest_sha256"] != protocol["design_manifest_sha256"]:
        raise ValueError("MDR execution/design binding mismatch")
    captures_root = run_root / "captures"
    evaluations_root = run_root / "evaluations"
    captures_root.mkdir(parents=True, exist_ok=True)
    evaluations_root.mkdir(parents=True, exist_ok=True)
    weights = [
        float(value)
        for value in design["mechanism"][
            "training_augmentation_weight_grid"
        ]
    ]
    sources = {
        (record["suite"], record["scenario"]): record
        for record in protocol["source_registry"]
    }
    completed_captures = 0
    for suite, scenarios in sorted(design["pilot"]["scenarios"].items()):
        for scenario in scenarios:
            source = sources[(suite, scenario)]
            for weight in weights:
                capture_dir = (
                    captures_root
                    / suite
                    / scenario
                    / weight_directory(weight)
                )
                manifest_path = capture_dir / "capture_manifest.json"
                if not validate_capture(
                    manifest_path, suite, scenario, weight
                ):
                    command: List[str] = [
                        sys.executable,
                        str(project_root / protocol["implementation"]["capture"]),
                        "--clean-trainer",
                        str(
                            project_root
                            / protocol["implementation"]["clean_trainer"]
                        ),
                        "--robust-trainer",
                        str(
                            project_root
                            / protocol["implementation"]["robust_trainer"]
                        ),
                        "--capture-dir",
                        str(capture_dir),
                        "--suite",
                        suite,
                        "--scenario",
                        scenario,
                        "--weight",
                        str(weight),
                        "--sample-fraction",
                        str(
                            design["mechanism"][
                                "training_sample_fraction"
                            ]
                        ),
                        "--training-seed",
                        str(design["pilot"]["training_seed"]),
                        "--augmentation-seed",
                        str(design["pilot"]["training_seed"]),
                        "--health-quantile",
                        str(
                            design["mechanism"]["health_gate"]["quantile"]
                        ),
                        "--validation-corruption-seed",
                        str(design["pilot"]["corruption_seed"]),
                        "--",
                        *source["base_trainer_arguments"],
                    ]
                    subprocess.run(command, cwd=project_root, check=True)
                    validate_capture(
                        manifest_path, suite, scenario, weight
                    )
                completed_captures += 1
                print(
                    f"capture={completed_captures}/"
                    f"{design['pilot']['scenario_count'] * len(weights)} "
                    f"suite={suite} scenario={scenario} weight={weight}",
                    flush=True,
                )

    paths = sorted(captures_root.rglob("capture_manifest.json"))
    selection_path = result_root / "weight_selection.json"
    selection = select(
        design,
        [load(path) for path in paths],
        [file_hash(path) for path in paths],
    )
    if selection_path.exists():
        existing = load(selection_path)
        if existing != selection:
            raise ValueError("existing MDR weight selection differs")
    else:
        selection_path.parent.mkdir(parents=True, exist_ok=True)
        selection_path.write_text(
            json.dumps(selection, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    selected_weight = float(selection["selected_weight"])

    completed_evaluations = 0
    for suite, scenarios in sorted(design["pilot"]["scenarios"].items()):
        for scenario in scenarios:
            capture_dir = (
                captures_root
                / suite
                / scenario
                / weight_directory(selected_weight)
            )
            for condition in design["pilot"]["conditions"]:
                output = (
                    evaluations_root
                    / suite
                    / scenario
                    / condition
                    / "evaluation.json"
                )
                if output.exists():
                    value = load(output)
                    if (
                        value.get("manifest_sha256")
                        != canonical_hash(value)
                        or value.get("design_manifest_sha256")
                        != design["manifest_sha256"]
                        or value.get("condition") != condition
                    ):
                        raise ValueError(
                            f"invalid existing MDR evaluation: {output}"
                        )
                else:
                    evaluate(
                        capture_dir,
                        design,
                        suite=suite,
                        scenario=scenario,
                        condition=condition,
                        output=output,
                    )
                completed_evaluations += 1
                print(
                    f"evaluation={completed_evaluations}/"
                    f"{design['pilot']['expected_evaluations']} "
                    f"suite={suite} scenario={scenario} "
                    f"condition={condition}",
                    flush=True,
                )
    return {
        "capture_count": completed_captures,
        "evaluation_count": completed_evaluations,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--project-root", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.protocol.resolve(),
        args.run_root.resolve(),
        args.result_root.resolve(),
        args.project_root.resolve(),
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
