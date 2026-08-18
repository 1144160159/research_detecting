from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

import evaluate_strict_v4_fhmm_calibrated_aggregation_development as base
from strict_v4_cicids2017_attack_family import (
    atomic_json,
    canonical_hash,
    file_hash,
    load_canonical,
)


def repeat_gates(
    operational: dict[str, float],
    research: dict[str, float],
    targets: dict[str, float],
) -> dict[str, bool]:
    user_warning = (
        operational["alert_accuracy"] >= targets["alert_accuracy_minimum"]
        and operational["benign_fpr"] < targets["benign_fpr_strictly_below"]
    )
    primary = (
        user_warning
        and operational["known_attack_type_accuracy"]
        >= targets["known_attack_type_accuracy_minimum"]
        and operational["unknown_attack_alert_recall"]
        >= targets["unknown_attack_alert_recall_minimum"]
        and operational["unknown_attack_recall"]
        >= targets["unknown_attack_rejection_recall_minimum"]
        and research["unknown_auroc"] >= targets["unknown_auroc_minimum"]
        and research["oscr_exact_v2"] >= targets["oscr_minimum"]
    )
    full_typed = (
        user_warning
        and operational["known_attack_type_accuracy"] >= 0.95
        and operational["unknown_attack_alert_recall"] >= 0.95
    )
    return {
        "user_warning_95_5": user_warning,
        "primary_known_unknown_confirmation": primary,
        "full_typed_known_unknown_95_5": full_typed,
    }


def verify_implementations(
    protocol: dict[str, Any],
    required_names: tuple[str, ...],
) -> None:
    project_root = Path(protocol["paths"]["project_root"]).resolve()
    expected = protocol["implementation_sha256"]
    for name in required_names:
        path = project_root / name
        if expected.get(name) != file_hash(path):
            raise ValueError(f"confirmation implementation drifted: {name}")


def evaluate(
    protocol_path: Path,
    repeats: list[tuple[int, list[Path]]],
) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    protocol = load_canonical(protocol_path, "FHMM-S confirmation protocol")
    if protocol["state"] != "frozen_before_fresh_training":
        raise ValueError("confirmation protocol is not frozen")
    verify_implementations(
        protocol,
        (
            Path(__file__).name,
            "evaluate_strict_v4_fhmm_calibrated_aggregation_development.py",
            "strict_v4_open_set_metric_contract_v2.py",
        ),
    )
    expected_tasks = {
        int(task["split_seed"]): [int(seed) for seed in task["model_seeds"]]
        for task in protocol["tasks"]
    }
    observed_tasks = {
        split_seed: [
            int(path.name.rsplit("model", 1)[1]) for path in member_dirs
        ]
        for split_seed, member_dirs in repeats
    }
    if observed_tasks != expected_tasks:
        raise ValueError(
            f"confirmation task identity mismatch: {observed_tasks}"
        )
    prepared = {
        str(split_seed): base.prepare_repeat(split_seed, member_dirs)
        for split_seed, member_dirs in repeats
    }
    configuration = dict(protocol["fixed_configuration"])
    targets = dict(protocol["evaluation_targets"])
    per_repeat = {}
    for identity, values in prepared.items():
        evaluated = base.evaluate_repeat(values, configuration)
        research = base.compact_research(evaluated["research"])
        per_repeat[identity] = {
            "operational": evaluated["operational"],
            "research_main": research,
            "gates": repeat_gates(
                evaluated["operational"],
                research,
                targets,
            ),
            "thresholds": evaluated["thresholds"],
            "validation_alert_calibration": evaluated[
                "validation_alert_calibration"
            ],
            "type_selection": values["type_selection"],
            "members": values["source"],
        }
    operational_names = tuple(
        next(iter(per_repeat.values()))["operational"]
    )
    research_names = tuple(
        next(iter(per_repeat.values()))["research_main"]
    )
    macro = {
        "operational": {
            name: float(
                np.mean(
                    [
                        value["operational"][name]
                        for value in per_repeat.values()
                    ]
                )
            )
            for name in operational_names
        },
        "research_main": {
            name: float(
                np.mean(
                    [
                        value["research_main"][name]
                        for value in per_repeat.values()
                    ]
                )
            )
            for name in research_names
        },
    }
    gate_names = tuple(next(iter(per_repeat.values()))["gates"])
    all_repeat_gates = {
        name: all(value["gates"][name] for value in per_repeat.values())
        for name in gate_names
    }
    result: dict[str, Any] = {
        "schema_version": "strict_v4_fhmm_stable_confirmation_v1",
        "state": (
            "confirmation_primary_gate_passed"
            if all_repeat_gates["primary_known_unknown_confirmation"]
            else "confirmation_primary_gate_not_met"
        ),
        "fixed_configuration": configuration,
        "evaluation_targets": targets,
        "repeat_count": len(per_repeat),
        "per_repeat": per_repeat,
        "macro_mean": macro,
        "all_repeat_gates": all_repeat_gates,
        "protocol": {
            "path": str(protocol_path),
            "file_sha256": file_hash(protocol_path),
            "manifest_sha256": protocol["manifest_sha256"],
        },
        "claim_boundary": {
            "fresh_split_confirmation": True,
            "true_unknown_used_for_training_or_threshold_selection": False,
            "configuration_was_frozen_before_member_training": True,
            "no_candidate_search_or_weight_selection": True,
            "full_typed_95_5_is_reported_separately": True,
        },
    }
    result["manifest_sha256"] = canonical_hash(result)
    return result


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument(
        "--repeat",
        action="append",
        nargs=4,
        metavar=("SPLIT_SEED", "MEMBER1", "MEMBER2", "MEMBER3"),
        required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    repeats = [
        (int(values[0]), [Path(value) for value in values[1:]])
        for values in args.repeat
    ]
    result = evaluate(args.protocol, repeats)
    atomic_json(args.output.resolve(), result)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
