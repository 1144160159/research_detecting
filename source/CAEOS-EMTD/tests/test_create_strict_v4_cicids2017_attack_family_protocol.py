from __future__ import annotations

import json
from pathlib import Path

from create_strict_v4_cicids2017_attack_family_protocol import build_protocol
from strict_v4_cicids2017_attack_family import canonical_hash


IMPLEMENTATIONS = (
    "strict_v4_cicids2017_attack_family.py",
    "create_strict_v4_cicids2017_attack_family_protocol.py",
    "run_strict_v4_cicids2017_attack_family_matrix.py",
    "launch_strict_v4_cicids2017_attack_family_matrix.py",
    "evaluate_strict_v4_cicids2017_attack_family_hybrid.py",
    "evaluate_strict_v4_hybrid_self_algorithm_development.py",
    "train_hybrid_open_set.py",
    "train_strict_v4_xgboost_warning_task.py",
)


def test_development_protocol_freezes_family_scope(tmp_path: Path) -> None:
    for name in IMPLEMENTATIONS:
        (tmp_path / name).write_text(name, encoding="utf-8")
    source = tmp_path / "source.csv"
    source.write_text("Label,Feature\nBenign,1\n", encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text("{}", encoding="utf-8")
    protocol = build_protocol(
        project_root=tmp_path,
        stage="development",
        source_csv=source,
        config_path=config,
        cache_root=tmp_path / "cache",
        run_root=tmp_path / "runs",
        result_root=tmp_path / "results",
    )
    declared = protocol.pop("manifest_sha256")
    assert canonical_hash(protocol) == declared
    assert protocol["seeds"] == [7]
    assert protocol["expected_task_count"] == 7
    assert protocol["claim_boundary"]["fine_subtype_claim_authorized"] is False
    assert protocol["resource_contract"]["declared_cpu_slots"] == 56
