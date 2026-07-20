from __future__ import annotations

import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_tail_external_protocol import create_protocol


def manifest(schema: str, **values: object) -> dict:
    payload = {"schema_version": schema, **values}
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


class StrictV4TailExternalProtocolTests(unittest.TestCase):
    def test_freezes_fresh_external_seeds(self) -> None:
        coverage = manifest("strict_v4_coverage_manifest_v2")
        tail = manifest(
            "strict_v4_tail_aware_confirmation_protocol_v1",
            candidate={
                "risk_selection": "tail",
                "risk_endpoint": "tail_endpoint",
                "reference_endpoint": "reference",
                "maximum_alpha": 0.5,
                "runtime_minimum_fold_gain": -1.0,
                "hard_pseudo_fraction": 0.5,
                "boundary_interpolation": 0.5,
                "boundary_max_per_task": 512,
            },
        )
        tournament = manifest(
            "strict_v4_self_algorithm_tournament_protocol_v1",
            incumbent_branch={"confirmation_seeds": [137, 139, 149]},
            challenger_branch={"confirmation_seeds": [157, 163, 167]},
            coverage={
                "scenario_count": 102,
                "scenario_registry": {"suite": [f"attack_{i}" for i in range(102)]},
            },
            external_confirmation_branch={
                "tail_challenger_wins": {"fresh_seeds": [173, 179, 181]}
            },
        )
        external = manifest(
            "strict_v4_external_confirmation_protocol_v1",
            selected_comparator="opendetect",
        )
        protocol = create_protocol(
            coverage,
            tail,
            tournament,
            external,
            input_file_sha256={},
            implementation_sha256={},
        )
        self.assertEqual(protocol["seeds"], [173, 179, 181])
        self.assertEqual(protocol["expected_candidate_runs"], 306)
        self.assertEqual(protocol["manifest_sha256"], canonical_hash(protocol))


if __name__ == "__main__":
    unittest.main()
