from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

from validate_splitpcap_integrity import capture_fingerprint


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".partial")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def tool_identity(command: list[str]) -> str:
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    lines = (result.stdout or result.stderr).splitlines()
    return lines[0].strip() if lines else f"{command[0]} exit={result.returncode}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-member")
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--pcapfix", default="/usr/bin/pcapfix")
    parser.add_argument("--tshark", default="/usr/bin/tshark")
    parser.add_argument("--capinfos", default="/usr/bin/capinfos")
    args = parser.parse_args()
    if args.source_member is not None:
        raise ValueError("archive-member repair requires prior audited materialization")
    if not args.source.is_file():
        raise FileNotFoundError(args.source)

    args.output_root.mkdir(parents=True, exist_ok=True)
    original_sha256 = sha256_file(args.source)
    repair_id = hashlib.sha256(
        f"{args.dataset_id}\0{args.source}\0{original_sha256}".encode("utf-8")
    ).hexdigest()
    repaired = args.output_root / f"{repair_id}.repaired.pcap"
    temporary = args.output_root / f"{repair_id}.partial.pcap"
    log_path = args.output_root / f"{repair_id}.pcapfix.log"
    temporary.unlink(missing_ok=True)
    started = time.time()
    result = subprocess.run(
        [args.pcapfix, "--deep-scan", "--keep-outfile", "--outfile", str(temporary), str(args.source)],
        check=False,
        capture_output=True,
        text=True,
    )
    log_path.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode != 0 or not temporary.is_file():
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"pcapfix failed ({result.returncode}); see {log_path}")
    os.replace(temporary, repaired)

    original_fingerprint = capture_fingerprint([args.source])
    repaired_fingerprint = capture_fingerprint([repaired])
    if original_fingerprint != repaired_fingerprint:
        repaired.unlink(missing_ok=True)
        raise RuntimeError(
            "pcapfix changed the captured packet multiset: "
            + json.dumps(
                {
                    "original": original_fingerprint,
                    "repaired": repaired_fingerprint,
                },
                sort_keys=True,
            )
        )

    capinfos = subprocess.run(
        [args.capinfos, "-c", "-s", "-a", "-e", str(repaired)],
        check=False,
        capture_output=True,
        text=True,
    )
    scan = subprocess.run(
        [args.tshark, "-n", "-r", str(repaired), "-T", "fields", "-e", "frame.number"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if capinfos.returncode != 0 or scan.returncode != 0:
        raise RuntimeError(
            f"repaired PCAP validation failed: capinfos={capinfos.returncode}, "
            f"tshark={scan.returncode}, stderr={scan.stderr[-1000:]}"
        )

    entry = {
        "dataset_id": args.dataset_id,
        "source_path": str(args.source),
        "source_member": None,
        "original_sha256": original_sha256,
        "original_size_bytes": args.source.stat().st_size,
        "repaired_path": str(repaired),
        "repaired_sha256": sha256_file(repaired),
        "repaired_size_bytes": repaired.stat().st_size,
        "repair_tool": tool_identity([args.pcapfix, "--help"]),
        "repair_mode": "deep_scan_keep_outfile",
        "repair_log_path": str(log_path),
        "repair_log_sha256": sha256_file(log_path),
        "captured_packet_fingerprint": original_fingerprint,
        "exact_captured_packet_multiset_preserved": True,
        "capinfos_validation": capinfos.stdout,
        "full_tshark_scan_passed": True,
        "elapsed_seconds": time.time() - started,
    }
    manifest = (
        json.loads(args.manifest.read_text(encoding="utf-8"))
        if args.manifest.exists()
        else {"schema_version": "caeos_pcap_repair_manifest_v1", "repairs": []}
    )
    repairs = [
        item
        for item in manifest.get("repairs", [])
        if not (
            item["dataset_id"] == args.dataset_id
            and item["source_path"] == str(args.source)
            and item.get("source_member") is None
        )
    ]
    repairs.append(entry)
    manifest["repairs"] = sorted(
        repairs, key=lambda item: (item["dataset_id"], item["source_path"], item.get("source_member") or "")
    )
    manifest["repair_count"] = len(manifest["repairs"])
    manifest["all_repairs_fully_validated"] = all(
        item.get("full_tshark_scan_passed", False) for item in manifest["repairs"]
    )
    atomic_json(args.manifest, manifest)
    print(json.dumps(entry, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
