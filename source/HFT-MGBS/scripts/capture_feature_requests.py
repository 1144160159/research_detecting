"""Capture and acknowledge raw_v1 requests from a Rust replay binary."""

from __future__ import annotations

import argparse
import json
import socket
import time
from pathlib import Path

from hft_mgbs.feature_equivalence import summarize_feature_vectors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--startup-timeout-s", type=float, default=30.0)
    parser.add_argument("--idle-timeout-s", type=float, default=2.0)
    args = parser.parse_args()

    feature_vectors = []
    request_count = 0
    started = time.monotonic()
    last_request = None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((args.host, args.port))
        listener.listen(128)
        listener.settimeout(0.2)
        while True:
            now = time.monotonic()
            if last_request is None:
                if now - started > args.startup_timeout_s:
                    raise TimeoutError("no feature request arrived")
            elif now - last_request > args.idle_timeout_s:
                break
            try:
                connection, _ = listener.accept()
            except socket.timeout:
                continue
            with connection:
                connection.settimeout(5.0)
                reader = connection.makefile("r", encoding="utf-8")
                line = reader.readline()
                if not line:
                    continue
                request = json.loads(line)
                if request.get("candidate_id") != "A09":
                    raise ValueError("unexpected candidate")
                if request.get("feature_encoding") != "raw_v1":
                    raise ValueError("unexpected feature encoding")
                flows = request.get("flows") or []
                feature_vectors.extend(flow["features"] for flow in flows)
                response = {
                    "ok": True,
                    "predictions": [0 for _ in flows],
                    "error": None,
                }
                connection.sendall(
                    (
                        json.dumps(response, separators=(",", ":"))
                        + "\n"
                    ).encode("utf-8")
                )
                request_count += 1
                last_request = time.monotonic()

    summary = summarize_feature_vectors(feature_vectors)
    summary.update(
        {
            "schema_version": 1,
            "scope": "rust_feature_stream_equivalence_probe",
            "request_count": request_count,
        }
    )
    args.output.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
