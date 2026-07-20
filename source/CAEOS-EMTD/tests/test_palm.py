import unittest
from argparse import Namespace

import numpy as np
import torch

from caeos.palm import (
    PALMClassifier,
    PALMObjective,
    PALMSSDMahalanobis,
    balanced_sinkhorn_assignments,
)
from run_neural_baseline_matrix import build_experiments, command_for


class PALMTests(unittest.TestCase):
    def test_sinkhorn_assignments_satisfy_equipartition_constraints(self):
        torch.manual_seed(3)
        features = torch.randn(12, 5)
        prototypes = torch.randn(6, 5)

        assignments = balanced_sinkhorn_assignments(
            features, prototypes, epsilon=0.2, iterations=20
        )

        self.assertEqual(tuple(assignments.shape), (12, 6))
        self.assertTrue(torch.isfinite(assignments).all())
        torch.testing.assert_close(assignments.sum(dim=1), torch.ones(12))
        torch.testing.assert_close(
            assignments.sum(dim=0), torch.full((6,), 2.0), atol=5e-4, rtol=5e-4
        )

    def test_label_mask_and_top_k_only_select_same_class_prototypes(self):
        objective = PALMObjective(
            num_classes=3,
            embedding_dim=4,
            prototypes_per_class=4,
            assignment_top_k=2,
        )
        assignments = torch.full((3, 12), 1.0 / 12.0)
        labels = torch.tensor([0, 1, 2])

        weights = objective.class_assignment_weights(assignments, labels)

        torch.testing.assert_close(weights.sum(dim=1), torch.ones(3))
        self.assertTrue((weights > 0).sum(dim=1).eq(2).all())
        selected_labels = objective.prototype_labels.expand(3, -1)[weights > 0]
        self.assertEqual(selected_labels.tolist(), [0, 0, 1, 1, 2, 2])

    def test_frozen_top_k_mask_is_reused_after_assignment_changes(self):
        objective = PALMObjective(
            num_classes=2,
            embedding_dim=2,
            prototypes_per_class=3,
            assignment_top_k=1,
        )
        labels = torch.tensor([0])
        before = torch.tensor([[0.8, 0.1, 0.1, 0.0, 0.0, 0.0]])
        selected = objective.class_assignment_mask(before, labels)
        after = torch.tensor([[0.1, 0.8, 0.1, 0.0, 0.0, 0.0]])

        frozen = objective.class_assignment_weights(after, labels, selected)
        refreshed = objective.class_assignment_weights(after, labels)

        self.assertEqual(int(frozen.argmax(dim=1).item()), 0)
        self.assertEqual(int(refreshed.argmax(dim=1).item()), 1)

    def test_objective_updates_unit_prototypes_and_backpropagates(self):
        torch.manual_seed(5)
        objective = PALMObjective(
            num_classes=3,
            embedding_dim=6,
            prototypes_per_class=3,
            assignment_top_k=2,
            prototype_momentum=0.9,
        )
        features = torch.randn(9, 2, 6, requires_grad=True)
        labels = torch.arange(9) % 3
        before = objective.prototypes.clone()

        loss = objective(features, labels)
        loss.backward()

        self.assertTrue(torch.isfinite(loss))
        self.assertTrue(torch.isfinite(features.grad).all())
        self.assertGreater(float(features.grad.abs().sum()), 0.0)
        self.assertFalse(torch.equal(before, objective.prototypes))
        torch.testing.assert_close(
            objective.prototypes.norm(dim=1), torch.ones(9), atol=1e-5, rtol=1e-5
        )
        self.assertEqual(int(objective.update_count), 1)
        self.assertFalse(objective.prototypes.requires_grad)

    def test_classifier_exposes_normalized_embeddings_and_vmf_logits(self):
        torch.manual_seed(7)
        model = PALMClassifier(
            (4, 3),
            3,
            hidden_dim=12,
            embedding_dim=6,
            dropout=0.2,
            prototypes_per_class=3,
            assignment_top_k=2,
        )
        views = (torch.randn(8, 4), torch.randn(8, 3))
        labels = torch.arange(8) % 3

        model.train()
        output = model(views)
        loss = model.loss(output, labels)
        self.assertEqual(tuple(output["logits"].shape), (8, 3))
        self.assertEqual(tuple(output["embedding"].shape), (8, 6))
        self.assertEqual(tuple(output["palm_views"].shape), (8, 2, 6))
        torch.testing.assert_close(
            output["embedding"].norm(dim=1), torch.ones(8), atol=1e-5, rtol=1e-5
        )
        self.assertTrue(torch.isfinite(loss))

        model.eval()
        first = model(views)
        second = model(views)
        self.assertEqual(tuple(first["palm_views"].shape), (8, 1, 6))
        torch.testing.assert_close(first["embedding"], second["embedding"])

    def test_ssd_plus_matches_auditable_known_train_formula(self):
        train = np.asarray(
            [
                [1.0, 0.2, 0.1],
                [0.9, -0.1, 0.2],
                [0.8, 0.3, -0.2],
                [1.1, -0.2, -0.1],
            ]
        )
        query = np.asarray([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        calibrator = PALMSSDMahalanobis(official_centering=False)
        calibrator.fit(train)

        risk = calibrator.score(query)

        self.assertTrue(np.isfinite(risk).all())
        self.assertGreater(risk[1], risk[0])
        evidence = calibrator.evidence()
        self.assertEqual(evidence["fit_split"], "known_only_train")
        self.assertFalse(evidence["unknown_or_test_labels_used"])

    def test_evidence_identifies_protocol_and_tabular_adaptations(self):
        model = PALMClassifier((3,), 2, embedding_dim=4)
        evidence = model.evidence()

        self.assertEqual(evidence["fit_split"], "known_only_train")
        self.assertEqual(evidence["prototypes_per_class"], 6)
        self.assertEqual(evidence["assignment_top_k"], 5)
        self.assertFalse(evidence["unknown_or_test_labels_used"])
        self.assertIn(
            "image_resnet_replaced_by_shared_concat_view_tabular_mlp",
            evidence["adaptations"],
        )

    def test_matrix_freezes_official_palm_paper_runner_settings(self):
        args = Namespace(
            suite="hikari",
            scenarios="probing",
            models="palm",
            seeds="7",
            workers=1,
            epochs=0,
            patience=10,
            doh_max_per_class=20,
            mal_max_per_class=20,
            hikari_max_per_class=20,
            doh_csv="doh.csv",
            mal_csv="mal.csv",
            hikari_csv="hikari.csv",
            output_root="runs/test",
        )
        experiment = build_experiments(args)[0]
        command = command_for(experiment, args)

        expected = {
            "--epochs": "500",
            "--embedding-dim": "128",
            "--weight-decay": "1e-6",
            "--palm-training-views": "2",
            "--palm-prototypes-per-class": "6",
            "--palm-assignment-top-k": "5",
            "--palm-prototype-momentum": "0.999",
            "--palm-temperature": "0.1",
            "--palm-assignment-epsilon": "0.05",
            "--palm-sinkhorn-iterations": "3",
            "--palm-prototype-contrast-weight": "1",
            "--palm-learning-rate": "0.5",
            "--palm-momentum": "0.9",
            "--batch-size": "512",
        }
        for flag, value in expected.items():
            self.assertEqual(command[command.index(flag) + 1], value)


if __name__ == "__main__":
    unittest.main()
