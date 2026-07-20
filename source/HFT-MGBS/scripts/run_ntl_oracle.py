"""Run GPL NTLFlowLyzer out of process as an isolated correctness oracle."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--ntl-root", type=Path, required=True)
    parser.add_argument("--activity-timeout-s", type=int, default=300)
    parser.add_argument("--max-flow-duration-s", type=int, default=120)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_csv = args.output_dir / "ntl_flows.csv"
    config_path = args.output_dir / "ntl_config.json"
    log_path = args.output_dir / "ntl_run.log"
    config = {
        "pcap_file_address": str(args.pcap),
        "output_file_address": str(output_csv),
        "label": "oracle",
        "number_of_threads": args.threads,
        "feature_extractor_min_flows": 100,
        "writer_min_rows": 100,
        "read_packets_count_value_log_info": 100000,
        "check_flows_ending_min_flows": 100,
        "capturer_updating_flows_min_value": 100,
        "max_flow_duration": args.max_flow_duration_s,
        "activity_timeout": args.activity_timeout_s,
        "floating_point_unit": ".8f",
        "max_rows_number": 1000000,
        "features_ignore_list": [],
    }
    config_path.write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(args.ntl_root)
    completed = subprocess.run(
        [sys.executable, "-m", "NTLFlowLyzer", "-c", str(config_path)],
        cwd=str(args.ntl_root),
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )
    log_path.write_text(completed.stdout, encoding="utf-8")
    csv_files = sorted(args.output_dir.glob("ntl_flows*.csv"))
    output_rows = 0
    for csv_path in csv_files:
        with csv_path.open("r", encoding="utf-8", errors="replace") as handle:
            output_rows += max(0, sum(1 for _ in handle) - 1)
    parser_error_markers = ("!! Exception happened!", "ERROR in packet number")
    parser_errors = [marker for marker in parser_error_markers if marker in completed.stdout]
    accepted = completed.returncode == 0 and output_rows > 0 and not parser_errors
    manifest = {
        "schema_version": 1,
        "status": "complete" if accepted else "failed_evidence_gate",
        "returncode": completed.returncode,
        "execution_mode": "isolated_subprocess_oracle",
        "license_boundary": "NTLFlowLyzer_GPL_not_linked_into_HFT_MGBS",
        "pcap": str(args.pcap),
        "config": str(config_path),
        "output_csv": str(output_csv),
        "output_csv_files": [str(path) for path in csv_files],
        "output_rows": output_rows,
        "parser_error_markers": parser_errors,
        "log": str(log_path),
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
