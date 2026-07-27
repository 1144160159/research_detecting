from __future__ import annotations

import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_unified_self_algorithm_selection_protocol import create_protocol
from select_strict_v4_unified_self_algorithm import CTC, PAIRWISE, select_unified


def canonical(schema, **items):
    payload = {"schema_version": schema, **items}
    payload["manifest_sha256"] = canonical_hash(payload)
    return payload


class StrictV4UnifiedSelfAlgorithmSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pairwise = canonical("strict_v4_boundary_pairwise_candidate_v1")
        self.mal_protocol = canonical("mal_tls_self_algorithm_selection_protocol_v2")
        self.ctc_protocol = canonical(
            "strict_v4_conflict_topology_copula_protocol_v1",
            metrics_observed_at_freeze=0,
        )
        self.protocol = create_protocol(
            pairwise_manifest=self.pairwise,
            mal_tls_selection_protocol=self.mal_protocol,
            ctc_pilot_protocol=self.ctc_protocol,
            input_file_sha256={},
            implementation_sha256={},
            observed_decisions=0,
        )
        self.mal_audit = canonical(
            "mal_tls_self_algorithm_selection_audit_v1",
            protocol_manifest_sha256=self.mal_protocol["manifest_sha256"],
            selected_mal_tls_component="mal_tls_geometry_preserving_adapter",
        )

    def test_protocol_refuses_post_result_freeze(self) -> None:
        with self.assertRaisesRegex(ValueError, "before decisions"):
            create_protocol(
                pairwise_manifest=self.pairwise,
                mal_tls_selection_protocol=self.mal_protocol,
                ctc_pilot_protocol=self.ctc_protocol,
                input_file_sha256={},
                implementation_sha256={},
                observed_decisions=1,
            )

    def test_negative_ctc_retains_pairwise_and_inherits_component(self) -> None:
        pilot = {
            "schema_version": "strict_v4_conflict_topology_copula_analysis_v1",
            "protocol_manifest_sha256": self.ctc_protocol["manifest_sha256"],
            "passes": False,
            "decision": "retain_pairwise",
        }
        result = select_unified(
            protocol=self.protocol,
            pairwise_manifest=self.pairwise,
            mal_tls_audit=self.mal_audit,
            ctc_pilot=pilot,
            ctc_branch_complete=True,
            ctc_not_required={"pilot_decision": "retain_pairwise"},
            ctc_confirmation_protocol=None,
            ctc_confirmation=None,
        )
        self.assertEqual(result["selected_global_accuracy_algorithm"], PAIRWISE)
        self.assertEqual(
            result["selected_mal_tls_component"],
            "mal_tls_geometry_preserving_adapter",
        )
        self.assertFalse(result["deployment_selection_complete"])

    def test_positive_reserved_confirmation_selects_ctc_accuracy_only(self) -> None:
        pilot = {
            "schema_version": "strict_v4_conflict_topology_copula_analysis_v1",
            "protocol_manifest_sha256": self.ctc_protocol["manifest_sha256"],
            "passes": True,
            "decision": "freeze_for_reserved_seed_confirmation",
        }
        confirmation_protocol = canonical(
            "strict_v4_conflict_topology_copula_confirmation_protocol_v1",
            pilot_protocol_manifest_sha256=self.ctc_protocol["manifest_sha256"],
        )
        confirmation = {
            "schema_version": "strict_v4_conflict_topology_copula_confirmation_v1",
            "protocol_manifest_sha256": confirmation_protocol["manifest_sha256"],
            "passes": True,
        }
        result = select_unified(
            protocol=self.protocol,
            pairwise_manifest=self.pairwise,
            mal_tls_audit=self.mal_audit,
            ctc_pilot=pilot,
            ctc_branch_complete=True,
            ctc_not_required=None,
            ctc_confirmation_protocol=confirmation_protocol,
            ctc_confirmation=confirmation,
        )
        self.assertEqual(result["selected_global_accuracy_algorithm"], CTC)
        self.assertEqual(
            result["deployment_status"],
            "pending_ctc_efficiency_and_external_dataset_gates",
        )
        self.assertFalse(result["deployment_selection_complete"])
        self.assertEqual(result["manifest_sha256"], canonical_hash(result))

    def test_positive_pilot_without_confirmation_fails_closed(self) -> None:
        pilot = {
            "schema_version": "strict_v4_conflict_topology_copula_analysis_v1",
            "protocol_manifest_sha256": self.ctc_protocol["manifest_sha256"],
            "passes": True,
            "decision": "freeze_for_reserved_seed_confirmation",
        }
        with self.assertRaisesRegex(ValueError, "lacks reserved-seed"):
            select_unified(
                protocol=self.protocol,
                pairwise_manifest=self.pairwise,
                mal_tls_audit=self.mal_audit,
                ctc_pilot=pilot,
                ctc_branch_complete=True,
                ctc_not_required=None,
                ctc_confirmation_protocol=None,
                ctc_confirmation=None,
            )


if __name__ == "__main__":
    unittest.main()
