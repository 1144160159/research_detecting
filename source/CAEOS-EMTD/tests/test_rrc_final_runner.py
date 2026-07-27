from __future__ import annotations

import json
from pathlib import Path

import run_strict_v4_rrc_csr_confirmation as runner
from create_strict_v4_external_confirmation_protocol import canonical_hash


def canonical(value):
    value["manifest_sha256"] = canonical_hash(value)
    return value


def test_runner_preserves_complete_scientific_negative(
    tmp_path: Path, monkeypatch
):
    project_root = tmp_path / "project"
    run_root = tmp_path / "run"
    result_root = tmp_path / "result"
    project_root.mkdir()
    protocol_path = tmp_path / "protocol.json"
    protocol = {"resource_contract": {"outer_workers": 1}}
    protocol["manifest_sha256"] = canonical_hash(protocol)
    protocol_path.write_text(json.dumps(protocol), encoding="utf-8")
    pipeline = canonical(
        {
            "schema_version": (
                "strict_v4_rrc_csr_capture_pipeline_inventory_v1"
            ),
            "protocol_manifest_sha256": protocol["manifest_sha256"],
        }
    )

    def fake_pipeline(*args, **kwargs):
        result_root.mkdir(parents=True, exist_ok=True)
        (result_root / "capture_pipeline_inventory.json").write_text(
            json.dumps(pipeline, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return pipeline

    def fake_summary(*args, **kwargs):
        return canonical(
            {
                "schema_version": (
                    "strict_v4_rrc_csr_confirmation_summary_v1"
                ),
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "pipeline_inventory_manifest_sha256": pipeline[
                    "manifest_sha256"
                ],
                "passes": False,
                "selection": "caeos_pairwise",
            }
        )

    def fake_audit(protocol_value, summary_value, *args, **kwargs):
        return canonical(
            {
                "schema_version": (
                    "strict_v4_rrc_csr_confirmation_audit_v1"
                ),
                "protocol_manifest_sha256": protocol["manifest_sha256"],
                "pipeline_inventory_manifest_sha256": pipeline[
                    "manifest_sha256"
                ],
                "summary_manifest_sha256": summary_value[
                    "manifest_sha256"
                ],
                "integrity_passes": True,
                "effect_gate_passes": False,
                "passes": False,
                "selection": "caeos_pairwise",
            }
        )

    monkeypatch.setattr(runner, "validate_protocol", lambda value: None)
    monkeypatch.setattr(
        runner, "validate_implementation", lambda *args: None
    )
    monkeypatch.setattr(runner, "run_capture_pipeline", fake_pipeline)
    monkeypatch.setattr(runner, "summarize", fake_summary)
    monkeypatch.setattr(runner, "audit", fake_audit)
    value = runner.run(
        protocol,
        protocol_path,
        project_root,
        run_root,
        result_root,
        1,
    )
    assert value["integrity_passes"] is True
    assert value["effect_gate_passes"] is False
    assert value["selection"] == "caeos_pairwise"
    assert value["full_sota_established"] is False
    assert (result_root / "execution_complete.json").is_file()
