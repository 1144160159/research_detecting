from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.summarize_physical_link_diagnostics import summarize


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


class PhysicalLinkDiagnosticsTest(unittest.TestCase):
    def test_selects_timestamp_af_packet_and_rejects_xdp_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            readiness = root / "readiness.json"
            write_json(readiness, {"hardware_pair_count": 1})

            runs = {}
            for driver in ("af-packet-ts", "xdp", "xdp-skb"):
                run = root / driver
                run.mkdir()
                (run / "manifest.txt").write_text(
                    "capture_driver={}\nstatus={}\n"
                    "capture_exit_status={}\ninjector_exit_status=0\n".format(
                        driver,
                        (
                            "raw_evidence_complete"
                            if driver == "af-packet-ts"
                            else "execution_failed"
                        ),
                        "0" if driver == "af-packet-ts" else "134",
                    ),
                    encoding="utf-8",
                )
                if driver == "af-packet-ts":
                    write_json(
                        run / "live_evidence.diagnostic.json",
                        {"composition": {"diagnostic_accepted": True}},
                    )
                else:
                    (run / "capture_stderr.log").write_text(
                        "UMEM dropped with 2048 frames still allocated",
                        encoding="utf-8",
                    )
                runs[driver] = run

            result = summarize(
                readiness,
                runs["af-packet-ts"],
                runs["xdp"],
                runs["xdp-skb"],
            )

        self.assertTrue(result["selection_complete"])
        self.assertEqual(
            result["selected_capture_driver"], "af-packet-ts"
        )
        self.assertFalse(result["production_run_allowed"])
        self.assertTrue(result["runs"][1]["umem_release_failure"])
        self.assertTrue(result["runs"][2]["umem_release_failure"])


if __name__ == "__main__":
    unittest.main()
