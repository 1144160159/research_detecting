import json
from argparse import Namespace
from pathlib import Path
from types import SimpleNamespace

from strict_v4_cicids2017_attack_family import canonical_hash
from train_strict_v4_xgboost_warning_task_cuda import (
    parse_arguments,
    update_gpu_evidence,
)


def test_cuda_trainer_module_exposes_argument_parser() -> None:
    assert callable(parse_arguments)
    assert Path("model.ubj").suffix == ".ubj"
    assert Namespace is not None


def test_gpu_evidence_uses_live_trained_classifier(tmp_path: Path) -> None:
    metrics = {
        "schema_version": "test_metrics_v1",
        "model": {},
        "claim_boundary": {},
    }
    metrics["manifest_sha256"] = canonical_hash(metrics)
    provenance = {"schema_version": "test_provenance_v1"}
    provenance["manifest_sha256"] = canonical_hash(provenance)
    (tmp_path / "metrics.json").write_text(
        json.dumps(metrics), encoding="utf-8"
    )
    (tmp_path / "provenance.json").write_text(
        json.dumps(provenance), encoding="utf-8"
    )

    class FakeBooster:
        def save_config(self) -> str:
            return json.dumps({"learner": {"generic_parameter": {"device": "cuda:0"}}})

    class FakeClassifier:
        def get_booster(self) -> FakeBooster:
            return FakeBooster()

    xgboost_module = SimpleNamespace(
        __version__="2.1.4",
        build_info=lambda: {"USE_CUDA": True, "CUDA_VERSION": [12, 8]},
    )
    sampler = SimpleNamespace(
        samples=[
            {
                "utilization_percent": 91.0,
                "memory_used_mib": 654.0,
                "compute_processes": [{"pid": 1}],
            }
        ],
        errors=[],
    )
    updated = update_gpu_evidence(
        output_dir=tmp_path,
        xgboost_module=xgboost_module,
        trained_classifier=FakeClassifier(),
        sampler=sampler,
        initial_gpu={
            "index": 0,
            "name": "NVIDIA RTX A6000",
            "uuid": "GPU-test",
        },
    )
    evidence = json.loads(
        (tmp_path / "gpu_execution.json").read_text(encoding="utf-8")
    )
    assert evidence["passes"] is True
    assert evidence["booster_device_values"] == ["cuda:0"]
    assert updated["model"]["device"] == "cuda"
