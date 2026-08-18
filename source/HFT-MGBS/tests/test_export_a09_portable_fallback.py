import ast
import hashlib
import importlib.util
from pathlib import Path

import numpy as np
import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "export_a09_portable_fallback.py"
SPEC = importlib.util.spec_from_file_location("a09_portable_export", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeTree:
    def __init__(self):
        self.node_count = 3


class FakeEstimator:
    def __init__(self):
        self.tree_ = FakeTree()


class FakeModel:
    def __init__(self):
        self.classes_ = np.asarray([0, 1])
        self.estimators_ = [FakeEstimator() for _ in range(200)]


class FakeVectorizer:
    feature_names_ = np.asarray(MODULE.EXPECTED_FEATURE_NAMES)


class FakeForest:
    tree_count = 200

    def __init__(self):
        shape = (200, 3)
        self.children_left = np.tile(np.asarray([1, -1, -1]), (200, 1))
        self.children_right = np.tile(np.asarray([2, -1, -1]), (200, 1))
        self.feature = np.tile(np.asarray([31, -2, -2]), (200, 1))
        self.threshold = np.tile(np.asarray([6.0, np.nan, np.nan]), (200, 1))
        self.positive_probability = np.tile(np.asarray([np.nan, 0.25, 0.75]), (200, 1))


def bundle():
    return {
        "schema_version": 1,
        "candidate_id": "A09",
        "classifier": "extra_trees",
        "feature_profile": "invariant_no_ports_v1",
        "vectorizer": FakeVectorizer(),
        "models": [FakeModel(), FakeModel(), FakeModel()],
        "positive_indices": [1, 1, 1],
        "thresholds": [0.3, 0.4, 0.5],
        "metadata": {"seeds": [7, 11, 19], "estimators_per_seed": 200},
    }


def test_exporter_source_has_no_training_call():
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert "fit" not in called
    assert "set_params" not in called


def test_build_is_deterministic_and_binds_all_roots(monkeypatch):
    monkeypatch.setattr(
        MODULE, "A09NumpyExactPredictor",
        lambda models, positive_indices: type("P", (), {"feature_count": 34, "_forests": [FakeForest()] * 3})(),
    )
    roots = ("11" * 32, "22" * 32, "33" * 32)
    first = MODULE.build_artifact(bundle(), *roots)
    second = MODULE.build_artifact(bundle(), *roots)
    assert first == second
    assert first.startswith(MODULE.MAGIC)
    assert bytes.fromhex(roots[0]) in first
    assert hashlib.sha256(first).hexdigest() == hashlib.sha256(second).hexdigest()


def test_wrong_release_contract_fails_closed(monkeypatch):
    value = bundle()
    value["metadata"]["seeds"] = [1, 2, 3]
    with pytest.raises(ValueError, match="seed/tree"):
        MODULE.build_artifact(value, "11" * 32, "22" * 32, "33" * 32)


def test_source_hash_mismatch_fails_before_load(tmp_path, monkeypatch):
    model = tmp_path / "model"
    engine = tmp_path / "engine"
    campaign = tmp_path / "campaign"
    for path in (model, engine, campaign):
        path.write_bytes(path.name.encode())
    monkeypatch.setattr(MODULE.joblib, "load", lambda path: pytest.fail("load must not run"))
    with pytest.raises(ValueError, match="model SHA-256 mismatch"):
        MODULE.export(model, engine, campaign, tmp_path / "out", "00" * 32, MODULE.sha256(engine), MODULE.sha256(campaign))


def test_output_is_create_only(tmp_path):
    output = tmp_path / "artifact.bin"
    output.write_bytes(b"sealed")
    with pytest.raises(FileExistsError, match="already exists"):
        MODULE._create_only_bytes(output, b"replacement")
    assert output.read_bytes() == b"sealed"


def test_output_parent_must_already_exist(tmp_path):
    with pytest.raises(ValueError, match="existing canonical directory"):
        MODULE._create_only_bytes(tmp_path / "missing" / "artifact.bin", b"payload")
