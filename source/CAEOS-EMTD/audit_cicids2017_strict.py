from __future__ import annotations

import argparse
import json
from pathlib import Path

from caeos.data import prepare_tabular_open_set
from prepare_cicids2017_strict import (
    LOW_SUPPORT_ATTACK_LABELS,
    PRIMARY_ATTACK_LABELS,
)


SCENARIOS = {
    "bot": "Bot",
    "ddos": "DDoS",
    "dos_goldeneye": "DoS GoldenEye",
    "dos_hulk": "DoS Hulk",
    "dos_slowhttptest": "DoS Slowhttptest",
    "dos_slowloris": "DoS slowloris",
    "ftp_patator": "FTP-Patator",
    "heartbleed": "Heartbleed",
    "infiltration": "Infiltration",
    "portscan": "PortScan",
    "ssh_patator": "SSH-Patator",
    "web_bruteforce": "Web Attack - Brute Force",
    "web_sql_injection": "Web Attack - Sql Injection",
    "web_xss": "Web Attack - XSS",
}


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit every CIC-IDS2017 strict leave-one-attack split"
    )
    parser.add_argument("--csv", required=True)
    parser.add_argument("--config", default="configs/cicids2017_strict.json")
    parser.add_argument("--max-per-class", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def audit(
    csv_path: str,
    config_path: str,
    max_per_class: int,
    seed: int,
) -> dict[str, object]:
    config_file = Path(config_path)
    config = json.loads(config_file.read_text(encoding="utf-8"))
    reports = []
    failures = []
    for scenario, unknown_label in SCENARIOS.items():
        try:
            bundle = prepare_tabular_open_set(
                csv_path,
                config,
                [unknown_label],
                "Benign",
                max_per_class=max_per_class,
                seed=seed,
                split_strategy="capture_grouped",
            )
            metadata = bundle.split_metadata
            overlap = metadata["group_overlap"]
            per_class_groups = metadata["per_class_groups"]
            empty_group_splits = {
                label: [name for name, count in counts.items() if count <= 0]
                for label, counts in per_class_groups.items()
                if any(count <= 0 for count in counts.values())
            }
            problems = []
            if any(int(value) != 0 for value in overlap.values()):
                problems.append(f"nonzero group overlap: {overlap}")
            if empty_group_splits:
                problems.append(f"classes missing split groups: {empty_group_splits}")
            cross_label = metadata["cross_label_fingerprint_filter"]
            report = {
                "scenario": scenario,
                "unknown_label": unknown_label,
                "support_tier": (
                    "low_support_sensitivity"
                    if unknown_label in LOW_SUPPORT_ATTACK_LABELS
                    else "primary"
                ),
                "split_rows": {
                    "train": len(bundle.train),
                    "validation": len(bundle.validation),
                    "test": len(bundle.test),
                },
                "unknown_rows": int(bundle.sample_counts[unknown_label]),
                "group_overlap": overlap,
                "known_cross_label_fingerprint_rows_removed": int(
                    cross_label["removed_rows"]
                ),
                "problems": problems,
            }
            reports.append(report)
            if problems:
                failures.append({"scenario": scenario, "problems": problems})
        except Exception as error:
            failure = {
                "scenario": scenario,
                "unknown_label": unknown_label,
                "error_type": type(error).__name__,
                "error": str(error),
            }
            reports.append(failure)
            failures.append(failure)
    return {
        "schema_version": "cicids2017_strict_split_audit_v1",
        "csv": str(Path(csv_path).resolve()),
        "config": str(config_file.resolve()),
        "seed": seed,
        "max_per_class": max_per_class,
        "scenario_count": len(SCENARIOS),
        "primary_scenario_count": len(PRIMARY_ATTACK_LABELS),
        "low_support_scenario_count": len(LOW_SUPPORT_ATTACK_LABELS),
        "reports": reports,
        "failure_count": len(failures),
        "failures": failures,
        "passes": not failures,
    }


def main() -> None:
    args = parse_arguments()
    report = audit(args.csv, args.config, args.max_per_class, args.seed)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passes"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
