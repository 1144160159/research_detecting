import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "restore_ustc_tfc2016_campaign_inputs.sh"
QUALITY = ROOT / "configs" / "ustc_tfc2016_binary_quality.json"


class RestoreUstcTfc2016InputsContractTest(unittest.TestCase):
    def test_source_commit_and_all_contract_paths_are_frozen(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            'readonly COMMIT="4bc9683b996f582c3843815b68da8e4dce9c7e1e"',
            text,
        )
        rows = re.findall(
            r"^(Benign|Malware)/([^|]+)\|(\d+)\|([0-9a-f]{40})\|"
            r"((?:Benign|Malware)/[^\n]+\.pcap)$",
            text,
            flags=re.MULTILINE,
        )
        self.assertEqual(len(rows), 18)
        targets = {row[4] for row in rows}
        self.assertEqual(len(targets), 18)
        quality = json.loads(QUALITY.read_text(encoding="utf-8"))
        expected = {
            str(Path(item["path"]).relative_to(
                "/opt/data/private/wangwt/ParkAttackKE/datasets/USTC-TFC2016"
            )).replace("\\", "/")
            for item in quality["samples"]
        }
        self.assertEqual(targets, expected)

    def test_fail_closed_download_and_sealing_gates_are_present(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for token in (
            "git hash-object --no-filters",
            "--continue-at -",
            "capinfos -c",
            "find \"${TARGET}\" -type l",
            "find \"${TARGET}\" -name '*.part'",
            "sha256sum -c",
            "source_manifest_v1.json",
            "ALL_DONE",
        ):
            self.assertIn(token, text)


if __name__ == "__main__":
    unittest.main()
