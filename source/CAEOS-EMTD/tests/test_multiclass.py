import unittest
import json
from pathlib import Path

import torch
import numpy as np
import pandas as pd

from caeos.data import (
    drop_cross_label_fingerprint_groups,
    make_synthetic_multiclass,
    stratified_column_group_split,
    stratified_fingerprint_group_split,
)
from caeos.multiclass import (
    build_multiclass_model,
    inject_symmetric_label_noise,
    model_probabilities,
    multiclass_report,
)
from caeos.hybrid import (
    ConflictAwareHybridClassifier,
    CorruptionRobustHybridClassifier,
    PairwiseSpecialistHybridClassifier,
    js_divergence,
    pairwise_js_conflict,
    probabilistic_or_conflict,
    temperature_scale,
)
from train_hybrid import compact_report, parse_max_features
from train_hybrid_open_set import safe_correlation
from evaluate_hybrid_structural_corruption import structural_corruption_cases
from audit_dataset_fingerprints import duplicate_summary
from caeos.hybrid_open_set import (
    ClassConditionalDiagonalDistance,
    ClassConditionalEmpiricalTailCalibrator,
    EmpiricalTailCalibrator,
    EmpiricalTwoSidedCalibrator,
    KnownKnnDistance,
    KnownLocalOutlierFactor,
    PredictedClassKnnDistance,
    KnownQuantileNormalizer,
    evaluate_hybrid_open_set,
    jensen_shannon_divergence,
    cauchy_combined_risk,
    bonferroni_union_risk,
)


class MulticlassBaselineTest(unittest.TestCase):
    def test_bonferroni_union_uses_strongest_calibrated_support_signal(self):
        risk = bonferroni_union_risk(
            {
                "distance": np.asarray([0.99, 0.10]),
                "knn_distance": np.asarray([0.20, 0.98]),
            },
            ("distance", "knn_distance"),
        )
        self.assertGreater(risk[0], 0.95)
        self.assertGreater(risk[1], 0.95)

    def test_knn_support_distance_increases_outside_known_cluster(self):
        model = KnownKnnDistance(neighbors=2)
        model.fit(np.asarray([[0.0], [0.1], [0.2], [0.3]]))
        risk = model.score(np.asarray([[0.15], [10.0]]))
        self.assertGreater(risk[1], risk[0] * 10.0)

    def test_class_knn_requires_support_from_claimed_class(self):
        model = PredictedClassKnnDistance(neighbors=2)
        model.fit(
            np.asarray([[0.0], [0.1], [10.0], [10.1]]),
            np.asarray([0, 0, 1, 1]),
        )
        values = np.asarray([[0.05], [0.05]])
        risk = model.score(values, np.asarray([0, 1]))
        self.assertGreater(risk[1], risk[0] * 10.0)

    def test_lof_density_flags_isolated_novel_sample(self):
        rng = np.random.RandomState(17)
        known = rng.normal(0.0, 0.1, size=(100, 2))
        model = KnownLocalOutlierFactor(neighbors=10, jobs=1)
        model.fit(known)
        risk = model.score(np.asarray([[0.0, 0.0], [5.0, 5.0]]))
        self.assertGreater(risk[1], risk[0] * 5.0)

    def test_two_sided_calibrator_flags_both_known_tail_directions(self):
        calibrator = EmpiricalTwoSidedCalibrator()
        calibrator.fit({"conflict": np.linspace(0.0, 1.0, 101)})
        risk = calibrator.transform(
            {"conflict": np.asarray([-1.0, 0.5, 2.0])}
        )["conflict"]
        self.assertGreater(risk[0], 0.95)
        self.assertLess(risk[1], 0.05)
        self.assertGreater(risk[2], 0.95)

    def test_class_conditional_tail_normalizes_per_class_scale(self):
        calibrator = ClassConditionalEmpiricalTailCalibrator()
        calibrator.fit(
            {"distance": np.asarray([0.0, 0.5, 1.0, 100.0, 100.5, 101.0])},
            np.asarray([0, 0, 0, 1, 1, 1]),
        )
        risk = calibrator.transform(
            {"distance": np.asarray([0.9, 100.9])}, np.asarray([0, 1])
        )["distance"]
        self.assertAlmostEqual(float(risk[0]), float(risk[1]))

    def test_capture_group_split_has_no_overlap(self):
        rows = []
        for label in ("x", "y"):
            for group_index in range(10):
                for row_index in range(3):
                    rows.append(
                        {
                            "value": row_index,
                            "CaptureId": "%s-%d" % (label, group_index),
                            "Label": label,
                        }
                    )
        frame = pd.DataFrame(rows)
        train, validation, test, metadata = stratified_column_group_split(
            frame, "Label", "CaptureId", seed=7
        )
        self.assertEqual(len(train) + len(validation) + len(test), len(frame))
        self.assertEqual(
            metadata["group_overlap"],
            {"train_validation": 0, "train_test": 0, "validation_test": 0},
        )
        for split in (train, validation, test):
            self.assertEqual(set(split["Label"]), {"x", "y"})

    def test_fingerprint_group_split_has_no_overlap(self):
        frame = pd.DataFrame(
            {
                "a": [1, 1, 2, 3, 4, 5, 6, 7]
                + [11, 11, 12, 13, 14, 15, 16, 17],
                "b": list(range(8)) + list(range(10, 18)),
                "Label": ["x"] * 8 + ["y"] * 8,
            }
        )
        train, validation, test, metadata = stratified_fingerprint_group_split(
            frame, "Label", ["a", "b"], seed=7
        )
        self.assertEqual(len(train) + len(validation) + len(test), len(frame))
        self.assertEqual(
            metadata["fingerprint_overlap"],
            {"train_validation": 0, "train_test": 0, "validation_test": 0},
        )
        for split in (train, validation, test):
            self.assertEqual(set(split["Label"]), {"x", "y"})

    def test_duplicate_audit_detects_cross_label_fingerprint(self):
        frame = pd.DataFrame(
            {
                "a": [1, 1, 2],
                "b": [3, 3, 4],
                "Label": ["x", "y", "x"],
            }
        )
        report = duplicate_summary(frame, "Label", ["a", "b"])
        self.assertEqual(report["duplicate_rows"], 1)
        self.assertEqual(report["cross_label_groups"], 1)

    def test_cross_label_fingerprint_groups_are_removed_before_split(self):
        frame = pd.DataFrame(
            {
                "a": [1, 1, 2, 3],
                "b": [5, 5, 6, 7],
                "Label": ["x", "y", "x", "y"],
            }
        )
        filtered, report = drop_cross_label_fingerprint_groups(
            frame, "Label", ["a", "b"]
        )
        self.assertEqual(len(filtered), 2)
        self.assertEqual(report["conflicting_fingerprint_groups"], 1)
        self.assertEqual(report["removed_rows"], 2)
        self.assertEqual(set(filtered["a"]), {2, 3})

    def test_structural_corruption_protocol_has_expected_cases(self):
        first = np.ones((8, 4))
        second = np.ones((8, 6))
        cases = list(
            structural_corruption_cases(
                [first, second], ["tls_handshake", "packet_sequence"], 7
            )
        )
        self.assertEqual(len(cases), 18)
        self.assertEqual(cases[0][0], "clean")
        self.assertTrue(any(case[0] == "sequence_truncation" for case in cases))

    def test_corruption_robust_classifier_exposes_discounted_evidence(self):
        rng = np.random.RandomState(31)
        labels = np.arange(180) % 3
        first = rng.normal(labels[:, None], 0.5, size=(180, 4))
        second = rng.normal(labels[:, None] * 0.5, 0.5, size=(180, 3))
        model = CorruptionRobustHybridClassifier(
            estimators=10,
            seed=31,
            jobs=1,
            minimum_robust_gain=0.0,
            routing_conflict_mode="adaptive_missingness",
        )
        model.fit(
            [first[:120], second[:120]],
            labels[:120],
            [first[120:150], second[120:150]],
            labels[120:150],
        )
        output = model.predict_with_evidence([first[150:], second[150:]])
        self.assertEqual(output["local_conflict"].shape, (30, 2))
        self.assertEqual(output["global_view_conflict"].shape, (30,))
        self.assertEqual(output["missingness_score"].shape, (30,))
        self.assertEqual(output["robust_gate"].shape, (30,))
        self.assertTrue(
            np.allclose(output["final_probability"].sum(axis=1), 1.0)
        )
        missing_output = model.predict_with_evidence(
            [np.zeros_like(first[150:]), second[150:]]
        )
        self.assertGreater(
            float(missing_output["missingness_score"].mean()),
            float(output["missingness_score"].mean()),
        )

    def test_validation_minimax_safety_mode_is_recorded(self):
        rng = np.random.RandomState(41)
        labels = np.arange(150) % 3
        first = rng.normal(labels[:, None], 0.7, size=(150, 4))
        second = rng.normal(labels[:, None], 0.7, size=(150, 3))
        model = CorruptionRobustHybridClassifier(
            estimators=10,
            seed=41,
            jobs=1,
            minimum_robust_gain=0.0,
            safety_fallback_mode="validation_minimax",
        )
        model.fit(
            [first[:90], second[:90]],
            labels[:90],
            [first[90:120], second[90:120]],
            labels[90:120],
        )
        output = model.predict_with_evidence([first[120:], second[120:]])
        self.assertEqual(
            model.robust_validation_scores["safety_fallback_mode"],
            "validation_minimax",
        )
        self.assertIn("uniform_view_probability", output)
        self.assertTrue(np.allclose(output["final_probability"].sum(axis=1), 1.0))

    def test_local_max_routing_uses_strongest_local_conflict(self):
        model = CorruptionRobustHybridClassifier(
            estimators=10, seed=7, jobs=1, routing_conflict_mode="local_max"
        )
        local = np.asarray([[0.1, 0.8], [0.3, 0.2]])
        routed = model._routing_conflict(
            np.asarray([0.2, 0.2]),
            np.asarray([0.1, 0.1]),
            local_conflict=local,
        )
        self.assertTrue(np.allclose(routed, np.asarray([0.8, 0.3])))

    def test_calibrated_local_routing_uses_per_view_clean_reference(self):
        model = CorruptionRobustHybridClassifier(
            estimators=10,
            seed=7,
            jobs=1,
            routing_conflict_mode="calibrated_local",
        )
        model.view_local_conflict_thresholds = np.asarray([0.2, 0.6])
        model.view_local_conflict_widths = np.asarray([0.2, 0.1])
        local = np.asarray([[0.3, 0.6], [0.2, 0.65]])
        routed = model._routing_conflict(
            np.asarray([0.1, 0.1]),
            np.asarray([0.1, 0.1]),
            local_conflict=local,
        )
        self.assertTrue(np.allclose(routed, np.asarray([0.5, 0.5])))

    def test_trimmed_view_fusion_removes_most_conflicting_view(self):
        evidence = {
            "view_reliability": np.ones((1, 3)),
            "local_conflict": np.asarray([[0.1, 0.9, 0.2]]),
            "view_probability": np.asarray(
                [[[0.9, 0.1], [0.0, 1.0], [0.8, 0.2]]]
            ),
        }
        fused = CorruptionRobustHybridClassifier._discounted_view_probability(
            evidence, discount_scale=0.0, trim_count=1
        )
        self.assertTrue(np.allclose(fused, np.asarray([[0.85, 0.15]])))

    def test_global_view_conflict_detects_opinion_disagreement(self):
        left = np.asarray([[0.9, 0.1], [0.5, 0.5]])
        right = np.asarray([[0.1, 0.9], [0.5, 0.5]])
        conflict = js_divergence(left, right)
        self.assertGreater(float(conflict[0]), 0.5)
        self.assertAlmostEqual(float(conflict[1]), 0.0, places=7)

    def test_probabilistic_or_accumulates_moderate_conflicts(self):
        left = np.asarray([0.2, 0.0])
        right = np.asarray([0.3, 0.4])
        combined = probabilistic_or_conflict(left, right)
        self.assertAlmostEqual(float(combined[0]), 0.44, places=7)
        self.assertAlmostEqual(float(combined[1]), 0.4, places=7)

    def test_safe_correlation_handles_constant_component(self):
        self.assertEqual(
            safe_correlation(np.ones(4), np.asarray([0.0, 1.0, 2.0, 3.0])),
            0.0,
        )

    def test_hybrid_open_set_components_are_oriented_and_finite(self):
        left = np.asarray([[0.8, 0.2], [0.5, 0.5]])
        right = np.asarray([[0.8, 0.2], [0.1, 0.9]])
        divergence = jensen_shannon_divergence(left, right)
        self.assertAlmostEqual(float(divergence[0]), 0.0, places=7)
        self.assertGreater(float(divergence[1]), 0.0)

        values = np.asarray([[0.0, 0.0], [0.2, 0.1], [3.0, 3.0], [3.2, 2.9]])
        labels = np.asarray([0, 0, 1, 1])
        distance = ClassConditionalDiagonalDistance()
        distance.fit(values, labels)
        scores = distance.score(np.asarray([[0.1, 0.0], [8.0, 8.0]]))
        self.assertLess(float(scores[0]), float(scores[1]))

        normalizer = KnownQuantileNormalizer()
        normalizer.fit({"distance": scores})
        transformed = normalizer.transform({"distance": scores})["distance"]
        self.assertTrue(np.isfinite(transformed).all())

    def test_hybrid_open_set_report_rewards_separated_risk(self):
        labels = np.asarray([0, 1, -1, -1])
        unknown = np.asarray([False, False, True, True])
        prediction = np.asarray([0, 1, 0, 1])
        risk = np.asarray([0.1, 0.2, 0.8, 0.9])
        report = evaluate_hybrid_open_set(
            labels, unknown, prediction, risk, threshold=0.5
        )
        self.assertEqual(report["unknown_auroc"], 1.0)
        self.assertEqual(report["unknown_rejection_rate"], 1.0)

    def test_empirical_tail_and_cauchy_risk_use_known_reference(self):
        calibrator = EmpiricalTailCalibrator()
        calibrator.fit(
            {
                "uncertainty": np.asarray([0.1, 0.2, 0.3, 0.4]),
                "conflict": np.asarray([0.05, 0.1, 0.15, 0.2]),
            }
        )
        risk = calibrator.transform(
            {
                "uncertainty": np.asarray([0.15, 0.9]),
                "conflict": np.asarray([0.08, 0.8]),
            }
        )
        combined = cauchy_combined_risk(
            risk, ("uncertainty", "conflict")
        )
        self.assertLess(float(combined[0]), float(combined[1]))
        self.assertTrue(np.isfinite(combined).all())

    def test_temperature_scaling_preserves_argmax(self):
        probability = np.asarray([[0.7, 0.2, 0.1], [0.1, 0.4, 0.5]])
        calibrated = temperature_scale(probability, 1.7)
        self.assertTrue(np.array_equal(probability.argmax(1), calibrated.argmax(1)))
        self.assertTrue(np.allclose(calibrated.sum(axis=1), 1.0))

    def test_max_features_parser_preserves_named_modes(self):
        self.assertEqual(parse_max_features("sqrt"), "sqrt")
        self.assertEqual(parse_max_features("log2"), "log2")
        self.assertEqual(parse_max_features("0.5"), 0.5)

    def test_global_tree_seed_offsets_are_explicit(self):
        model = ConflictAwareHybridClassifier(
            estimators=10, seed=7, jobs=1, global_seed_offsets=(202, 606)
        )
        self.assertEqual(model.random_forest.random_state, 209)
        self.assertEqual(model.extra_trees.random_state, 613)

    def test_pairwise_specialist_keeps_probability_normalized(self):
        rng = np.random.RandomState(13)
        labels = np.arange(180) % 3
        first = rng.normal(labels[:, None], 0.7, size=(180, 4))
        second = rng.normal(labels[:, None] * 0.5, 0.7, size=(180, 3))
        model = PairwiseSpecialistHybridClassifier(
            estimators=10,
            seed=13,
            jobs=1,
            max_specialists=2,
            minimum_pair_errors=1,
        )
        model.fit(
            [first[:120], second[:120]],
            labels[:120],
            [first[120:150], second[120:150]],
            labels[120:150],
        )
        output = model.predict_with_evidence(
            [first[150:], second[150:]]
        )
        self.assertEqual(output["final_probability"].shape, (30, 3))
        self.assertEqual(output["specialist_activation"].shape[0], 30)
        self.assertTrue(
            np.allclose(output["final_probability"].sum(axis=1), 1.0)
        )

    def test_compact_hybrid_report_maps_macro_f1_key(self):
        labels = torch.tensor([0, 0, 1, 1])
        probability = np.asarray(
            [[0.9, 0.1], [0.8, 0.2], [0.2, 0.8], [0.1, 0.9]]
        )
        report = compact_report(labels, probability, ["normal", "attack"])
        self.assertEqual(report["macro_f1"], 1.0)

    def test_hybrid_conflict_is_symmetric_and_zero_for_agreement(self):
        probability = np.asarray(
            [
                [[0.8, 0.2], [0.8, 0.2], [0.8, 0.2]],
                [[0.9, 0.1], [0.1, 0.9], [0.5, 0.5]],
            ],
            dtype=np.float64,
        )
        reliability = np.ones((2, 3), dtype=np.float64)
        pairwise, global_conflict = pairwise_js_conflict(probability, reliability)
        self.assertTrue(np.allclose(pairwise, pairwise.transpose(0, 2, 1)))
        self.assertAlmostEqual(float(global_conflict[0]), 0.0, places=7)
        self.assertGreater(float(global_conflict[1]), 0.0)

    def test_hybrid_classifier_outputs_auditable_evidence(self):
        rng = np.random.RandomState(3)
        labels = np.arange(120) % 3
        first = rng.normal(labels[:, None], 0.25, size=(120, 4))
        second = rng.normal(labels[:, None] * 0.5, 0.25, size=(120, 3))
        model = ConflictAwareHybridClassifier(estimators=10, seed=3, jobs=1)
        model.fit(
            [first[:90], second[:90]],
            labels[:90],
            [first[90:], second[90:]],
            labels[90:],
        )
        output = model.predict_with_evidence([first[90:], second[90:]])
        self.assertEqual(output["final_probability"].shape, (30, 3))
        self.assertEqual(output["view_evidence"].shape, (30, 2, 3))
        self.assertEqual(output["view_probability"].shape, (30, 2, 3))
        self.assertEqual(output["view_uncertainty"].shape, (30, 2))
        self.assertEqual(output["view_reliability"].shape, (30, 2))
        self.assertEqual(output["pairwise_conflict"].shape, (30, 2, 2))
        self.assertTrue(
            np.allclose(output["final_probability"].sum(axis=1), 1.0)
        )
        self.assertTrue((output["view_evidence"] >= 0.0).all())
        self.assertTrue((output["view_uncertainty"] >= 0.0).all())
        self.assertTrue((output["view_uncertainty"] <= 1.0).all())

    def test_mal_tls_config_covers_all_non_label_columns(self):
        config_path = Path(__file__).parents[1] / "configs" / "mal_tls2023.json"
        with config_path.open("r", encoding="utf-8") as handle:
            config = json.load(handle)
        columns = [
            column
            for values in config["modalities"].values()
            for column in values
        ]
        self.assertEqual(config["label_column"], "Label")
        self.assertEqual(len(columns), 117)
        self.assertEqual(len(columns), len(set(columns)))
        self.assertNotIn("Label", columns)
    def test_synthetic_closed_set_contains_no_unknown(self):
        bundle = make_synthetic_multiclass(samples_per_class=40, seed=3)
        self.assertFalse(bool(bundle.train.is_unknown.any()))
        self.assertFalse(bool(bundle.validation.is_unknown.any()))
        self.assertFalse(bool(bundle.test.is_unknown.any()))
        self.assertTrue(bool((bundle.test.labels >= 0).all()))

    def test_all_internal_models_produce_probabilities(self):
        views = [torch.randn(12, 8), torch.randn(12, 6), torch.randn(12, 4)]
        quality = torch.ones(12, 3)
        for name in ("mc0", "mc1", "mc2", "mc3", "mc4"):
            model = build_multiclass_model(
                name, [8, 6, 4], 5, hidden_dim=16, embedding_dim=12
            )
            output = model(views, quality)
            probability = model_probabilities(name, output)
            self.assertEqual(tuple(probability.shape), (12, 5))
            self.assertTrue(
                torch.allclose(probability.sum(dim=-1), torch.ones(12), atol=1e-5)
            )

    def test_fusion_modes_have_expected_discount(self):
        views = [torch.randn(10, 8), torch.randn(10, 6), torch.randn(10, 4)]
        quality = torch.ones(10, 3)
        sum_model = build_multiclass_model(
            "mc2", [8, 6, 4], 5, hidden_dim=16, embedding_dim=12
        )
        reliability_model = build_multiclass_model(
            "mc3", [8, 6, 4], 5, hidden_dim=16, embedding_dim=12
        )
        sum_output = sum_model(views, quality)
        reliability_output = reliability_model(views, quality)
        self.assertTrue(torch.allclose(sum_output["discount"], torch.ones(10, 3)))
        self.assertTrue(
            torch.allclose(
                reliability_output["discount"],
                reliability_output["reliability"],
                atol=1e-6,
            )
        )

    def test_symmetric_noise_never_keeps_selected_label(self):
        labels = torch.arange(200) % 5
        noisy = inject_symmetric_label_noise(labels, 5, rate=0.5, seed=11)
        changed = labels != noisy
        self.assertGreater(int(changed.sum()), 70)
        self.assertLess(int(changed.sum()), 130)
        self.assertTrue(bool(((noisy >= 0) & (noisy < 5)).all()))

    def test_report_contains_paper_and_long_tail_metrics(self):
        labels = torch.tensor([0, 0, 1, 1])
        probability = torch.tensor(
            [[0.9, 0.1], [0.8, 0.2], [0.2, 0.8], [0.1, 0.9]]
        )
        report = multiclass_report(labels, probability, ["Benign", "Attack"])
        self.assertEqual(report["f1_weighted"], 1.0)
        self.assertEqual(report["f1_macro"], 1.0)
        self.assertIn("classification_report", report)


if __name__ == "__main__":
    unittest.main()
