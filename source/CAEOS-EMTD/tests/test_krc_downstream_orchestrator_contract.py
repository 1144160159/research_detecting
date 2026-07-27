from pathlib import Path

from create_strict_v4_krc_parrot_safety_protocol import IMPLEMENTATION


def test_orchestrator_uses_actual_parrot_feature_completion_contract():
    project = Path(__file__).resolve().parents[1]
    script = (
        project / "scripts" / "wait_and_run_strict_v4_krc_downstream.sh"
    ).read_text(encoding="utf-8")
    assert "$FEATURE/full_feature_extraction_complete" in script
    assert "$FEATURE/feature_shard_manifest.json" in script
    assert '--feature-summary "$FEATURE/feature_shard_manifest.json"' in script
    assert "$FEATURE/summary.json" not in script


def test_parrot_watcher_is_decision_gated():
    project = Path(__file__).resolve().parents[1]
    script = (
        project
        / "scripts"
        / "wait_and_run_parrot2025_full_no_decryption_features.sh"
    ).read_text(encoding="utf-8")
    assert "DOWNSTREAM_DECISION=" in script
    assert "strict_v4_krc_integrated_comprehensive_sota_v2" in script
    assert 'value.get("downstream_execution_required") is True' in script
    assert "KRC negative; PARROT model-safety branch not required" in script


def test_orchestrator_uses_integrity_effect_separated_decision_v2():
    project = Path(__file__).resolve().parents[1]
    script = (
        project / "scripts" / "wait_and_run_strict_v4_krc_downstream.sh"
    ).read_text(encoding="utf-8")
    assert "strict_v4_krc_integrated_comprehensive_sota_v2" in script
    assert "finalize_strict_v4_krc_downstream_decision_v2.py" in script


def test_parrot_protocol_binds_preprocessing_and_runtime_dependency_closure():
    required = {
        "train_hybrid_open_set.py",
        "caeos/data.py",
        "caeos/krc_csr_runtime.py",
        "caeos/csr_runtime.py",
        "caeos/csr_exact_replay_runtime.py",
        "caeos/pairwise_runtime.py",
        "caeos/open_detect_runtime.py",
        "create_strict_v4_mdr_parrot_safety_protocol.py",
        "create_strict_v4_krc_selected_system_protocol.py",
    }
    assert required.issubset(IMPLEMENTATION)
