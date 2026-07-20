import unittest

import numpy as np
import torch

from caeos.data import MultiViewFlowDataset
from caeos.neural_open_set import HCRPOSDClassifier
from caeos.nested_neural import (
    CandidateAggregate,
    RemappedSubset,
    aggregate_scores,
    pseudo_unknown_auroc,
    select_candidate,
)
from train_nested_neural_gate import resolve_gate_candidate
from run_nested_neural_gate_matrix import command_for
from argparse import Namespace


class NestedNeuralTests(unittest.TestCase):
    def test_hcrp_osd_adapter_fuses_1d_and_2d_convolution_before_arpl(self):
        model = HCRPOSDClassifier([5, 4], 3, hidden_dim=8, embedding_dim=6)
        output = model([torch.randn(4, 5), torch.randn(4, 4)])
        self.assertEqual(tuple(output["embedding"].shape), (4, 6))
        self.assertEqual(tuple(output["logits"].shape), (4, 3))
        loss = model.loss(output, torch.tensor([0, 1, 2, 1]))
        self.assertTrue(torch.isfinite(loss))
        loss.backward()
        self.assertIsNotNone(model.points.grad)

    def test_remapped_subset_marks_pseudo_unknown(self):
        dataset = MultiViewFlowDataset(
            [np.arange(12, dtype=np.float32).reshape(4, 3)],
            np.ones((4, 1), dtype=np.float32),
            np.asarray([0, 1, 2, 1]),
            np.zeros(4, dtype=bool),
        )
        subset = RemappedSubset(dataset, [0, 1, 2], {0: 0, 2: 1}, 1)
        self.assertEqual(subset.labels.tolist(), [0, -1, 1])
        self.assertTrue(bool(subset[1]["is_unknown"]))
        self.assertEqual(subset[2]["label"].item(), 1)

    def test_candidate_selection_requires_strict_neural_margin(self):
        aggregates = {
            "support_union": CandidateAggregate(0.80, 0.70, 0.75),
            "cauchy_evidence": CandidateAggregate(0.70, 0.60, 0.65),
            "neural_mahalanobis": CandidateAggregate(0.84, 0.72, 0.78),
        }
        self.assertEqual(
            select_candidate(aggregates, minimum_neural_gain=0.02)[0],
            "neural_mahalanobis",
        )
        self.assertEqual(
            select_candidate(aggregates, minimum_neural_gain=0.031)[0],
            "support_union",
        )

    def test_score_aggregation_and_pseudo_auroc(self):
        aggregate = aggregate_scores([0.8, 0.6])
        self.assertAlmostEqual(aggregate.mean_auroc, 0.7)
        self.assertAlmostEqual(aggregate.minimum_auroc, 0.6)
        labels = np.asarray([0, 1, 0, 1])
        risk = np.asarray([0.1, 0.8, 0.2, 0.9])
        self.assertEqual(pseudo_unknown_auroc(labels, risk, 1), 1.0)

    def test_contrastive_candidate_competes_with_complete_caeos_gate(self):
        aggregates = {
            "caeos_gate": CandidateAggregate(0.85, 0.75, 0.80),
            "closr": CandidateAggregate(0.90, 0.78, 0.84),
        }
        selected, _ = select_candidate(
            aggregates,
            neural_candidates=("closr",),
            minimum_neural_gain=0.02,
        )
        self.assertEqual(selected, "closr")

    def test_resolve_gate_candidate_uses_recorded_hierarchical_selection(self):
        report = {"unknown_auroc": 0.91}
        metrics = {
            "risk_selection_details": {
                "selected_risk": "anchor_support",
                "selected_report": report,
                "candidate_aggregates": {
                    "anchor_support": {
                        "mean_auroc": 0.88,
                        "minimum_auroc": 0.72,
                        "robust_objective": 0.80,
                    }
                },
            },
            "reports": {"anchor_support": report},
        }
        name, aggregate, selected_report = resolve_gate_candidate(metrics)
        self.assertEqual(name, "anchor_support")
        self.assertAlmostEqual(aggregate.robust_objective, 0.80)
        self.assertIs(selected_report, report)

    def test_open_detect_nested_matrix_uses_official_adaptation_settings(self):
        args = Namespace(
            output_root="runs/test",
            csv="hikari.csv",
            max_per_class=2000,
            epochs=100,
            patience=10,
            minimum_neural_gain=0.0,
            candidate_model="opendetect",
            gate_root="gate",
            neural_root="neural",
        )
        _, command = command_for("probing", "Probing", 7, args)
        self.assertEqual(command[command.index("--candidate-model") + 1], "opendetect")
        self.assertEqual(command[command.index("--hidden-dim") + 1], "256")
        self.assertEqual(command[command.index("--embedding-dim") + 1], "128")
        self.assertEqual(
            command[command.index("--open-detect-reset-epochs") + 1], "50,80"
        )


if __name__ == "__main__":
    unittest.main()
