from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from audit_strict_v2_sota import build_audit, parse_expected_models, parse_seeds


def sha(tag: str) -> str:
    return hashlib.sha256(tag.encode("utf-8")).hexdigest()


def write_run(
    root: Path,
    suite: str,
    scenario: str,
    seed: int,
    model: str | None,
) -> None:
    suffix = f"_{model}" if model is not None else ""
    run = root / suite / f"{scenario}_seed{seed}{suffix}"
    run.mkdir(parents=True, exist_ok=True)
    metrics = {"seed": seed}
    if model is not None:
        metrics["model"] = model
    (run / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
    task: dict[str, object] = {
        "suite": suite,
        "scenario": scenario,
        "seed": seed,
    }
    if model is not None:
        task["model"] = model
    provenance = {
        "task": task,
        "inputs": {"csv": {"path": "cache.csv"}},
        "code": {"sha256": sha(f"code:{model}")},
        "parameter_fingerprint": sha(f"parameters:{suite}:{scenario}:{seed}:{model}"),
    }
    (run / "provenance.json").write_text(
        json.dumps(provenance), encoding="utf-8"
    )
    (run / "scores.npz").write_bytes(b"scores")
    if model is None:
        (run / "evidence_package.npz").write_bytes(b"evidence")


class StrictV2SotaAuditTests(unittest.TestCase):
    def test_complete_exact_matrix_passes_without_legacy_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = root / "gate"
            baseline = root / "baseline"
            scenarios = {"edge": {"attack": "Attack"}}
            for seed in (7, 11):
                write_run(gate, "edge", "attack", seed, None)
                for model in ("mlp", "palm"):
                    write_run(baseline, "edge", "attack", seed, model)
            report = build_audit(
                gate,
                {"modern": baseline},
                {"modern": ("mlp", "palm")},
                (7, 11),
                scenarios,
            )

        self.assertEqual(report["state"], "complete")
        self.assertEqual(report["expected_paired_tasks"], 2)
        self.assertEqual(report["baselines"]["modern"]["expected_runs"], 4)
        self.assertEqual(
            report["baselines"]["modern"]["manifest_status"],
            "legacy_compatible_missing",
        )

    def test_missing_task_is_incomplete_but_corrupt_artifact_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = root / "gate"
            baseline = root / "baseline"
            scenarios = {"edge": {"attack": "Attack"}}
            write_run(gate, "edge", "attack", 7, None)
            write_run(baseline, "edge", "attack", 7, "mlp")
            incomplete = build_audit(
                gate,
                {"modern": baseline},
                {"modern": ("mlp",)},
                (7, 11),
                scenarios,
            )
            self.assertEqual(incomplete["state"], "incomplete")

            (baseline / "edge" / "attack_seed7_mlp" / "scores.npz").unlink()
            invalid = build_audit(
                gate,
                {"modern": baseline},
                {"modern": ("mlp",)},
                (7, 11),
                scenarios,
            )

        self.assertEqual(invalid["state"], "invalid")
        self.assertTrue(invalid["baselines"]["modern"]["issues"])

    def test_complete_legacy_manifest_without_state_is_strictly_inferred(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = root / "gate"
            baseline = root / "baseline"
            scenarios = {"edge": {"attack": "Attack"}}
            write_run(gate, "edge", "attack", 7, None)
            write_run(baseline, "edge", "attack", 7, "mlp")
            manifest = {
                "number_of_experiments": 1,
                "completed": 1,
                "failed": 0,
                "skipped": 0,
                "runs": [{"status": "completed"}],
            }
            (baseline / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            report = build_audit(
                gate,
                {"modern": baseline},
                {"modern": ("mlp",)},
                (7,),
                scenarios,
            )

        item = report["baselines"]["modern"]
        self.assertEqual(report["state"], "complete")
        self.assertEqual(item["manifest_status"], "present_legacy_inferred_complete")
        self.assertEqual(item["manifest_state"], "legacy_inferred_complete")

    def test_ambiguous_legacy_manifest_without_state_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            gate = root / "gate"
            baseline = root / "baseline"
            scenarios = {"edge": {"attack": "Attack"}}
            write_run(gate, "edge", "attack", 7, None)
            write_run(baseline, "edge", "attack", 7, "mlp")
            manifest = {
                "number_of_experiments": 1,
                "completed": 1,
                "failed": 0,
                "skipped": 0,
                "runs": [{"status": "running"}],
            }
            (baseline / "manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            report = build_audit(
                gate,
                {"modern": baseline},
                {"modern": ("mlp",)},
                (7,),
                scenarios,
            )

        self.assertEqual(report["state"], "invalid")
        self.assertIsNone(report["baselines"]["modern"]["manifest_state"])

    def test_parsers_reject_ambiguous_protocol_inputs(self) -> None:
        self.assertEqual(parse_seeds("19,7,11"), (7, 11, 19))
        self.assertEqual(
            parse_expected_models(["modern=palm,mlp"]),
            {"modern": ("mlp", "palm")},
        )
        for value in ("", "7,", "7,7", "-1,7", "x"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    parse_seeds(value)


if __name__ == "__main__":
    unittest.main()
