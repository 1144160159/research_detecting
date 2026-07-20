from __future__ import annotations

import unittest

from select_strict_v4_final_algorithm import (
    REQUIRED_CHECKS,
    select_final_algorithm,
)


def inputs(passes: bool = True) -> tuple[dict, dict, dict]:
    router = {
        "schema_version": "strict_v4_domain_safe_router_candidate_v1",
        "manifest_sha256": "router-hash",
        "fallback": "caeos_pairwise",
    }
    protocol = {
        "schema_version": "strict_v4_domain_safe_router_confirmation_protocol_v1",
        "manifest_sha256": "protocol-hash",
        "router_manifest_sha256": "router-hash",
        "confirmation_seeds": [137, 139, 149],
    }
    checks = {name: True for name in REQUIRED_CHECKS}
    if not passes:
        checks["aupr_bootstrap_lower_strictly_positive"] = False
    confirmation = {
        "schema_version": "strict_v4_domain_safe_router_confirmation_v1",
        "router_manifest_sha256": "router-hash",
        "protocol_manifest_sha256": "protocol-hash",
        "validation": {
            "passes": True,
            "task_set_complete": True,
            "seeds": [137, 139, 149],
            "unknown_or_test_labels_used_for_confirmation_selection": False,
        },
        "decision": {"passes": passes, "checks": checks},
    }
    return router, protocol, confirmation


class StrictV4FinalAlgorithmSelectionTests(unittest.TestCase):
    def test_pass_selects_frozen_router(self) -> None:
        result = select_final_algorithm(*inputs(True))
        self.assertEqual(result["selected_algorithm"], "caeos_domain_safe_router")
        self.assertEqual(result["status"], "frozen_final_self_algorithm")

    def test_failed_gate_selects_pairwise_and_next_generation(self) -> None:
        result = select_final_algorithm(*inputs(False))
        self.assertEqual(result["selected_algorithm"], "caeos_pairwise")
        self.assertIn("next_generation", result["status"])
        self.assertIn("suite_conditioned", result["next_action"])

    def test_inconsistent_decision_fails_closed(self) -> None:
        router, protocol, confirmation = inputs(True)
        confirmation["decision"]["passes"] = False
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            select_final_algorithm(router, protocol, confirmation)

    def test_binding_and_validation_are_required(self) -> None:
        router, protocol, confirmation = inputs(True)
        confirmation["router_manifest_sha256"] = "other"
        with self.assertRaisesRegex(ValueError, "binding"):
            select_final_algorithm(router, protocol, confirmation)
        router, protocol, confirmation = inputs(True)
        confirmation["validation"]["task_set_complete"] = False
        with self.assertRaisesRegex(ValueError, "incomplete or unsafe"):
            select_final_algorithm(router, protocol, confirmation)


if __name__ == "__main__":
    unittest.main()
