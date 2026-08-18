from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.audit_release_candidate import audit


ROOT = Path(__file__).resolve().parents[1]


class ReleaseCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.search = json.loads(
            (ROOT / "configs" / "algorithm_search_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        cls.release = json.loads(
            (ROOT / "configs" / "release_candidate_rc1.json").read_text(
                encoding="utf-8"
            )
        )

    def test_current_release_candidate_is_offline_qualified(self):
        result = audit(self.search, self.release)

        self.assertTrue(result["accepted"])
        self.assertEqual(result["algorithm_candidate_count"], 10)
        self.assertEqual(result["selected_candidate"], "A09")
        self.assertTrue(result["physical_live_gate_pending"])
        self.assertTrue(result["split_recovery_qualified"])
        self.assertFalse(result["final_pareto_eligible"])

    def test_failed_quality_gate_cannot_be_hidden(self):
        release = copy.deepcopy(self.release)
        release["frozen_non_live_gates"][
            "min_independent_attack_recall"
        ] = 0.99

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.gate.min_independent_attack_recall.failed",
            result["errors"],
        )

    def test_unbounded_or_too_small_search_is_rejected(self):
        search = copy.deepcopy(self.search)
        search["exploration_budget"]["minimum_candidates"] = 11

        result = audit(search, self.release)

        self.assertFalse(result["accepted"])
        self.assertIn("search.exploration_budget", result["errors"])

    def test_split_recovery_gate_is_directly_enforced(self):
        release = copy.deepcopy(self.release)
        release["observed_split_recovery_confirmation"][
            "recovery_to_success_s_max"
        ] = 0.5

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn("release.split_recovery.failed", result["errors"])

    def test_pending_live_preflight_cannot_be_reported_as_accepted(self):
        release = copy.deepcopy(self.release)
        release["observed_latest_physical_live_preflight"][
            "accepted"
        ] = True

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.latest_live_preflight.pending_marker",
            result["errors"],
        )

    def test_physical_p99_and_resources_are_hard_gates(self):
        release = copy.deepcopy(self.release)
        release["observed_physical_offline_confirmation"][
            "gpu_batch_p99_us_max"
        ] = 110000
        release["observed_physical_offline_confirmation"][
            "feature_enqueue_p99_us_max"
        ] = 6000
        release["observed_physical_offline_confirmation"][
            "python_host_cpu_fraction_upper"
        ] = 0.9

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.physical_offline.max_gpu_batch_p99_us.failed",
            result["errors"],
        )
        self.assertIn(
            "release.physical_offline.max_internal_feature_enqueue_p99_us.failed",
            result["errors"],
        )
        self.assertIn(
            "release.resource.cpu_utilization_max.failed",
            result["errors"],
        )

    def test_historical_runtime_failure_cannot_be_hidden(self):
        release = copy.deepcopy(self.release)
        release["observed_runtime_robust_selection"][
            "inference_batch_p99_us_max"
        ] = 130000

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.runtime_selection.inference_batch_p99_us_max.failed",
            result["errors"],
        )

    def test_virtual_diagnostic_cannot_enter_final_pareto(self):
        release = copy.deepcopy(self.release)
        release["observed_virtual_link_diagnostic"][
            "final_pareto_ingestion_allowed"
        ] = True

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.virtual_diagnostic.final_pareto_marker",
            result["errors"],
        )

    def test_temporary_management_shadow_cannot_enter_final_pareto(self):
        release = copy.deepcopy(self.release)
        release["observed_temporary_passive_shadow"][
            "final_pareto_ingestion_allowed"
        ] = True

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.temporary_shadow.final_pareto_marker",
            result["errors"],
        )

    def test_temporary_management_shadow_cannot_enable_replay(self):
        release = copy.deepcopy(self.release)
        release["observed_temporary_passive_shadow"][
            "traffic_generation_allowed"
        ] = True

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.temporary_shadow.traffic_generation",
            result["errors"],
        )

    def test_unqualified_native_xdp_claim_is_rejected(self):
        release = copy.deepcopy(self.release)
        release["capture_capability"][
            "xdp_native_driver_qualified"
        ] = True

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.capture_capability.xdp_native_driver_qualified",
            result["errors"],
        )

    def test_xdp_diagnostic_drop_and_final_claim_are_hard_failures(self):
        release = copy.deepcopy(self.release)
        release["observed_xdp_skb_diagnostic_stability"][
            "capture_packets_dropped_max"
        ] = 1
        release["observed_xdp_skb_diagnostic_stability"][
            "final_pareto_ingestion_allowed"
        ] = True

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn("release.xdp_skb.capture_drop", result["errors"])
        self.assertIn("release.xdp_skb.final_pareto_marker", result["errors"])

    def test_capture_fallback_cannot_reuse_normal_zero_drop_evidence(self):
        release = copy.deepcopy(self.release)
        release["observed_capture_driver_fallback_diagnostic"][
            "normal_path_zero_drop_evidence_reused"
        ] = True

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.capture_fallback.zero_drop_scope", result["errors"]
        )

    def test_direct_inference_resource_gate_is_enforced(self):
        release = copy.deepcopy(self.release)
        release["observed_split_inference_resource_confirmation"][
            "host_cpu_fraction_max"
        ] = 0.9

        result = audit(self.search, release)

        self.assertFalse(result["accepted"])
        self.assertIn(
            "release.resource_confirmation.host_cpu_fraction_max.failed",
            result["errors"],
        )
        self.assertIn(
            "release.resource_confirmation.host_cpu_fraction_max.mismatch",
            result["errors"],
        )

    def test_background_gpu_load_is_not_attributed_to_cpu_model(self):
        release = copy.deepcopy(self.release)
        release["observed_split_inference_resource_confirmation"][
            "system_gpu_utilization_fraction_background_max"
        ] = 1.0

        result = audit(self.search, release)

        self.assertTrue(result["accepted"])


if __name__ == "__main__":
    unittest.main()
