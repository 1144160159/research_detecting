import json
from pathlib import Path

from audit_strict_v4_current_goal_status import (
    DIRECT_TOURNAMENT_IMPLEMENTATION_FILES,
    direct_tournament_terminal_status,
)
from audit_strict_v4_self_algorithm_direct_tournament_confirmation import (
    build_audit,
)
from capture_pairwise_runtime import file_hash
from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_strict_v4_self_algorithm_direct_tournament_confirmation import (
    frozen_challenger_risk,
    split_fingerprint,
)
from summarize_strict_v4_self_algorithm_direct_tournament_confirmation import (
    build_summary,
)
from watch_strict_v4_self_algorithm_direct_tournament_confirmation import (
    resource_state,
)
from write_strict_v4_self_algorithm_direct_tournament_activation import (
    classify_activation,
)


def canonical(value: dict) -> dict:
    value["manifest_sha256"] = canonical_hash(value)
    return value


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def test_activation_requires_exact_dual_positive_goal_state() -> None:
    design_path = (
        Path(__file__).parents[1]
        / "results/strict_v4_self_algorithm_direct_tournament_design_v1/"
        "design.json"
    )
    design = json.loads(design_path.read_text(encoding="utf-8"))
    selection = {
        "final": False,
        "selected_algorithm": "krc_csr_caeos_v1",
        "provisional_challenger": "caeos_pug",
        "krc_rrc_branch": {"terminal": True, "status": "complete"},
        "pug_branch": {
            "terminal": True,
            "status": "cross_suite_positive",
            "cross_suite": {
                "terminal": True,
                "selected_algorithm": "caeos_pug",
            },
        },
        "direct_tournament": {
            "required": True,
            "terminal": False,
            "incumbent": "krc_csr_caeos_v1",
            "challenger": "caeos_pug",
            "status": "fresh_direct_tournament_required",
        },
    }
    goal = canonical(
        {
            "schema_version": "strict_v4_current_goal_status_audit_v1",
            "requirements": {
                "best_self_algorithm_finally_selected": {
                    "satisfied": False,
                    "status": "self_algorithm_direct_tournament_incomplete",
                }
            },
            "evidence": {"self_algorithm_selection": selection},
        }
    )
    activation = classify_activation(
        goal,
        design,
        goal_file_sha256="a" * 64,
        design_file_sha256="b" * 64,
        formal_output_counts={
            "protocol": 0,
            "task_records": 0,
            "summary": 0,
            "audit": 0,
            "completion": 0,
        },
    )

    assert activation["execution_admitted"] is True
    assert activation["incumbent_algorithm"] == "krc_csr_caeos_v1"
    assert activation["challenger_algorithm"] == "caeos_pug"

    selection["pug_branch"]["terminal"] = False
    pending = classify_activation(
        canonical(
            {
                "schema_version": "strict_v4_current_goal_status_audit_v1",
                "requirements": goal["requirements"],
                "evidence": {"self_algorithm_selection": selection},
            }
        ),
        design,
        goal_file_sha256="c" * 64,
        design_file_sha256="b" * 64,
        formal_output_counts={},
    )
    assert pending["activation_required"] is False


def tournament_fixture(root: Path) -> tuple[Path, dict]:
    base = root / "results/strict_v4_self_algorithm_direct_tournament_v1"
    implementation = {}
    for index, relative in enumerate(
        DIRECT_TOURNAMENT_IMPLEMENTATION_FILES
    ):
        path = root / relative
        path.write_text(f"VALUE = {index}\n", encoding="utf-8")
        implementation[relative] = file_hash(path)
    activation = canonical(
        {
            "schema_version": (
                "strict_v4_self_algorithm_direct_tournament_activation_v1"
            ),
            "state": "dual_positive_direct_tournament_admitted",
            "execution_admitted": True,
            "incumbent_algorithm": "krc_csr_caeos_v1",
            "challenger_algorithm": "caeos_pug",
        }
    )
    write_json(base / "activation.json", activation)
    scenarios = {
        f"suite_{suite}": [
            f"scenario_{suite}_{index}"
            for index in range(15 if suite < 4 else 14)
        ]
        for suite in range(7)
    }
    tasks = [
        {
            "identity": f"{suite}/{scenario}/seed{seed}",
            "suite": suite,
            "scenario": scenario,
            "seed": seed,
            "training_seed": seed,
            "corruption_seed": 1000 + seed,
        }
        for suite, names in scenarios.items()
        for scenario in names
        for seed in (809, 811, 821)
    ]
    protocol = canonical(
        {
            "schema_version": (
                "strict_v4_self_algorithm_direct_tournament_protocol_v1"
            ),
            "execution_admitted": True,
            "incumbent_algorithm": "krc_csr_caeos_v1",
            "challenger_algorithm": "caeos_pug",
            "confirmation_universe": {
                "paired_task_count": 306,
                "paired_evaluation_count": 918,
                "conditions": [
                    "clean",
                    "modality_missing",
                    "gaussian_drift",
                ],
                "tasks": tasks,
            },
            "selection_gate": {
                "known_macro_f1_equal_suite_mean_gain_minimum": -0.002,
                "four_unknown_metric_oriented_mean_gain_minimum": 0.005,
                "four_unknown_metric_bootstrap_lower_95_minimum": 0.0,
                "unknown_metric_positive_count_minimum": 3,
                "nonnegative_suite_count_minimum": 5,
                "worst_suite_four_unknown_metric_mean_gain_minimum": -0.02,
            },
            "statistics": {"bootstrap_repetitions": 10000},
            "implementation_sha256": implementation,
            "input_manifest_sha256": {
                "activation": activation["manifest_sha256"]
            },
        }
    )
    protocol_path = base / "protocol.json"
    write_json(protocol_path, protocol)
    records = []
    inventory = []
    for task in tasks:
        conditions = []
        for condition in protocol["confirmation_universe"]["conditions"]:
            incumbent = {
                "known_macro_f1": 0.80,
                "unknown_auroc": 0.80,
                "unknown_aupr": 0.75,
                "unknown_fpr95": 0.30,
                "oscr": 0.70,
            }
            challenger = {
                "known_macro_f1": 0.80,
                "unknown_auroc": 0.81,
                "unknown_aupr": 0.76,
                "unknown_fpr95": 0.29,
                "oscr": 0.71,
            }
            conditions.append(
                {
                    "condition": condition,
                    "incumbent_report": incumbent,
                    "challenger_report": challenger,
                }
            )
        record = canonical(
            {
                "schema_version": (
                    "strict_v4_self_algorithm_direct_tournament_"
                    "task_evaluation_v1"
                ),
                "task": {
                    "identity": task["identity"],
                    "suite": task["suite"],
                    "scenario": task["scenario"],
                    "seed": task["training_seed"],
                },
                "incumbent_algorithm": protocol["incumbent_algorithm"],
                "challenger_algorithm": protocol["challenger_algorithm"],
                "condition_evaluations": conditions,
                "input_evidence": {
                    "protocol_manifest_sha256": protocol["manifest_sha256"]
                },
            }
        )
        record_path = (
            base
            / "task_records"
            / task["suite"]
            / task["scenario"]
            / f"seed{task['training_seed']}"
            / "evaluation.json"
        )
        write_json(record_path, record)
        records.append(record)
        inventory.append(
            {
                "path": record_path.relative_to(base).as_posix(),
                "file_sha256": file_hash(record_path),
                "manifest_sha256": record["manifest_sha256"],
            }
        )
    summary = build_summary(protocol, records, inventory)
    write_json(base / "summary.json", summary)
    audit = build_audit(
        project_root=root,
        protocol_path=protocol_path,
        result_root=base,
    )
    write_json(base / "audit.json", audit)
    completion = canonical(
        {
            "schema_version": (
                "strict_v4_self_algorithm_direct_tournament_completion_v1"
            ),
            "state": "complete",
            "protocol_manifest_sha256": protocol["manifest_sha256"],
            "protocol_file_sha256": file_hash(protocol_path),
            "summary_manifest_sha256": summary["manifest_sha256"],
            "summary_file_sha256": file_hash(base / "summary.json"),
            "audit_manifest_sha256": audit["manifest_sha256"],
            "audit_file_sha256": file_hash(base / "audit.json"),
            "integrity_passes": True,
            "challenger_gate_passes": True,
            "selected_algorithm": "caeos_pug",
        }
    )
    write_json(base / "execution_complete.json", completion)
    return base, protocol


def test_positive_tournament_closes_independent_terminal_selection(
    tmp_path: Path,
) -> None:
    base, _protocol = tournament_fixture(tmp_path)

    status = direct_tournament_terminal_status(tmp_path)

    assert status["terminal"] is True
    assert status["selected_algorithm"] == "caeos_pug"
    assert status["challenger_gate_passes"] is True

    completion = json.loads(
        (base / "execution_complete.json").read_text(encoding="utf-8")
    )
    completion["selected_algorithm"] = "krc_csr_caeos_v1"
    write_json(base / "execution_complete.json", completion)
    invalid = direct_tournament_terminal_status(tmp_path)
    assert invalid["terminal"] is False


def test_resource_gate_requires_three_clean_observable_polls() -> None:
    state, idle = resource_state(
        prior_idle_count=2,
        required_idle_polls=3,
        max_load_fraction=0.25,
        commands=[],
        load1=1.0,
        logical_cpu_count=16,
        gpu_pids=[],
    )
    assert idle == 3
    assert state["launch_admitted"] is True

    busy, idle = resource_state(
        prior_idle_count=2,
        required_idle_polls=3,
        max_load_fraction=0.25,
        commands=["python train_hybrid_open_set.py"],
        load1=1.0,
        logical_cpu_count=16,
        gpu_pids=[],
    )
    assert idle == 0
    assert busy["launch_admitted"] is False


def test_split_fingerprint_accepts_only_bound_combined_sha256() -> None:
    value = "a" * 64
    assert split_fingerprint({"combined": value}) == value
    assert split_fingerprint(value) == value


def test_challenger_runtime_must_use_frozen_pug_risk() -> None:
    class Runtime:
        def __init__(self, selected: str):
            self.selected = selected

        def evidence(self) -> dict:
            return {"selected_risk": self.selected}

    protocol = {
        "candidate_training": {
            "pug_execution_controls": {
                "candidate_risk_selection": (
                    "nested_pug_continuous_outer_min_p"
                )
            }
        }
    }
    assert frozen_challenger_risk(
        protocol, Runtime("nested_pug_continuous_outer_min_p")
    ) == "nested_pug_continuous_outer_min_p"

    try:
        frozen_challenger_risk(protocol, Runtime("support_union"))
    except ValueError as error:
        assert "frozen PUG risk" in str(error)
    else:
        raise AssertionError("runtime risk drift must fail closed")
