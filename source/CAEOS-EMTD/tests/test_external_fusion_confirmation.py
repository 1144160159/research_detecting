from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from confirm_external_fusion_candidate import build_confirmation


def report(value: float) -> dict[str, float]:
    return {
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
        "known_macro_f1": 0.9,
    }


class ExternalFusionConfirmationTest(unittest.TestCase):
    def write_inputs(self, root: Path) -> tuple[Path, Path]:
        selection = {
            "candidate_status": "frozen_unconfirmed",
            "development_seeds": [7],
            "confirmation_seeds": [29, 31],
            "selected_candidate": {
                "expert_name": "relative_mahalanobis",
                "expert_model": "mlp",
                "fusion": "rank_cauchy",
                "base_risk": "cauchy_modality_support_union",
            },
        }
        runs = []
        for scenario_index in range(14):
            for seed in (29, 31):
                runs.append(
                    {
                        "task": f"attack_{scenario_index}_seed{seed}",
                        "gate_report": report(0.6),
                        "reports": {"rank_cauchy": report(0.7)},
                    }
                )
        raw = {
            "selection_scope": {"seeds": [29, 31], "suites": ["edge_iiot"]},
            "overall": {
                "expert_name": "relative_mahalanobis",
                "methods": {"rank_cauchy": {}},
            },
            "runs": runs,
        }
        selection_path = root / "selection.json"
        raw_path = root / "raw.json"
        selection_path.write_text(json.dumps(selection), encoding="utf-8")
        raw_path.write_text(json.dumps(raw), encoding="utf-8")
        return selection_path, raw_path

    def test_complete_positive_confirmation_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            selection, raw = self.write_inputs(Path(directory))
            result = build_confirmation(selection, raw, 100, 17)
            self.assertTrue(result["decision"]["confirmation_passes"])
            self.assertEqual(result["scenario_count"], 14)
            self.assertEqual(result["run_count"], 28)
            self.assertGreater(
                result["metrics"]["unknown_auroc"]["bootstrap_95_ci"]["lower"],
                0.0,
            )

    def test_unreserved_seed_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            selection, raw = self.write_inputs(Path(directory))
            payload = json.loads(raw.read_text(encoding="utf-8"))
            payload["selection_scope"]["seeds"] = [29, 37]
            raw.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "seed mismatch"):
                build_confirmation(selection, raw, 100, 17)


if __name__ == "__main__":
    unittest.main()
