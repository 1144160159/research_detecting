from __future__ import annotations

import unittest

from analyze_strict_v4_lcb_tail_aware_pilot_v2 import analyze
from create_strict_v4_lcb_analysis_correction import create_correction
from create_strict_v4_lcb_tail_aware_pilot_protocol import create_protocol
from tests.test_strict_v4_lcb_tail_aware_protocol import (
    row,
    source_protocol,
)


def deployed_row(suite: str, scenario: str) -> dict:
    value = row(suite, scenario)
    arguments = value["metrics"]["arguments"]
    policy = arguments.pop("risk_policy_name")
    arguments["risk_policy"] = policy
    value["metrics"]["risk_policy"] = policy
    candidate = {
        "--pseudo-unknown-max-alpha": "0.5",
        "--pseudo-unknown-min-fold-gain": "-0.05",
        "--boundary-hard-pseudo-fraction": "0.5",
        "--boundary-interpolation": "0.5",
        "--boundary-max-per-task": "512",
        "--tail-aware-confidence-z": "1.645",
        "--tail-aware-min-metric-lcb-gain": "0.0",
        "--tail-aware-min-aupr-lcb-gain": "0.0",
        "--tail-aware-min-aupr-fold-gain": "-0.05",
    }
    command = [
        "python",
        "train_hybrid_open_set.py",
        "--risk-selection",
        arguments["risk_selection"],
        "--risk-policy-name",
        policy,
        "--seed",
        "191",
    ]
    for flag, observed in candidate.items():
        command.extend((flag, observed))
    value["provenance"] = {
        "task": {"suite": suite, "scenario": scenario, "seed": 191},
        "command": command,
    }
    return value


class LcbAnalysisCorrectionTests(unittest.TestCase):
    def protocol(self) -> dict:
        protocol = create_protocol(
            source_protocol(),
            source_file_sha256="source",
            implementation_sha256={"implementation": "sha"},
        )
        protocol["implementation_sha256"] = {
            "analyze_strict_v4_lcb_tail_aware_pilot.py": "frozen"
        }
        from create_strict_v4_external_confirmation_protocol import canonical_hash

        protocol["manifest_sha256"] = canonical_hash(protocol)
        return protocol

    def rows(self, protocol: dict) -> list[dict]:
        return [
            deployed_row(suite, scenario)
            for suite, scenarios in protocol["pilot"]["scenarios"].items()
            for scenario in scenarios
        ]

    def test_adapter_accepts_deployed_policy_schema(self) -> None:
        protocol = self.protocol()
        result = analyze(protocol, self.rows(protocol))
        self.assertTrue(result["passes"])
        self.assertTrue(result["validation"]["deployed_risk_policy_schema_validated"])

    def test_adapter_rejects_top_level_policy_drift(self) -> None:
        protocol = self.protocol()
        rows = self.rows(protocol)
        rows[0]["metrics"]["risk_policy"] = "tampered"
        with self.assertRaisesRegex(ValueError, "top-level risk policy"):
            analyze(protocol, rows)

    def test_adapter_rejects_arguments_policy_drift(self) -> None:
        protocol = self.protocol()
        rows = self.rows(protocol)
        rows[0]["metrics"]["arguments"]["risk_policy"] = "tampered"
        with self.assertRaisesRegex(ValueError, "arguments risk policy"):
            analyze(protocol, rows)

    def test_adapter_rejects_provenance_parameter_drift(self) -> None:
        protocol = self.protocol()
        rows = self.rows(protocol)
        command = rows[0]["provenance"]["command"]
        command[command.index("--pseudo-unknown-max-alpha") + 1] = "0.75"
        with self.assertRaisesRegex(ValueError, "provenance frozen argument"):
            analyze(protocol, rows)

    def test_correction_preserves_frozen_scope(self) -> None:
        protocol = self.protocol()
        correction = create_correction(
            protocol,
            protocol_file_sha256="protocol-file",
            corrected_analyzer_sha256="corrected",
        )
        self.assertTrue(correction["correction"]["training_outputs_unchanged"])
        self.assertTrue(
            correction["correction"]["selection_and_expansion_gates_unchanged"]
        )
        self.assertFalse(
            correction["correction"]["test_labels_used_for_new_parameter_selection"]
        )


if __name__ == "__main__":
    unittest.main()
