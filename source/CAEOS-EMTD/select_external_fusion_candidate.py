from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


FUSION_DEFINITIONS = {
    "rank_mean": "arithmetic mean of separately calibrated empirical percentiles",
    "rank_union": "probabilistic union 1-(1-r_caeos)*(1-r_expert)",
    "rank_max": "maximum of separately calibrated empirical percentiles",
    "rank_min": "minimum of separately calibrated empirical percentiles",
    "rank_cauchy": "equal-weight Cauchy p-value combination",
    "rank_bonferroni": "Bonferroni-adjusted minimum anomaly p-value",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_seeds(value: str) -> tuple[int, ...]:
    tokens = [token.strip() for token in value.split(",")]
    if not tokens or any(not token for token in tokens):
        raise ValueError("seeds must be a non-empty comma-separated list")
    try:
        seeds = tuple(int(token) for token in tokens)
    except ValueError as error:
        raise ValueError("seeds must be integers") from error
    if any(seed < 0 for seed in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be unique non-negative integers")
    return tuple(sorted(seeds))


def read_object(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def _development_seeds(payload: dict[str, object], path: Path) -> tuple[int, ...]:
    scope = payload.get("selection_scope")
    if not isinstance(scope, dict) or not isinstance(scope.get("seeds"), list):
        raise ValueError(f"missing explicit development seed list: {path}")
    return tuple(sorted(int(seed) for seed in scope["seeds"]))


def build_manifest(
    screening_paths: Iterable[Path],
    safety_path: Path,
    confirmation_seeds: Iterable[int],
) -> dict[str, object]:
    paths = sorted(screening_paths)
    if not paths:
        raise ValueError("at least one screening input is required")
    candidates: list[dict[str, object]] = []
    development_seeds: tuple[int, ...] | None = None
    for path in paths:
        payload = read_object(path)
        seeds = _development_seeds(payload, path)
        if development_seeds is None:
            development_seeds = seeds
        elif development_seeds != seeds:
            raise ValueError("screening inputs use different development seeds")
        overall = payload.get("overall")
        if not isinstance(overall, dict) or int(overall.get("number_of_runs", 0)) <= 0:
            raise ValueError(f"invalid screening summary: {path}")
        methods = overall.get("methods")
        if not isinstance(methods, dict) or not methods:
            raise ValueError(f"screening summary has no methods: {path}")
        expert = str(overall.get("expert_name"))
        for fusion, item in methods.items():
            if not isinstance(item, dict):
                raise ValueError(f"invalid method summary: {path}:{fusion}")
            candidates.append(
                {
                    "expert_name": expert,
                    "fusion": str(fusion),
                    "mean_auroc": float(item["mean_auroc"]),
                    "minimum_auroc": float(item["minimum_auroc"]),
                    "mean_delta_vs_gate": float(item["mean_delta_vs_gate"]),
                    "wins_ties_losses_vs_gate": list(
                        item["wins_ties_losses_vs_gate"]
                    ),
                    "source": str(path),
                }
            )
    candidates.sort(
        key=lambda item: (
            float(item["mean_auroc"]),
            float(item["minimum_auroc"]),
            str(item["expert_name"]),
            str(item["fusion"]),
        ),
        reverse=True,
    )
    selected = candidates[0]
    if selected["fusion"] not in FUSION_DEFINITIONS:
        raise ValueError(f"unknown frozen fusion: {selected['fusion']!r}")

    safety = read_object(safety_path)
    safety_seeds = _development_seeds(safety, safety_path)
    if safety_seeds != development_seeds:
        raise ValueError("safety input does not use the screening development seeds")
    overall = safety.get("overall")
    if not isinstance(overall, dict) or overall.get("expert_name") != selected["expert_name"]:
        raise ValueError("safety input expert does not match screened candidate")
    methods = overall.get("methods")
    if not isinstance(methods, dict) or selected["fusion"] not in methods:
        raise ValueError("safety input does not contain screened fusion")
    safety_item = methods[selected["fusion"]]
    if not isinstance(safety_item, dict):
        raise ValueError("invalid selected safety summary")
    safety_gate = safety_item.get("development_safety_gate")
    metrics = safety_item.get("metrics")
    if not isinstance(safety_gate, dict) or not isinstance(metrics, dict):
        raise ValueError("selected safety summary is incomplete")
    if not bool(safety_gate.get("passes")):
        raise ValueError("screened candidate fails the development safety gate")

    assert development_seeds is not None
    confirmation = tuple(sorted(int(seed) for seed in confirmation_seeds))
    if not confirmation or len(set(confirmation)) != len(confirmation):
        raise ValueError("confirmation seeds must be non-empty and unique")
    overlap = sorted(set(development_seeds) & set(confirmation))
    if overlap:
        raise ValueError(f"development and confirmation seeds overlap: {overlap}")
    return {
        "schema_version": "external_risk_fusion_selection_v1",
        "purpose": "freeze_development_selected_candidate_before_confirmation",
        "candidate_status": "frozen_unconfirmed",
        "development_seeds": list(development_seeds),
        "confirmation_seeds": list(confirmation),
        "seed_overlap": [],
        "selection_rule": (
            "maximize scenario-mean development AUROC across all fixed candidates, "
            "then require AUROC improvement and <=0.01 mean regression in AUPR, "
            "oriented FPR95, and OSCR"
        ),
        "screened_expert_count": len(paths),
        "screened_candidate_count": len(candidates),
        "selected_candidate": {
            **selected,
            "expert_model": "mlp",
            "calibration": "separate known-validation empirical percentiles",
            "fusion_definition": FUSION_DEFINITIONS[selected["fusion"]],
            "base_risk": "cauchy_modality_support_union",
            "safety_gate": safety_gate,
            "metrics": metrics,
        },
        "screening_ranking": candidates,
        "inputs": {
            "screening": [
                {"path": str(path), "sha256": sha256(path)} for path in paths
            ],
            "safety": {"path": str(safety_path), "sha256": sha256(safety_path)},
        },
    }


def markdown(manifest: dict[str, object]) -> str:
    selected = manifest["selected_candidate"]
    assert isinstance(selected, dict)
    metrics = selected["metrics"]
    assert isinstance(metrics, dict)
    lines = [
        "# Edge external-risk fusion development selection",
        "",
        f"Status: `{manifest['candidate_status']}`",
        f"Development seeds: `{manifest['development_seeds']}`",
        f"Reserved confirmation seeds: `{manifest['confirmation_seeds']}`",
        "",
        "## Frozen candidate",
        "",
        f"- Expert risk: `{selected['expert_name']}` from `{selected['expert_model']}`",
        f"- Fusion: `{selected['fusion']}`",
        f"- Screened candidates: {manifest['screened_candidate_count']}",
        "",
        "| Metric | Gate mean | Candidate mean | Oriented delta | W/T/L |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in (
        "unknown_auroc",
        "unknown_aupr",
        "unknown_fpr95",
        "oscr",
        "known_macro_f1",
    ):
        item = metrics[name]
        lines.append(
            f"| {name} | {item['gate_mean']:.6f} | {item['candidate_mean']:.6f} | "
            f"{item['oriented_mean_delta']:+.6f} | "
            f"{'/'.join(str(value) for value in item['wins_ties_losses'])} |"
        )
    lines.extend(
        [
            "",
            "This is development-only evidence. The candidate must not be promoted "
            "until the reserved confirmation seeds pass the frozen gate.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freeze an external-risk fusion candidate")
    parser.add_argument("--screening-dir", required=True)
    parser.add_argument("--safety-input", required=True)
    parser.add_argument("--confirmation-seeds", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--markdown-output")
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    screening_dir = Path(args.screening_dir)
    paths = sorted(
        path
        for path in screening_dir.glob("*.json")
        if not path.name.endswith("_full_metrics.json")
        and path.name != Path(args.output).name
    )
    manifest = build_manifest(
        paths,
        Path(args.safety_input),
        parse_seeds(args.confirmation_seeds),
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    markdown_output = (
        Path(args.markdown_output)
        if args.markdown_output
        else output.with_suffix(".md")
    )
    markdown_output.write_text(markdown(manifest), encoding="utf-8")
    print(
        json.dumps(
            {
                "selected_candidate": manifest["selected_candidate"],
                "output": str(output),
                "markdown_output": str(markdown_output),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
