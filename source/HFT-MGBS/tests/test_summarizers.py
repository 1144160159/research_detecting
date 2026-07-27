from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import summarize_grouped_quality, summarize_pcap_matrix
from scripts.merge_offline_candidate_evidence import load_named


class SummarizerInputTest(unittest.TestCase):
    def _exercise(self, module, function_name):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "repeat1.json").write_text(
                json.dumps({"run": 1}), encoding="utf-8"
            )
            (root / "summary.json").write_text("", encoding="utf-8")
            with mock.patch.object(
                module,
                function_name,
                return_value={"candidate_count": 1},
            ) as summarize:
                with mock.patch.object(
                    sys, "argv", ["summarizer", str(root)]
                ):
                    with contextlib.redirect_stdout(io.StringIO()):
                        status = module.main()

        self.assertEqual(status, 0)
        # Python 3.7's unittest.mock call object does not expose ``.args``.
        named_runs = summarize.call_args[0][0]
        self.assertEqual(
            [name for name, _ in named_runs], ["repeat1.json"]
        )

    def test_pcap_summary_is_not_reingested(self):
        self._exercise(
            summarize_pcap_matrix, "summarize_offline_runs"
        )

    def test_quality_summary_is_not_reingested(self):
        self._exercise(
            summarize_grouped_quality, "summarize_quality_runs"
        )

    def test_joint_loader_ignores_all_derived_summaries(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "normal_repeat1.json").write_text(
                '{"run": 1}', encoding="utf-8"
            )
            (root / "summary.json").write_text("", encoding="utf-8")
            (root / "joint_grouped_summary.json").write_text(
                "", encoding="utf-8"
            )

            loaded = load_named(root)

        self.assertEqual(loaded, [("normal_repeat1.json", {"run": 1})])


if __name__ == "__main__":
    unittest.main()
