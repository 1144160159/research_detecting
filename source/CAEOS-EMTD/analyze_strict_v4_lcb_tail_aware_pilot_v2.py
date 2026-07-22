from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from analyze_strict_v4_lcb_tail_aware_pilot import (
    analyze as analyze_v1,
    render,
)
from create_strict_v4_external_confirmation_protocol import canonical_hash, file_hash
from create_strict_v4_lcb_analysis_correction import (
    CORRECTED_ANALYZER,
    FROZEN_ANALYZER,
)


FROZEN_COMMAND_ARGUMENTS = {
    "--pseudo-unknown-max-alpha": ("pseudo_unknown_max_alpha", "maximum_alpha"),
    "--pseudo-unknown-min-fold-gain": (
        "pseudo_unknown_min_fold_gain",
        "minimum_fold_gain",
    ),
    "--boundary-hard-pseudo-fraction": (
        "boundary_hard_pseudo_fraction",
        "hard_pseudo_fraction",
    ),
    "--boundary-interpolation": ("boundary_interpolation", "boundary_interpolation"),
    "--boundary-max-per-task": ("boundary_max_per_task", "boundary_max_per_task"),
    "--tail-aware-confidence-z": ("tail_aware_confidence_z", "confidence_z"),
    "--tail-aware-min-metric-lcb-gain": (
        "tail_aware_min_metric_lcb_gain",
        "minimum_metric_lcb_gain",
    ),
    "--tail-aware-min-aupr-lcb-gain": (
        "tail_aware_min_aupr_lcb_gain",
        "minimum_aupr_lcb_gain",
    ),
    "--tail-aware-min-aupr-fold-gain": (
        "tail_aware_min_aupr_fold_gain",
        "minimum_aupr_fold_gain",
    ),
}


def command_value(command: list[str], flag: str) -> str:
    indices = [index for index, value in enumerate(command) if value == flag]
    if len(indices) != 1 or indices[0] + 1 >= len(command):
        raise ValueError(f"LCB provenance command flag mismatch: {flag}")
    return str(command[indices[0] + 1])


def analyze(protocol: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    expected_policy = str(protocol["candidate"]["risk_policy_name"])
    normalized = deepcopy(rows)
    for row in normalized:
        payload = row["metrics"]
        arguments = payload.get("arguments", {})
        provenance = row.get("provenance", {})
        task = provenance.get("task", {})
        if (
            task.get("suite") != row["suite"]
            or task.get("scenario") != row["scenario"]
            or int(task.get("seed", -1)) != int(row["seed"])
        ):
            raise ValueError("LCB provenance task identity mismatch")
        command = [str(value) for value in provenance.get("command", [])]
        if command_value(command, "--risk-selection") != protocol["candidate"][
            "risk_selection"
        ]:
            raise ValueError("LCB provenance risk selection mismatch")
        if command_value(command, "--risk-policy-name") != expected_policy:
            raise ValueError("LCB provenance risk policy mismatch")
        if int(command_value(command, "--seed")) != int(row["seed"]):
            raise ValueError("LCB provenance seed mismatch")
        if payload.get("risk_policy") != expected_policy:
            raise ValueError("LCB top-level risk policy mismatch")
        if arguments.get("risk_policy") != expected_policy:
            raise ValueError("LCB arguments risk policy mismatch")
        legacy = arguments.get("risk_policy_name")
        if legacy is not None and legacy != expected_policy:
            raise ValueError("LCB legacy risk policy field mismatch")
        arguments["risk_policy_name"] = arguments["risk_policy"]
        for flag, (argument_name, protocol_name) in FROZEN_COMMAND_ARGUMENTS.items():
            observed = float(command_value(command, flag))
            expected = float(protocol["candidate"][protocol_name])
            if observed != expected:
                raise ValueError(f"LCB provenance frozen argument mismatch: {flag}")
            arguments[argument_name] = observed
    result = analyze_v1(protocol, normalized)
    result["schema_version"] = "strict_v4_lcb_tail_aware_pilot_analysis_v2"
    result["validation"]["deployed_risk_policy_schema_validated"] = True
    return result


def validate_correction(
    correction: dict[str, Any], protocol: dict[str, Any], protocol_path: Path
) -> None:
    if correction.get("schema_version") != "strict_v4_lcb_analysis_schema_correction_v1":
        raise ValueError("unexpected LCB analysis correction schema")
    if correction.get("manifest_sha256") != canonical_hash(correction):
        raise ValueError("LCB analysis correction SHA mismatch")
    if correction.get("source_protocol_file_sha256") != file_hash(protocol_path):
        raise ValueError("LCB correction source protocol file SHA mismatch")
    if correction.get("source_protocol_manifest_sha256") != protocol.get(
        "manifest_sha256"
    ):
        raise ValueError("LCB correction source protocol manifest mismatch")
    frozen = correction.get("frozen_analyzer", {})
    if frozen.get("path") != FROZEN_ANALYZER or frozen.get("sha256") != protocol.get(
        "implementation_sha256", {}
    ).get(FROZEN_ANALYZER):
        raise ValueError("LCB correction frozen analyzer binding mismatch")
    corrected = correction.get("corrected_analyzer", {})
    if corrected.get("path") != CORRECTED_ANALYZER or corrected.get(
        "sha256"
    ) != file_hash(Path(__file__).resolve()):
        raise ValueError("LCB corrected analyzer implementation mismatch")
    scope = correction.get("correction", {})
    required_true = {
        "training_outputs_unchanged",
        "scenario_set_unchanged",
        "candidate_parameters_unchanged",
        "selection_and_expansion_gates_unchanged",
    }
    if not all(scope.get(name) is True for name in required_true):
        raise ValueError("LCB analysis correction scope is unsafe")
    if scope.get("test_labels_used_for_new_parameter_selection") is not False:
        raise ValueError("LCB analysis correction leakage boundary is unsafe")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--correction", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text(encoding="utf-8"))
    correction = json.loads(args.correction.read_text(encoding="utf-8"))
    validate_correction(correction, protocol, args.protocol)
    seed = int(protocol["pilot"]["development_seed"])
    rows = []
    for suite, scenarios in protocol["pilot"]["scenarios"].items():
        for scenario in scenarios:
            path = args.run_root / suite / f"{scenario}_seed{seed}" / "metrics.json"
            rows.append(
                {
                    "suite": suite,
                    "scenario": scenario,
                    "seed": seed,
                    "metrics": json.loads(path.read_text(encoding="utf-8")),
                    "provenance": json.loads(
                        (path.parent / "provenance.json").read_text(encoding="utf-8")
                    ),
                }
            )
    result = analyze(protocol, rows)
    result["analysis_correction_manifest_sha256"] = correction["manifest_sha256"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "analysis.md").write_text(render(result), encoding="utf-8")
    (args.output_dir / "pilot_complete").write_text(
        correction["manifest_sha256"] + "\n", encoding="ascii"
    )
    print(render(result), end="")


if __name__ == "__main__":
    main()
