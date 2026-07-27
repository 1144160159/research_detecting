from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from caeos.pseudo_unknown_gated_continuous import (
    PAIRWISE_REFERENCE_RISK,
    PUG_RISK_NAME,
    PUG_SELECTION_NAME,
)


REQUIRED_ARTIFACTS = ("metrics.json", "scores.npz", "evidence_package.npz")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scalar_text(array: Any, name: str) -> str:
    value = np.asarray(array)
    if value.ndim != 0:
        raise ValueError(f"{name} must be scalar")
    return str(value.item())


def inspect_run(run_dir: Path) -> dict[str, Any]:
    paths = {name: run_dir / name for name in REQUIRED_ARTIFACTS}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing:
        raise ValueError("missing PUG run artifacts: " + ", ".join(missing))

    metrics = json.loads(paths["metrics.json"].read_text(encoding="utf-8"))
    selected = str(metrics.get("selected_risk", ""))
    if not selected:
        raise ValueError("metrics.json has no selected_risk")
    if metrics.get("risk_selection") != PUG_SELECTION_NAME:
        raise ValueError("run does not use the frozen PUG selection route")

    details = metrics.get("risk_selection_details")
    if not isinstance(details, dict):
        raise ValueError("risk_selection_details must be an object")
    gate = details.get("pug_continuous_outer_gate")
    if not isinstance(gate, dict):
        raise ValueError("PUG gate evidence is absent")
    if gate.get("selection_uses_unknown_or_test_labels") is not False:
        raise ValueError("PUG gate is not isolated from unknown/test labels")
    if details.get("unknown_or_test_labels_used_for_selection") is not False:
        raise ValueError("selection is not isolated from unknown/test labels")
    if details.get("selected_risk") != selected:
        raise ValueError("selection details disagree with metrics selected_risk")

    gate_passes = gate.get("passes")
    pug_selected = details.get("pug_selected")
    eligible = details.get("pug_base_route_eligible")
    pairwise_base = details.get("pairwise_base_selected_risk")
    if not isinstance(gate_passes, bool) or not isinstance(pug_selected, bool):
        raise ValueError("PUG gate and route decisions must be boolean")
    if not isinstance(eligible, bool):
        raise ValueError("PUG route eligibility must be boolean")
    expected_selected = (
        PUG_RISK_NAME
        if eligible and gate_passes
        else str(pairwise_base)
    )
    if selected != expected_selected:
        raise ValueError("selected risk violates the frozen PUG route decision")
    if pug_selected != (selected == PUG_RISK_NAME):
        raise ValueError("pug_selected disagrees with selected_risk")
    if eligible != (pairwise_base == PAIRWISE_REFERENCE_RISK):
        raise ValueError("PUG eligibility disagrees with the Pairwise base route")

    reports = metrics.get("reports")
    if not isinstance(reports, dict) or selected not in reports:
        raise ValueError("selected risk report is absent")
    if metrics.get("selected_report") != reports[selected]:
        raise ValueError("selected_report disagrees with reports[selected_risk]")

    validation_key = f"validation_{selected}"
    test_key = f"test_{selected}"
    pug_keys = (
        f"validation_{PUG_RISK_NAME}",
        f"test_{PUG_RISK_NAME}",
    )
    with np.load(paths["scores.npz"], allow_pickle=False) as scores, np.load(
        paths["evidence_package.npz"], allow_pickle=False
    ) as evidence:
        for key in (validation_key, test_key, *pug_keys):
            if key not in scores:
                raise ValueError(f"scores.npz is missing {key}")
        evidence_selected = scalar_text(
            evidence["selected_risk_name"], "selected_risk_name"
        )
        if evidence_selected != selected:
            raise ValueError("evidence package disagrees with selected_risk")
        if not np.array_equal(
            evidence["validation_selected_risk"], scores[validation_key]
        ):
            raise ValueError("validation selected-risk arrays disagree")
        if not np.array_equal(evidence["test_selected_risk"], scores[test_key]):
            raise ValueError("test selected-risk arrays disagree")
        threshold = float(np.asarray(evidence["selected_threshold"]).item())
        expected_rejected = np.asarray(scores[test_key]) > threshold
        if not np.array_equal(evidence["test_rejected"], expected_rejected):
            raise ValueError("test rejection decisions disagree with threshold")

    aggregates = gate.get("aggregates", {})
    checks = gate.get("checks", {})
    return {
        "schema_version": "strict_v4_pug_run_inspection_v1",
        "run_dir": str(run_dir.resolve()),
        "artifact_sha256": {
            name: file_sha256(path) for name, path in paths.items()
        },
        "selected_risk": selected,
        "pairwise_base_selected_risk": pairwise_base,
        "pug_base_route_eligible": eligible,
        "pug_gate_passes": gate_passes,
        "pug_selected": pug_selected,
        "pseudo_unknown_fold_count": int(gate.get("fold_count", 0)),
        "gate_checks": checks,
        "gate_aggregates": aggregates,
        "unknown_or_test_labels_used_for_selection": False,
        "cross_artifact_selected_risk_consistent": True,
        "selected_arrays_exact": True,
        "inspection_passes": True,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect an isolated or formal strict-v4 PUG run."
    )
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = inspect_run(args.run_dir)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
