import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reproducibility"))

from run_minimal_repro import build_runs, command_for


def protocol():
    return json.loads(
        (ROOT / "reproducibility/minimal_open_set_profile.json").read_text(
            encoding="utf-8"
        )
    )


def test_smoke_profile_is_two_datasets_by_three_risks(tmp_path):
    spec = protocol()
    inputs = {
        "mal_csv": tmp_path / "mal.csv",
        "hikari_csv": tmp_path / "hikari.csv",
    }
    runs = build_runs(spec, "smoke", inputs, tmp_path / "out")

    assert len(runs) == 6
    assert {run["dataset"] for run in runs} == {
        "mal_tls_tor",
        "hikari_probing",
    }
    assert {run["profile"] for run in runs} == {
        "support_union",
        "cauchy_evidence",
        "nested_conflict_gate",
    }
    assert {run["seed"] for run in runs} == {7}


def test_commands_freeze_grouped_split_and_risk_profiles(tmp_path):
    spec = protocol()
    runs = build_runs(
        spec,
        "smoke",
        {
            "mal_csv": tmp_path / "mal.csv",
            "hikari_csv": tmp_path / "hikari.csv",
        },
        tmp_path / "out",
    )
    commands = [command_for(run, spec, ROOT, "python") for run in runs]

    for command in commands:
        assert command[command.index("--split-strategy") + 1] == "fingerprint_grouped"
        assert command[command.index("--known-acceptance") + 1] == "0.95"
        assert "--output-dir" in command
    fixed = [command for command in commands if "--fixed-risk-name" in command]
    nested = [
        command
        for command in commands
        if command[command.index("--risk-selection") + 1] == "nested_conflict_gate"
    ]
    assert len(fixed) == 4
    assert len(nested) == 2
