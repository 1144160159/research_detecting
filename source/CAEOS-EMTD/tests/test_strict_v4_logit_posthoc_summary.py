import json
import tempfile
import unittest
from pathlib import Path

from create_strict_v4_external_confirmation_protocol import canonical_hash
from create_strict_v4_logit_posthoc_expansion_gate import create_gate
from summarize_strict_v4_logit_posthoc_pilot import analyze


def report(value: float) -> dict:
    return {
        "known_macro_f1": 0.75,
        "unknown_auroc": value,
        "unknown_aupr": value,
        "unknown_fpr95": 1.0 - value,
        "oscr": value,
    }


def write(path: Path, reports: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "split_metadata": {"split_fingerprint": "same"},
                "reports": reports,
            }
        ),
        encoding="utf-8",
    )


class StrictV4LogitPosthocSummaryTests(unittest.TestCase):
    def test_all_passing_fixture_expands_gen(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            selected = {
                f"suite_{index}": ["first", "second"] for index in range(7)
            }
            protocol = {
                "schema_version": "strict_v4_mlp_logit_posthoc_protocol_v1",
                "mode": "pilot",
                "expected_runs": 14,
                "selected_scenarios": selected,
            }
            protocol["manifest_sha256"] = canonical_hash(protocol)
            pilot = root / "pilot"
            pilot.mkdir()
            (pilot / "protocol_manifest.json").write_text(
                json.dumps(protocol), encoding="utf-8"
            )
            source = root / "source"
            external = root / "external"
            for suite, scenarios in selected.items():
                for scenario in scenarios:
                    write(
                        pilot / suite / f"{scenario}_seed7" / "metrics.json",
                        {"gen": report(0.8), "shannon_entropy": report(0.6)},
                    )
                    write(
                        source / suite / f"{scenario}_seed7_mlp" / "metrics.json",
                        {"energy": report(0.7)},
                    )
                    write(
                        external
                        / suite
                        / f"{scenario}_seed7_opendetect"
                        / "metrics.json",
                        {"opendetect": report(0.65)},
                    )
            gate = create_gate(protocol, 0)
            result = analyze(pilot, source, external, gate)
            self.assertTrue(result["decision"]["expand_gen_to_full102"])
            self.assertTrue(all(result["expansion_checks"].values()))


if __name__ == "__main__":
    unittest.main()
