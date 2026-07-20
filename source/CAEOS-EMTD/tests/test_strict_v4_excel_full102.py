import unittest

from create_strict_v4_external_confirmation_protocol import canonical_hash
from summarize_strict_v4_excel_full102 import merge_and_decide


class StrictV4ExCeLFull102Tests(unittest.TestCase):
    def test_merge_keeps_stronger_opendetect(self) -> None:
        metrics = {
            "known_macro_f1": 0.8, "unknown_auroc": 0.8, "unknown_aupr": 0.7,
            "unknown_fpr95": 0.2, "oscr": 0.7,
        }
        existing = {
            "overall": [dict(method="opendetect", **metrics)],
            "by_suite": {"suite": [dict(method="opendetect", **metrics)]},
        }
        blocks = {"suite/scenario": {"excel": dict(metrics, unknown_auroc=0.6)}}
        overall, _, decision = merge_and_decide(existing, blocks)
        self.assertEqual({row["method"] for row in overall}, {"opendetect", "excel"})
        self.assertEqual(decision["selected_comparator"], "opendetect")
        self.assertTrue(decision["existing_opendetect_protocol_remains_valid"])

    def test_canonical_hash_excludes_manifest_field(self) -> None:
        payload = {"schema_version": "strict_v4_excel_full102_protocol_v1"}
        payload["manifest_sha256"] = canonical_hash(payload)
        self.assertEqual(payload["manifest_sha256"], canonical_hash(payload))


if __name__ == "__main__":
    unittest.main()
