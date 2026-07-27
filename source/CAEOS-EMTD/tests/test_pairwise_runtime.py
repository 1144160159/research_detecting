import unittest

import numpy as np

from benchmark_pairwise_runtime import batch_indices, percentile
from caeos.pairwise_runtime import (
    COMPONENT_TIE_TOLERANCE,
    PairwiseRuntime,
    SUPPORTED_RISKS,
    empirical_tail_cluster_starts,
    snap_to_reference_ties,
    stable_empirical_tail_scores,
)
from caeos.pseudo_unknown_gated_continuous import PUG_RISK_NAME


class PairwiseRuntimeTests(unittest.TestCase):
    def test_supported_risks_are_frozen_pairwise_endpoints(self) -> None:
        self.assertEqual(
            SUPPORTED_RISKS,
            {
                "cauchy_modality_support_union",
                "pseudo_unknown_learned_blend",
                PUG_RISK_NAME,
            },
        )

    def test_rejects_unsupported_risk(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported"):
            PairwiseRuntime(
                model=None,
                foss_model=None,
                distance_model=None,
                knn_model=None,
                view_knn_models=[],
                class_knn_model=None,
                lof_model=None,
                normalizer=None,
                tail_calibrator=None,
                selected_risk="test_label_router",
                learned_weights={},
                validation_raw_learned=np.asarray([0.1]),
                selected_alpha=0.0,
                foss_structural_view=False,
                foss_structural_view_mode="tree",
                foss_structural_view_scope="full",
            )

    def test_evidence_excludes_labels(self) -> None:
        runtime = PairwiseRuntime(
            model=None,
            foss_model=None,
            distance_model=None,
            knn_model=None,
            view_knn_models=[],
            class_knn_model=None,
            lof_model=None,
            normalizer=None,
            tail_calibrator=None,
            selected_risk="cauchy_modality_support_union",
            learned_weights={},
            validation_raw_learned=np.asarray([0.1, 0.2]),
            selected_alpha=0.0,
            foss_structural_view=False,
            foss_structural_view_mode="tree",
            foss_structural_view_scope="full",
        )
        evidence = runtime.evidence()
        self.assertFalse(evidence["contains_training_or_test_labels"])
        self.assertFalse(evidence["contains_test_ground_truth"])

    def test_batch_indices_wrap_deterministically(self) -> None:
        np.testing.assert_array_equal(batch_indices(5, 4, 0), [0, 1, 2, 3])
        np.testing.assert_array_equal(batch_indices(5, 4, 1), [4, 0, 1, 2])

    def test_percentile_is_finite(self) -> None:
        self.assertEqual(percentile([1.0, 2.0, 3.0], 50), 2.0)

    def test_empirical_tail_ties_are_stable_at_machine_precision(self) -> None:
        reference = np.asarray([0.1, 0.2, 0.2, 0.4])
        values = np.asarray([0.2 - 2e-16, 0.2 + 2e-16, 0.3])
        stabilized = snap_to_reference_ties(values, reference)
        np.testing.assert_array_equal(stabilized[:2], [0.2, 0.2])
        self.assertEqual(stabilized[2], 0.3)
        self.assertEqual(COMPONENT_TIE_TOLERANCE, 1e-12)

    def test_dense_reference_near_ties_share_one_empirical_rank(self) -> None:
        reference = np.asarray([0.1, 0.2 - 1e-16, 0.2 + 1e-16, 0.4])
        starts = empirical_tail_cluster_starts(reference)
        np.testing.assert_array_equal(starts, [0, 1, 3])
        below = stable_empirical_tail_scores(
            reference, np.asarray([0.2 - 2e-16]), starts
        )
        above = stable_empirical_tail_scores(
            reference, np.asarray([0.2 + 2e-16]), starts
        )
        np.testing.assert_array_equal(below, above)

    def test_runtime_predict_does_not_depend_on_component_method_locals(self) -> None:
        class IdentityTail:
            reference = {
                name: np.asarray([0.0, 0.5, 1.0])
                for name in (
                    "conflict",
                    "tree_disagreement",
                    "distance",
                    "knn_view_0",
                )
            }

            def transform(self, components):
                return components

        runtime = PairwiseRuntime(
            model=None,
            foss_model=None,
            distance_model=None,
            knn_model=None,
            view_knn_models=[],
            class_knn_model=None,
            lof_model=None,
            normalizer=IdentityTail(),
            tail_calibrator=IdentityTail(),
            selected_risk="cauchy_modality_support_union",
            learned_weights={},
            validation_raw_learned=np.asarray([]),
            selected_alpha=0.0,
            foss_structural_view=False,
            foss_structural_view_mode="tree",
            foss_structural_view_scope="full",
        )
        components = {
            name: np.asarray([0.2, 0.8]) for name in IdentityTail.reference
        }
        runtime.component_values = lambda raw_views: (
            components,
            np.asarray([[0.7, 0.3], [0.2, 0.8]]),
        )
        output = runtime.predict([])
        np.testing.assert_array_equal(output["prediction"], [0, 1])
        self.assertEqual(output["risk"].shape, (2,))

    def test_learned_tail_is_stable_across_machine_precision_noise(
        self,
    ) -> None:
        class IdentityCalibration:
            reference = {
                name: np.asarray([0.0, 0.2 - 1e-16, 0.2 + 1e-16, 1.0])
                for name in (
                    "conflict",
                    "tree_disagreement",
                    "distance",
                    "knn_view_0",
                )
            }

            def transform(self, components):
                return components

        runtime = PairwiseRuntime(
            model=None,
            foss_model=None,
            distance_model=None,
            knn_model=None,
            view_knn_models=[],
            class_knn_model=None,
            lof_model=None,
            normalizer=IdentityCalibration(),
            tail_calibrator=IdentityCalibration(),
            selected_risk="pseudo_unknown_learned_blend",
            learned_weights={"distance": 1.0},
            validation_raw_learned=np.asarray(
                [0.0, 0.2 - 1e-16, 0.2 + 1e-16, 1.0]
            ),
            selected_alpha=1.0,
            foss_structural_view=False,
            foss_structural_view_mode="tree",
            foss_structural_view_scope="full",
        )
        call_count = 0

        def component_values(_raw_views):
            nonlocal call_count
            perturbation = -2e-16 if call_count == 0 else 2e-16
            call_count += 1
            components = {
                name: np.asarray([0.2 + perturbation])
                for name in IdentityCalibration.reference
            }
            return components, np.asarray([[0.7, 0.3]])

        runtime.component_values = component_values
        first = runtime.predict([])
        second = runtime.predict([])
        np.testing.assert_array_equal(first["prediction"], second["prediction"])
        np.testing.assert_array_equal(first["risk"], second["risk"])

    def test_pug_runtime_uses_continuous_outer_min_p_endpoint(self) -> None:
        class Calibration:
            reference = {
                name: np.asarray([0.0, 0.25, 0.5, 0.75, 1.0])
                for name in (
                    "conflict",
                    "tree_disagreement",
                    "distance",
                    "knn_view_0",
                )
            }

            def transform(self, components):
                return components

        runtime = PairwiseRuntime(
            model=None,
            foss_model=None,
            distance_model=None,
            knn_model=None,
            view_knn_models=[],
            class_knn_model=None,
            lof_model=None,
            normalizer=Calibration(),
            tail_calibrator=Calibration(),
            selected_risk=PUG_RISK_NAME,
            learned_weights={},
            validation_raw_learned=np.asarray([]),
            selected_alpha=0.0,
            foss_structural_view=False,
            foss_structural_view_mode="tree",
            foss_structural_view_scope="full",
        )
        components = {
            "conflict": np.asarray([0.1, 0.8]),
            "tree_disagreement": np.asarray([0.2, 0.7]),
            "distance": np.asarray([0.3, 0.6]),
            "knn_view_0": np.asarray([0.4, 0.5]),
        }
        runtime.component_values = lambda _views: (
            components,
            np.asarray([[0.8, 0.2], [0.1, 0.9]]),
        )

        output = runtime.predict([])

        self.assertEqual(output["risk"].shape, (2,))
        self.assertTrue(np.isfinite(output["risk"]).all())
        self.assertTrue(((0.0 <= output["risk"]) & (output["risk"] <= 1.0)).all())
        evidence = runtime.evidence()
        self.assertEqual(evidence["selected_risk"], PUG_RISK_NAME)


if __name__ == "__main__":
    unittest.main()
