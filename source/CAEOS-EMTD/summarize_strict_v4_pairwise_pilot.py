from __future__ import annotations

import summarize_strict_v4_pilot as base


if __name__ == "__main__":
    base.EXPECTED_POLICY = "strict_v4_pairwise_pilot_v1"
    base.EXPECTED_RISK = {
        "cauchy_modality_support_union",
        "pseudo_unknown_learned_blend",
    }
    base.main()
