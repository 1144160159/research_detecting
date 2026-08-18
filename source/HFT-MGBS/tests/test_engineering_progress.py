from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.generate_engineering_progress import generate_markdown


ROOT = Path(__file__).resolve().parents[1]


class EngineeringProgressTest(unittest.TestCase):
    def test_snapshot_keeps_optimality_boundary_and_live_blocker(self):
        search = json.loads(
            (ROOT / "configs" / "algorithm_search_rc1.json").read_text(
                encoding="utf-8"
            )
        )
        release = json.loads(
            (ROOT / "configs" / "release_candidate_rc1.json").read_text(
                encoding="utf-8"
            )
        )

        rendered = generate_markdown(
            search, release, "2026-07-29T00:00:00Z"
        )

        self.assertIn("冻结的 10 个候选", rendered)
        self.assertIn("不声称对所有可能算法全局最优", rendered)
        self.assertIn("最终 Pareto 资格：`false`", rendered)
        self.assertIn(
            release["observed_latest_physical_live_preflight"]["run_id"],
            rendered,
        )
        self.assertIn("thresholds.not_frozen", rendered)
        self.assertIn("内核接收至特征入队 P99", rendered)
        self.assertIn("每次 60 秒的被动确认", rendered)
        self.assertIn("8 队列 `xdp-skb` 三轮诊断均零丢包", rendered)
        self.assertIn("当前候选对为 `ens8f0/ens8f1`", rendered)
        self.assertIn("最终 10GbE 双口就绪状态", rendered)
        self.assertIn("final_live_run_allowed=false", rendered)


if __name__ == "__main__":
    unittest.main()
