from __future__ import annotations

from pathlib import Path


def test_cicids2018_waits_behind_formal_admission_gate() -> None:
    project_root = Path(__file__).resolve().parents[1]
    script = (
        project_root / "scripts" / "supervise_caeos_feature_extraction_v5_four_lanes.sh"
    ).read_text(encoding="utf-8")

    assert "cicids2017 cicids2018 unsw_nb15 5gad_2022 cic_ton_iot" in script
    assert "dataset_is_admitted" in script
    assert 'item.get("status") == "ready"' in script
    assert "label_ready and source_ready and catalog_ready" in script
    assert 'dataset_is_admitted "${dataset_id}" || continue' in script


def test_all_supervised_datasets_are_accepted_by_additional_lane_launcher() -> None:
    project_root = Path(__file__).resolve().parents[1]
    supervisor = (
        project_root / "scripts" / "supervise_caeos_feature_extraction_v5_four_lanes.sh"
    ).read_text(encoding="utf-8")
    launcher = (
        project_root
        / "scripts"
        / "run_caeos_unified_feature_extraction_v5_additional_lane.sh"
    ).read_text(encoding="utf-8")

    queue = supervisor.split("queue=(", 1)[1].split(")", 1)[0].split()
    for dataset_id in queue:
        assert dataset_id in launcher


def test_bot_iot_is_supervised_with_its_frozen_preprocessor() -> None:
    project_root = Path(__file__).resolve().parents[1]
    supervisor = (
        project_root / "scripts" / "supervise_caeos_feature_extraction_v5_four_lanes.sh"
    ).read_text(encoding="utf-8")
    launcher = (
        project_root
        / "scripts"
        / "run_caeos_unified_feature_extraction_v5_additional_lane.sh"
    ).read_text(encoding="utf-8")

    queue = supervisor.split("queue=(", 1)[1].split(")", 1)[0].split()
    assert "cic_bot_iot" in queue
    assert "cic_bot_iot)" in launcher
    assert "ciciot2023)" in launcher
    assert launcher.count(
        "export CAEOS_PREPROCESSOR_VARIANT=frozen_87f_tcp_ns_fix"
    ) == 2


def test_ciciot2023_uses_28_piece_workers_without_parallel_original_pcaps() -> None:
    project_root = Path(__file__).resolve().parents[1]
    launcher = (
        project_root
        / "scripts"
        / "run_caeos_unified_feature_extraction_v5_additional_lane.sh"
    ).read_text(encoding="utf-8")

    assert 'if [[ "${dataset_id}" == ciciot2023 ]]' in launcher
    assert "target_piece_bytes=67108864" in launcher
    assert "split_threshold_bytes=134217728" in launcher
    assert "cpu_worker_cap=28" in launcher
    assert "estimated_worker_gib=1" in launcher
    assert '--cpu-worker-cap "${cpu_worker_cap}"' in launcher
