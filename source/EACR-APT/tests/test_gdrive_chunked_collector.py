import tempfile
import unittest
from pathlib import Path

from scripts.collect_gdrive_manifest_chunked import (
    atomic_json,
    covered_bytes,
    order_chunks,
    parse_args,
    parse_content_range,
    plan_chunks,
)


class GDriveChunkedCollectorTests(unittest.TestCase):
    def test_plan_chunks_preserves_an_existing_prefix(self):
        self.assertEqual(plan_chunks(10, 100, 32), [(10, 41), (42, 73), (74, 99)])

    def test_content_range_uses_final_redirect_response(self):
        headers = """HTTP/1.1 302 Found\r
Location: elsewhere\r
\r
HTTP/2 206\r
Content-Length: 32\r
Content-Range: bytes 10-41/100\r
"""
        self.assertEqual(parse_content_range(headers), (10, 41, 100))

    def test_reverse_request_order_keeps_an_explicit_canonical_plan(self):
        canonical = plan_chunks(0, 10, 4)
        self.assertEqual(canonical, [(0, 3), (4, 7), (8, 9)])
        self.assertEqual(order_chunks(canonical, "reverse"), [(8, 9), (4, 7), (0, 3)])
        self.assertEqual(canonical, [(0, 3), (4, 7), (8, 9)])

    def test_spread_order_starts_in_separated_regions(self):
        canonical = [(index, index) for index in range(7)]
        spread = order_chunks(canonical, "spread")
        self.assertEqual(spread, [(3, 3), (1, 1), (5, 5), (0, 0), (2, 2), (4, 4), (6, 6)])
        self.assertEqual(sorted(spread), canonical)

    def test_atomic_json_leaves_only_the_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "state.json"
            atomic_json(target, {"complete": False})
            self.assertEqual(target.read_text(encoding="utf-8"), '{\n  "complete": false\n}\n')
            self.assertEqual([path.name for path in target.parent.iterdir()], ["state.json"])

    def test_covered_bytes_merges_overlapping_multigranularity_chunks(self):
        with tempfile.TemporaryDirectory() as directory:
            chunk_dir = Path(directory)
            (chunk_dir / "000000000000-000000000009.chunk").write_bytes(b"a" * 10)
            (chunk_dir / "000000000005-000000000014.chunk").write_bytes(b"b" * 10)
            (chunk_dir / "000000000020-000000000024.chunk").write_bytes(b"c" * 5)
            (chunk_dir / "000000000030-000000000039.chunk").write_bytes(b"short")
            self.assertEqual(covered_bytes(chunk_dir, 100), 20)
            self.assertEqual(covered_bytes(chunk_dir, 100, prefix_size=8), 20)

    def test_state_stem_is_namespaced_and_path_safe(self):
        args = parse_args(
            [
                "--manifest",
                "manifest.json",
                "--root",
                "/gpu/root",
                "--state-stem",
                "theia6r_json_core",
            ]
        )
        self.assertEqual(args.state_stem, "theia6r_json_core")
        with self.assertRaises(SystemExit):
            parse_args(
                [
                    "--manifest",
                    "manifest.json",
                    "--root",
                    "/gpu/root",
                    "--state-stem",
                    "../escape",
                ]
            )


if __name__ == "__main__":
    unittest.main()
