from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from audit_csr_caeos_pilot import audit
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_csr_caeos_runtime import evaluate
from summarize_csr_caeos_pilot import (
    clean_admission,
    load_json,
    summarize,
)


def validate_protocol(value: Dict[str, Any]) -> None:
    if (
        value.get("schema_version")
        != "strict_v4_csr_caeos_pilot_protocol_v1"
        or value.get("manifest_sha256") != canonical_hash(value)
        or value.get("execution_admitted") is not True
    ):
        raise ValueError("valid admitted CSR pilot protocol required")


def validate_capture(
    path: Path, suite: str, scenario: str, weight: float
) -> bool:
    if not path.is_file():
        if path.parent.exists() and any(path.parent.iterdir()):
            raise ValueError(f"partial CSR capture directory: {path.parent}")
        return False
    value = load_json(path)
    if (
        value.get("schema_version")
        != "strict_v4_csr_caeos_runtime_capture_v1"
        or value.get("state") != "complete"
        or value.get("algorithm") != "csr_caeos_v1"
        or value.get("task") != {"suite": suite, "scenario": scenario}
        or float(value.get("weight", -1.0)) != float(weight)
        or value.get("roundtrip", {}).get("passes") is not True
        or value.get("test_effect_metrics_computed") is not False
    ):
        raise ValueError(f"invalid CSR capture: {path}")
    root = path.parent
    for name, hash_name in (
        ("runtime_artifact", "runtime_artifact_sha256"),
        ("evaluation_inputs", "evaluation_inputs_sha256"),
    ):
        if file_hash(root / value[name]) != value[hash_name]:
            raise ValueError(f"CSR capture hash mismatch: {path}")
    return True


def write_canonical(path: Path, value: Dict[str, Any]) -> None:
    if value.get("manifest_sha256") != canonical_hash(value):
        raise ValueError("canonical output required")
    if path.exists():
        if load_json(path) != value:
            raise ValueError(f"existing output differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run(
    protocol_path: Path,
    run_root: Path,
    result_root: Path,
    project_root: Path,
) -> Dict[str, Any]:
    protocol = load_json(protocol_path)
    validate_protocol(protocol)
    design_path = project_root / protocol["design_path"]
    design = load_json(design_path)
    if (
        design.get("schema_version") != "strict_v4_csr_caeos_design_v4"
        or design["manifest_sha256"] != protocol["design_manifest_sha256"]
        or file_hash(design_path) != protocol["input_file_sha256"]["design"]
    ):
        raise ValueError("CSR protocol/design binding mismatch")
    captures_root = run_root / "captures"
    evaluations_root = run_root / "evaluations"
    captures_root.mkdir(parents=True, exist_ok=True)
    weight = float(design["mechanism"]["fixed_augmentation_weight"])
    sources = {
        (record["suite"], record["scenario"]): record
        for record in protocol["source_registry"]
    }
    completed_captures = 0
    for suite, scenarios in sorted(
        design["development"]["scenarios"].items()
    ):
        for scenario in scenarios:
            source = sources[(suite, scenario)]
            capture_dir = captures_root / suite / scenario
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
                    str(design["mechanism"]["training_sample_fraction"]),
                    "--training-seed",
                    str(design["development"]["training_seed"]),
                    "--augmentation-seed",
                    str(design["development"]["augmentation_seed"]),
                    "--health-quantile",
                    str(
                        design["mechanism"][
                            "legacy_health_quantile_argument"
                        ]["value"]
                    ),
                    "--validation-corruption-seed",
                    str(design["development"]["corruption_seed"]),
                    "--",
                    *source["base_trainer_arguments"],
                ]
                subprocess.run(command, cwd=project_root, check=True)
                validate_capture(
                    manifest_path, suite, scenario, weight
                )
            completed_captures += 1
            print(
                f"capture={completed_captures}/14 "
                f"suite={suite} scenario={scenario}",
                flush=True,
            )

    admission = clean_admission(
        design,
        sorted(captures_root.rglob("capture_manifest.json")),
    )
    admission_path = result_root / "clean_admission.json"
    write_canonical(admission_path, admission)
    if admission["passes"] is not True:
        rejection = {
            "schema_version": "strict_v4_csr_caeos_pilot_rejection_v1",
            "state": "rejected_on_known_validation_only",
            "design_manifest_sha256": design["manifest_sha256"],
            "clean_admission_manifest_sha256": admission[
                "manifest_sha256"
            ],
            "evaluation_count": 0,
            "selected_algorithm": "caeos_pairwise",
            "reason": "csr_clean_admission_failed",
            "unknown_or_test_labels_used": False,
        }
        rejection["manifest_sha256"] = canonical_hash(rejection)
        write_canonical(result_root / "rejection.json", rejection)
        (result_root / "pilot_complete").write_text(
            rejection["manifest_sha256"] + "\n", encoding="utf-8"
        )
        return {
            "capture_count": completed_captures,
            "evaluation_count": 0,
            "passes": False,
            "state": "rejected_on_known_validation_only",
        }

    evaluations_root.mkdir(parents=True, exist_ok=True)
    completed_evaluations = 0
    for suite, scenarios in sorted(
        design["development"]["scenarios"].items()
    ):
        for scenario in scenarios:
            capture_dir = captures_root / suite / scenario
            for condition in design["development"]["conditions"]:
                output = (
                    evaluations_root
                    / suite
                    / scenario
                    / condition
                    / "evaluation.json"
                )
                if output.exists():
                    value = load_json(output)
                    if (
                        value.get("manifest_sha256")
                        != canonical_hash(value)
                        or value.get("design_manifest_sha256")
                        != design["manifest_sha256"]
                        or value.get("condition") != condition
                    ):
                        raise ValueError(
                            f"invalid existing CSR evaluation: {output}"
                        )
                elif output.parent.exists() and any(
                    output.parent.iterdir()
                ):
                    raise ValueError(
                        f"partial CSR evaluation directory: {output.parent}"
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
                    f"evaluation={completed_evaluations}/84 "
                    f"suite={suite} scenario={scenario} "
                    f"condition={condition}",
                    flush=True,
                )
    evaluation_paths = sorted(
        evaluations_root.rglob("evaluation.json")
    )
    summary = summarize(design, admission, evaluation_paths)
    summary_path = result_root / "summary.json"
    write_canonical(summary_path, summary)
    audited = audit(
        design,
        admission,
        summary,
        sorted(captures_root.rglob("capture_manifest.json")),
        evaluation_paths,
        implementation_file_sha256=protocol["implementation_sha256"],
    )
    audit_path = result_root / "audit.json"
    write_canonical(audit_path, audited)
    if audited["passes"] is not True:
        raise RuntimeError("CSR pilot integrity audit failed")
    (result_root / "pilot_complete").write_text(
        audited["manifest_sha256"] + "\n", encoding="utf-8"
    )
    return {
        "capture_count": completed_captures,
        "evaluation_count": completed_evaluations,
        "passes": bool(summary["passes"]),
        "state": "complete",
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
