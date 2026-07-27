from __future__ import annotations

import unittest

from analyze_strict_v4_conservative_missing_aware_fallback_development import (
    CONSERVATIVE_CANDIDATE,
    should_activate,
)


class ConservativeMissingAwareFallbackTests(unittest.TestCase):
    def test_candidate_identity_is_explicitly_conservative(self) -> None:
        self.assertEqual(
            CONSERVATIVE_CANDIDATE,
            "selected_risk_compatible_missing_aware_fallback_v1",
        )

    def test_activation_requires_compatible_selected_risk(self) -> None:
        self.assertTrue(
            should_activate("cauchy_modality_support_union")
        )
        self.assertFalse(should_activate("pseudo_unknown_learned_blend"))


if __name__ == "__main__":
    unittest.main()
