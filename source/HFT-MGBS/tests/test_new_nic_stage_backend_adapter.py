import unittest

from hft_mgbs.new_nic_r0_unified import (
    stage_backend_binding_from_r0_identity,
)


class NewNicStageBackendAdapterTests(unittest.TestCase):
    def test_exact_xdp_primary_dpdk_fallback_pair_is_preserved(self):
        result = stage_backend_binding_from_r0_identity(
            {
                "backends": [
                    "native_af_xdp_forced_zerocopy",
                    "dpdk_multiqueue_rss_tss",
                ],
                "primary_backend": "native_af_xdp_forced_zerocopy",
                "fallback_backend": "dpdk_multiqueue_rss_tss",
            }
        )

        self.assertEqual(
            result,
            {
                "primary_backend": "native_af_xdp_forced_zerocopy",
                "fallback_backend": "dpdk_multiqueue_rss_tss",
            },
        )

    def test_missing_fallback_identity_is_rejected(self):
        with self.assertRaises(ValueError):
            stage_backend_binding_from_r0_identity(
                {
                    "backends": ["native_af_xdp_forced_zerocopy"],
                    "primary_backend": "native_af_xdp_forced_zerocopy",
                    "fallback_backend": None,
                }
            )

    def test_reordered_or_aliased_pair_is_rejected(self):
        with self.assertRaises(ValueError):
            stage_backend_binding_from_r0_identity(
                {
                    "backends": [
                        "dpdk_multiqueue_rss_tss",
                        "native_af_xdp_forced_zerocopy",
                    ],
                    "primary_backend": "native_af_xdp_forced_zerocopy",
                    "fallback_backend": "dpdk_rss_tss_multiqueue",
                }
            )


if __name__ == "__main__":
    unittest.main()
