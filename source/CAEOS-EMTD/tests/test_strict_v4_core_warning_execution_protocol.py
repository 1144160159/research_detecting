import json
from pathlib import Path

from create_strict_v4_core_warning_execution_protocol import (
    DEVELOPMENT_BUDGETS,
    IMPLEMENTATION_FILES,
    canonical_hash,
    create_protocol,
)


def write_manifest(path: Path, payload: dict) -> None:
    payload = dict(payload)
    payload["manifest_sha256"] = canonical_hash(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_execution_protocol_freezes_fresh_seed_boundary(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    for relative in IMPLEMENTATION_FILES:
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(relative, encoding="utf-8")

    core = project / "results/core/protocol.json"
    write_manifest(
        core,
        {
            "schema_version": "strict_v4_core_warning_protocol_v1",
            "status": "frozen_before_fresh_seed_confirmation",
            "core_confirmation": {
                "fresh_seeds": [907, 911, 919],
                "datasets": ["cicids2017"],
            },
        },
    )
    candidate = project / "results/candidate.json"
    candidate.parent.mkdir(parents=True, exist_ok=True)
    candidate.write_text(
        json.dumps(
            {
                "candidate": {
                    "maximum_alpha": 0.25,
                    "minimum_fold_gain": 0.0,
                    "hard_pseudo_fraction": 0.1,
                    "interpolation": 0.5,
                    "max_per_task": 1000,
                    "training_objective": "pairwise",
                }
            }
        ),
        encoding="utf-8",
    )
    evidence = []
    for index, budget in enumerate(DEVELOPMENT_BUDGETS):
        path = project / f"results/dev_{index}.json"
        write_manifest(
            path,
            {
                "alert_mode": "hierarchical_probability",
                "suites": ["cicids2017"],
                "scenario_count": 14,
                "observed_seeds": [7],
                "validation_benign_fpr_budget": budget,
                "suite_equal_mean": {"alert_accuracy": 0.96},
                "aggregate_gates": {"basic_warning_95_5_gate": True},
            },
        )
        evidence.append(path)
    source = tmp_path / "source.csv"
    source.write_text("Label\nBenign\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text("{}", encoding="utf-8")

    protocol = create_protocol(
        project_root=project,
        core_protocol_path=core,
        candidate_manifest_path=candidate,
        source_csv_path=source,
        config_path=config,
        development_evidence_paths=evidence,
        run_root=project / "runs/formal",
        result_root=project / "results/formal",
        cache_root=project / "caches/formal",
        workers=24,
        model_jobs=8,
    )

    assert protocol["seeds"] == [907, 911, 919]
    assert protocol["expected_task_count"] == 42
    assert protocol["development_selection"][
        "selected_validation_benign_fpr_budget"
    ] == 0.04
    assert protocol["execution"]["workers"] == 24
    assert protocol["execution"]["resource_policy"][
        "preferred_cpu_utilization_fraction"
    ] == 0.8
    assert protocol["execution"]["resource_policy"][
        "declared_parallel_job_slots"
    ] == 192
    assert protocol["acceptance"][
        "all_three_fresh_seeds_must_pass_basic_warning_gate"
    ]
    assert protocol["anti_leakage"][
        "fresh_seed_test_metrics_used_for_selection"
    ] is False
