from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from create_strict_v4_external_confirmation_protocol import canonical_hash
from evaluate_strict_v4_comp_confirmation import load, validate_protocol


PAIRWISE_REQUIRED = (
    "metrics.json",
    "scores.npz",
    "evidence_package.npz",
    "provenance.json",
)
OPENDETECT_REQUIRED = ("metrics.json", "scores.npz", "provenance.json")


def artifact_set_nonempty(directory: Path, required: tuple[str, ...]) -> bool:
    return all(
        (directory / name).is_file() and (directory / name).stat().st_size > 0
        for name in required
    )


def load_json_object(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def npz_has_arrays(path: Path, required: tuple[str, ...]) -> bool:
    try:
        with np.load(path, allow_pickle=False) as archive:
            if not archive.files:
                return False
            if not set(required) <= set(archive.files):
                return False
            return all(np.asarray(archive[name]).size > 0 for name in required)
    except (OSError, ValueError, EOFError):
        return False


def pairwise_artifacts_valid(directory: Path) -> bool:
    if not artifact_set_nonempty(directory, PAIRWISE_REQUIRED):
        return False
    metrics = load_json_object(directory / "metrics.json")
    provenance = load_json_object(directory / "provenance.json")
    return bool(
        metrics
        and provenance is not None
        and metrics.get("risk_policy")
        == "strict_v4_comp_confirmation_pairwise_v1"
        and npz_has_arrays(
            directory / "scores.npz",
            ("test_unknown", "test_labels", "test_prediction"),
        )
        and npz_has_arrays(directory / "evidence_package.npz", ())
    )


def opendetect_artifacts_valid(directory: Path) -> bool:
    if not artifact_set_nonempty(directory, OPENDETECT_REQUIRED):
        return False
    metrics = load_json_object(directory / "metrics.json")
    provenance = load_json_object(directory / "provenance.json")
    return bool(
        metrics
        and provenance is not None
        and isinstance(metrics.get("reports", {}).get("opendetect"), dict)
        and npz_has_arrays(
            directory / "scores.npz",
            ("test_unknown", "test_labels", "test_opendetect"),
        )
    )


def build_progress(
    protocol: dict[str, Any],
    pairwise_root: Path,
    opendetect_root: Path,
    confirmation_path: Path,
) -> dict[str, Any]:
    pairwise_complete = []
    opendetect_complete = []
    for task in protocol["tasks"]:
        suite = str(task["suite"])
        scenario = str(task["scenario"])
        seed = int(task["seed"])
        key = f"{suite}/{scenario}/seed{seed}"
        pairwise_dir = pairwise_root / suite / f"{scenario}_seed{seed}"
        opendetect_dir = (
            opendetect_root / suite / f"{scenario}_seed{seed}_opendetect"
        )
        if pairwise_artifacts_valid(pairwise_dir):
            pairwise_complete.append(key)
        if opendetect_artifacts_valid(opendetect_dir):
            opendetect_complete.append(key)

    confirmation = {"state": "pending"}
    if confirmation_path.is_file() and confirmation_path.stat().st_size > 0:
        result = load(confirmation_path)
        canonical = result.get("manifest_sha256") == canonical_hash(result)
        confirmation = {
            "state": "complete" if canonical else "invalid",
            "canonical": canonical,
            "decision_passes": result.get("decision", {}).get("passes"),
            "manifest_sha256": result.get("manifest_sha256"),
        }

    progress: dict[str, Any] = {
        "schema_version": "strict_v4_comp_confirmation_progress_v1",
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol_manifest_sha256": protocol["manifest_sha256"],
        "expected_task_count": len(protocol["tasks"]),
        "pairwise": {
            "complete_count": len(pairwise_complete),
            "complete_tasks": pairwise_complete,
        },
        "opendetect": {
            "complete_count": len(opendetect_complete),
            "complete_tasks": opendetect_complete,
        },
        "confirmation": confirmation,
        "claim_boundary": {
            "partial_metrics_not_aggregated": True,
            "progress_is_not_an_effect_conclusion": True,
        },
    }
    progress["manifest_sha256"] = canonical_hash(progress)
    return progress


def write_progress(progress: dict[str, Any], output_root: Path) -> Path:
    output_root.mkdir(parents=True, exist_ok=True)
    pairwise_count = progress["pairwise"]["complete_count"]
    opendetect_count = progress["opendetect"]["complete_count"]
    observed = datetime.fromisoformat(progress["observed_at_utc"])
    timestamp = observed.strftime("%Y%m%dT%H%M%S%fZ")
    output = output_root / (
        f"progress_pairwise_{pairwise_count:03d}_"
        f"opendetect_{opendetect_count:03d}_{timestamp}.json"
    )
    temporary = output.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(progress, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(output)
    return output


def append_state(path: Path, message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} {message}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_v1/protocol.json"),
    )
    parser.add_argument(
        "--pairwise-root",
        type=Path,
        default=Path("runs/strict_v4_comp_confirmation_v1/pairwise"),
    )
    parser.add_argument(
        "--opendetect-root",
        type=Path,
        default=Path("runs/strict_v4_comp_confirmation_v1/opendetect"),
    )
    parser.add_argument(
        "--confirmation",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_v1/confirmation.json"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("results/strict_v4_comp_confirmation_progress_v1"),
    )
    parser.add_argument(
        "--state-log",
        type=Path,
        default=Path(
            "results/strict_v4_comp_confirmation_progress_v1/watcher_state.log"
        ),
    )
    parser.add_argument("--poll-seconds", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    protocol = load(args.protocol)
    validate_protocol(protocol)
    previous_counts: tuple[int, int] | None = None
    while True:
        progress = build_progress(
            protocol,
            args.pairwise_root,
            args.opendetect_root,
            args.confirmation,
        )
        counts = (
            progress["pairwise"]["complete_count"],
            progress["opendetect"]["complete_count"],
        )
        if counts != previous_counts or args.once:
            output = write_progress(progress, args.output_root)
            append_state(
                args.state_log,
                f"froze {output.name} {progress['manifest_sha256']}",
            )
            previous_counts = counts
        if args.once or progress["confirmation"]["state"] == "complete":
            break
        time.sleep(args.poll_seconds)


if __name__ == "__main__":
    main()
