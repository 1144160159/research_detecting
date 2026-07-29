from __future__ import annotations

import unittest
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from write_strict_v4_krc_terminal_handoff import (
    SCHEMA,
    build_handoff,
    validate_existing,
)


def decision(*, passes: bool) -> dict:
    value = {
        "schema_version": "strict_v4_krc_downstream_decision_v1",
        "decision_revision": (
            "integrity_effect_separated_negative_branch_v2"
        ),
        "krc_audit_integrity_passes": True,
        "krc_effect_gate_passes": passes,
        "selected_algorithm": (
            "krc_csr_caeos_v1" if passes else "caeos_pairwise"
        ),
        "downstream_execution_required": passes,
        "rrc_fallback_execution_permitted": not passes,
    }
    value["manifest_sha256"] = canonical_hash(value)
    return value


class KrcTerminalHandoffTest(unittest.TestCase):
    def test_positive_krc_defers_downstream_until_unified_selection(self):
        value = build_handoff(decision(passes=True), "a" * 64)
        self.assertEqual(value["schema_version"], SCHEMA)
        self.assertEqual(value["decision_action"], "rrc_not_required")
        self.assertFalse(value["rrc_confirmation_required"])
        self.assertFalse(value["legacy_krc_specific_downstream_started"])
        self.assertTrue(
            value["unified_selected_system_downstream_required"]
        )
        self.assertEqual(value["manifest_sha256"], canonical_hash(value))

    def test_negative_krc_hands_off_to_rrc_without_downstream(self):
        value = build_handoff(decision(passes=False), "b" * 64)
        self.assertEqual(value["decision_action"], "run_rrc")
        self.assertTrue(value["rrc_confirmation_required"])
        self.assertFalse(value["legacy_krc_specific_downstream_started"])

    def test_existing_handoff_is_immutable(self):
        source = decision(passes=True)
        value = build_handoff(source, "c" * 64)
        validate_existing(
            value,
            decision=source,
            decision_file_sha256="c" * 64,
        )
        value["decision_action"] = "run_rrc"
        with self.assertRaisesRegex(ValueError, "drifted"):
            validate_existing(
                value,
                decision=source,
                decision_file_sha256="c" * 64,
            )


if __name__ == "__main__":
    unittest.main()
