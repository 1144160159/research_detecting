from __future__ import annotations

import unittest

from create_strict_v4_attack_taxonomy import classify


class StrictV4AttackTaxonomyTests(unittest.TestCase):
    def test_representative_categories(self) -> None:
        expected = {
            ("cic_iot2023", "ddos_tcp_flood"): "distributed_denial_of_service",
            ("cicids2017", "dos_hulk"): "denial_of_service",
            ("edge_iiot", "fingerprinting"): "reconnaissance_and_scanning",
            ("nf_cse", "ssh_bruteforce"): "credential_and_bruteforce",
            ("cic_ton_iot", "xss"): "web_and_injection_attack",
            ("ustc_tfc2016", "zeus"): "malware_and_botnet",
            ("nf_unsw", "backdoor"): "backdoor_and_infiltration",
            ("cic_iot2023", "dns_spoofing"): "mitm_and_spoofing",
            ("edge_iiot", "ransomware"): "ransomware",
            ("nf_unsw", "shellcode"): "exploitation",
            ("nf_unsw", "fuzzers"): "fuzzing",
            ("nf_unsw", "generic"): "generic_or_unspecified_attack",
        }
        for key, category in expected.items():
            self.assertEqual(classify(*key), category)

    def test_unknown_label_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "unmapped attack scenario"):
            classify("future_suite", "new_attack")


if __name__ == "__main__":
    unittest.main()
