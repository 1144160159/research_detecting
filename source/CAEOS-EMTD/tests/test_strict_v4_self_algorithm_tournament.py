from __future__ import annotations

import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from select_strict_v4_optimal_self_algorithm import select_optimal


def manifest(schema: str, **values: object) -> dict:
    payload = {"schema_version": schema, **values}
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


class StrictV4SelfAlgorithmTournamentTests(unittest.TestCase):
    def protocol(self) -> dict:
        return manifest(
            "strict_v4_self_algorithm_tournament_protocol_v1",
            challenger_branch={"tail_confirmation_protocol_sha256": "tail-protocol"},
            external_confirmation_branch={
                "incumbent_wins": {"seeds": [137, 139, 149]},
                "tail_challenger_wins": {"fresh_seeds": [173, 179, 181]},
            },
        )

    def incumbent(self) -> dict:
        return manifest(
            "strict_v4_final_algorithm_decision_v1",
            selected_algorithm="caeos_domain_safe_router",
        )

    def tail(self, passes: bool) -> dict:
        return {
            "schema_version": "strict_v4_tail_aware_confirmation_v1",
            "protocol_manifest_sha256": "tail-protocol",
            "decision": {"passes": passes},
        }

    def test_failed_tail_confirmation_retains_incumbent(self) -> None:
        result = select_optimal(self.protocol(), self.incumbent(), self.tail(False), None)
        self.assertEqual(result["selected_algorithm"], "caeos_domain_safe_router")
        self.assertEqual(result["external_confirmation_seeds"], [137, 139, 149])

    def test_tail_replaces_incumbent_only_after_paired_gate(self) -> None:
        head = {
            "schema_version": "strict_v4_tail_vs_incumbent_confirmation_v1",
            "protocol_manifest_sha256": self.protocol()["manifest_sha256"],
            "validation": {"incumbent_algorithm": "caeos_domain_safe_router"},
            "decision": {"passes": True},
        }
        result = select_optimal(self.protocol(), self.incumbent(), self.tail(True), head)
        self.assertEqual(result["selected_algorithm"], "caeos_tail_aware_pairwise")
        self.assertEqual(result["external_confirmation_seeds"], [173, 179, 181])


if __name__ == "__main__":
    unittest.main()
