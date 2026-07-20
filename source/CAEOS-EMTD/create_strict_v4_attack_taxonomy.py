from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from select_strict_v4_external_risk_candidate import canonical_hash


RECONNAISSANCE = {
    "analysis",
    "fingerprinting",
    "port_scanning",
    "portscan",
    "recon_host_discovery",
    "recon_os_scan",
    "recon_ping_sweep",
    "recon_port_scan",
    "reconnaissance",
    "scanning",
    "vulnerability_scan",
    "vulnerability_scanner",
}
CREDENTIAL = {
    "brute_force_web",
    "dictionary_bruteforce",
    "ftp_bruteforce",
    "ftp_patator",
    "password",
    "ssh_bruteforce",
    "ssh_patator",
    "web_bruteforce",
}
WEB_INJECTION = {
    "browser_hijacking",
    "brute_force_xss",
    "command_injection",
    "injection",
    "sql_injection",
    "uploading",
    "uploading_attack",
    "web_sql_injection",
    "web_xss",
    "xss",
}
BACKDOOR_INFILTRATION = {"backdoor", "infilteration", "infiltration"}
MITM_SPOOFING = {"dns_spoofing", "mitm", "mitm_arp_spoofing"}
EXPLOITATION = {"exploits", "heartbleed", "shellcode"}


def classify(suite: str, scenario: str) -> str:
    if scenario == "ddos" or scenario.startswith("ddos_") or scenario.startswith("mirai_"):
        return "distributed_denial_of_service"
    if scenario == "dos" or scenario.startswith("dos_"):
        return "denial_of_service"
    if scenario in RECONNAISSANCE:
        return "reconnaissance_and_scanning"
    if scenario in CREDENTIAL:
        return "credential_and_bruteforce"
    if scenario in WEB_INJECTION:
        return "web_and_injection_attack"
    if suite == "ustc_tfc2016" or scenario in {"backdoor_malware", "bot", "worms"}:
        return "malware_and_botnet"
    if scenario in BACKDOOR_INFILTRATION:
        return "backdoor_and_infiltration"
    if scenario in MITM_SPOOFING:
        return "mitm_and_spoofing"
    if scenario == "ransomware":
        return "ransomware"
    if scenario in EXPLOITATION:
        return "exploitation"
    if scenario == "fuzzers":
        return "fuzzing"
    if scenario == "generic":
        return "generic_or_unspecified_attack"
    raise ValueError(f"unmapped attack scenario: {suite}/{scenario}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("manifest_sha256") != canonical_hash(manifest):
        raise ValueError("coverage manifest SHA mismatch")

    rows: list[dict[str, str]] = []
    labels_by_category: dict[str, set[str]] = defaultdict(set)
    category_counts: Counter[str] = Counter()
    for suite, entry in sorted(manifest["scenario_registry"].items()):
        scenarios = entry["scenarios"]
        if len(scenarios) != entry["count"]:
            raise ValueError(f"scenario count mismatch for {suite}")
        for scenario in scenarios:
            category = classify(suite, scenario)
            rows.append({"suite": suite, "scenario": scenario, "broad_category": category})
            category_counts[category] += 1
            labels_by_category[category].add(scenario)

    expected = manifest["scenario_inference_units"]
    if len(rows) != expected:
        raise ValueError(f"expected {expected} rows, got {len(rows)}")

    payload: dict[str, Any] = {
        "schema_version": "strict_v4_attack_taxonomy_v1",
        "coverage_manifest_sha256": manifest["manifest_sha256"],
        "counting_unit": "dataset_scenario_pair",
        "broad_category_count": len(category_counts),
        "fine_grained_scenario_count": len(rows),
        "unique_source_label_count": len({row["scenario"] for row in rows}),
        "category_counts": dict(sorted(category_counts.items())),
        "source_labels_by_category": {
            category: sorted(labels)
            for category, labels in sorted(labels_by_category.items())
        },
        "mapping": rows,
        "scope_note": (
            "Broad categories are an analysis taxonomy, not native dataset labels. "
            "Fine-grained count uses dataset-scenario pairs because identical label "
            "strings in different datasets remain separate inference units."
        ),
    }
    payload["record_sha256"] = canonical_hash(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "broad_category_count": payload["broad_category_count"],
        "fine_grained_scenario_count": payload["fine_grained_scenario_count"],
        "unique_source_label_count": payload["unique_source_label_count"],
        "category_counts": payload["category_counts"],
        "record_sha256": payload["record_sha256"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
