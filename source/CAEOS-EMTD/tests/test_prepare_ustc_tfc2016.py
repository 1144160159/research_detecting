import tempfile
import unittest
from pathlib import Path

from prepare_ustc_tfc2016 import discover_pcaps, label_for, part_name


class PrepareUstcTfc2016Test(unittest.TestCase):
    def test_benign_pcaps_are_merged_under_one_class(self):
        self.assertEqual(label_for(Path("Benign/SMB/SMB-1.pcap")), "Benign")

    def test_malware_label_comes_from_pcap_stem(self):
        self.assertEqual(label_for(Path("Malware/Nsis-ay.pcap")), "Nsis-ay")

    def test_discovery_filter_is_case_insensitive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Malware").mkdir()
            (root / "Malware" / "Tinba.pcap").touch()
            (root / "Malware" / "Zeus.pcap").touch()
            matches = discover_pcaps(root, "tinba")
        self.assertEqual([path.name for path in matches], ["Tinba.pcap"])

    def test_part_names_are_flat_and_deterministic(self):
        self.assertEqual(
            part_name(Path("Benign/SMB/SMB-1.pcap")),
            "Benign_SMB_SMB-1.pcap.csv",
        )


if __name__ == "__main__":
    unittest.main()
