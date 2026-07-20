from __future__ import annotations

import argparse
import json
from pathlib import Path

from create_strict_v4_aegis_training_pilot_protocol import METHODS
from summarize_strict_v4_external_training_pilot import analyze, render


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--opendetect-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(
        args.pilot_root,
        args.source_root,
        args.opendetect_root,
        methods=METHODS,
        analysis_schema="strict_v4_aegis_training_pilot_analysis_v1",
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "analysis.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    text = render(result).replace(
        "# Strict-v4 external training baseline pilot",
        "# Strict-v4 AEGIS training baseline pilot",
        1,
    )
    (args.output_dir / "analysis.md").write_text(text, encoding="utf-8")
    (args.output_dir / "pilot_complete").write_text(
        result["pilot_protocol_manifest_sha256"] + "\n", encoding="ascii"
    )
    if result["expand_to_full102"]:
        (args.output_dir / "full102_expansion_required").write_text(
            "\n".join(result["expand_to_full102"]) + "\n", encoding="ascii"
        )
    print(text, end="")


if __name__ == "__main__":
    main()
