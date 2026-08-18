from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def reconcile(input_path: Path, output_path: Path) -> dict[str, Any]:
    report = json.loads(input_path.read_text(encoding="utf-8"))
    if report.get("schema_version") != "caeos_cicddos2019_label_index_audit_v1":
        raise ValueError("unsupported CICDDoS2019 label index audit schema")
    if report.get("dataset_id") != "cicddos2019":
        raise ValueError("CICDDoS2019 audit dataset mismatch")

    counters = report.get("input_counters", {})
    mismatch_count = int(counters.get("member_label_conflicts", 0))
    valid_rows = int(counters.get("valid_rows", 0))
    report["member_name_label_consistency"] = {
        "authority": "row_level_Label_column",
        "member_name_role": "informational_partition_hint_only",
        "mismatch_count": mismatch_count,
        "gate": "informational_only",
        "reason": (
            "official CICDDoS2019 CSV members contain row-level labels that "
            "can differ from the member filename; the row Label remains the "
            "official flow authority"
        ),
    }
    report["ready_for_pcap_coverage_dry_run"] = valid_rows > 0
    report["ready_for_pcap_coverage_dry_run_reason"] = (
        "row-level official labels indexed; member-name mismatches are audited "
        "but do not override or block official row labels"
    )
    report.pop("audit_sha256", None)
    report["audit_sha256"] = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    atomic_json(output_path, report)
    return report


def main() -> None:
    args = parse_arguments()
    print(
        json.dumps(
            reconcile(args.input, args.output),
            ensure_ascii=False,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
