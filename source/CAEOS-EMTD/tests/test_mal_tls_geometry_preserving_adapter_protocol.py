import json
import tempfile
import unittest
from pathlib import Path

import torch

from analyze_mal_tls_geometry_preserving_adapter import analyze
from create_mal_tls_geometry_preserving_adapter_protocol import create_protocol
from verify_geometry_preserving_adapter_checkpoints import verify


class GeometryPreservingAdapterProtocolTests(unittest.TestCase):
    def protocol(self):
        return create_protocol(
            dataset_sha256="a" * 64,
            implementation_sha256={"train.py": "b" * 64},
            observed_metrics=0,
        )

    def test_protocol_freezes_disjoint_seed_and_geometry_invariants(self) -> None:
        protocol = self.protocol()
        self.assertEqual(protocol["training"]["development_seed"], 195)
        self.assertEqual(protocol["metrics_observed_at_freeze"], 0)
        self.assertEqual(
            protocol["paired_methods"]["candidate_trainable_scope"],
            "evidence_adapters_only",
        )
        self.assertIn(
            "normal_distance_auroc",
            protocol["hard_invariants"]["invariant_metrics"],
        )

    def test_checkpoint_audit_rejects_any_base_change(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reference = root / "reference.pt"
            candidate = root / "candidate.pt"
            torch.save({"model_state": {"base": torch.tensor([1.0])}}, reference)
            torch.save(
                {
                    "model_state": {
                        "base": torch.tensor([1.0]),
                        "evidence_adapters.0.head.weight": torch.tensor([0.2]),
                    },
                    "arguments": {
                        "encoder_profile": "mal_tls_geometry_preserving_adapter",
                        "freeze_base_for_adapter": True,
                        "consistency_weight": 1.0,
                    },
                },
                candidate,
            )
            self.assertTrue(verify(reference, candidate)["passes"])
            payload = torch.load(candidate)
            payload["model_state"]["base"] = torch.tensor([2.0])
            torch.save(payload, candidate)
            self.assertFalse(verify(reference, candidate)["passes"])

    def test_analyzer_requires_geometry_and_open_set_gates(self) -> None:
        protocol = self.protocol()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            seed = protocol["training"]["development_seed"]
            invariants = protocol["hard_invariants"]["invariant_metrics"]
            for scenario in protocol["dataset"]["scenarios"]:
                for role in ("reference", "candidate"):
                    method = protocol["paired_methods"][role]
                    run = root / method["encoder_profile"] / f"{scenario}_seed{seed}"
                    run.mkdir(parents=True)
                    gain = 0.01 if role == "candidate" else 0.0
                    metrics = {
                        "encoder_profile": method["encoder_profile"],
                        "encoder_kinds": method["encoder_kinds"],
                        "evidence_adapter_kinds": method["evidence_adapter_kinds"],
                        "evidence_temperature_calibration": True,
                        "known_macro_f1": 0.8 + gain,
                        "ece": 0.1 - gain,
                        "unknown_auroc": 0.8 + gain,
                        "unknown_aupr": 0.7 + gain,
                        "unknown_fpr95": 0.3 - gain,
                        "oscr": 0.6 + gain,
                    }
                    metrics.update({name: 0.75 for name in invariants})
                    metadata = {
                        "split_metadata": {
                            "split_fingerprint": {"combined": scenario + "-fp"}
                        }
                    }
                    (run / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
                    (run / "data_metadata.json").write_text(
                        json.dumps(metadata), encoding="utf-8"
                    )
                    if role == "candidate":
                        (run / "base_equivalence.json").write_text(
                            json.dumps({"passes": True}), encoding="utf-8"
                        )
            result = analyze(protocol, root)
            self.assertTrue(result["passes"])
            self.assertTrue(result["checks"]["all_geometry_invariants_pass"])


if __name__ == "__main__":
    unittest.main()
