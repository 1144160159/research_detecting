#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-modality-formal-20260716}"
FROZEN_ROOT="${FROZEN_ROOT:-/opt/data/private/wangwt/ParkAttackKE/CAEOS-EMTD-strict-v2-20260716/runs/strict_v2_caeos_frozen_policy_5seed}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$PROJECT_ROOT/runs/strict_v2_caeos_confirmed_policy_5seed}"
CONDA="${CONDA:-/opt/data/private/wangwt/anaconda3/bin/conda}"

EDGE_ROOT="$PROJECT_ROOT/runs/strict_v2_caeos_modality_union_edge_5seed/edge_iiot"
NF_CSE_ROOT="$FROZEN_ROOT/nf_cse"
USTC_ROOT="$FROZEN_ROOT/ustc_tfc2016"

count_files() {
  find -L "$1" -name "$2" | wc -l
}

[[ $(count_files "$EDGE_ROOT" metrics.json) -eq 70 ]]
[[ $(count_files "$NF_CSE_ROOT" metrics.json) -eq 70 ]]
[[ $(count_files "$USTC_ROOT" metrics.json) -eq 50 ]]
[[ $(count_files "$EDGE_ROOT" failure.json) -eq 0 ]]
[[ $(count_files "$NF_CSE_ROOT" failure.json) -eq 0 ]]
[[ $(count_files "$USTC_ROOT" failure.json) -eq 0 ]]

if [[ -e "$OUTPUT_ROOT" ]]; then
  [[ -L "$OUTPUT_ROOT/edge_iiot" ]]
  [[ -L "$OUTPUT_ROOT/nf_cse" ]]
  [[ -L "$OUTPUT_ROOT/ustc_tfc2016" ]]
  [[ $(readlink -f "$OUTPUT_ROOT/edge_iiot") == $(readlink -f "$EDGE_ROOT") ]]
  [[ $(readlink -f "$OUTPUT_ROOT/nf_cse") == $(readlink -f "$NF_CSE_ROOT") ]]
  [[ $(readlink -f "$OUTPUT_ROOT/ustc_tfc2016") == $(readlink -f "$USTC_ROOT") ]]
else
  mkdir -p "$OUTPUT_ROOT"
  ln -s "$EDGE_ROOT" "$OUTPUT_ROOT/edge_iiot"
  ln -s "$NF_CSE_ROOT" "$OUTPUT_ROOT/nf_cse"
  ln -s "$USTC_ROOT" "$OUTPUT_ROOT/ustc_tfc2016"
fi

{
  printf 'edge_iiot=%s metrics=70\n' "$(readlink -f "$OUTPUT_ROOT/edge_iiot")"
  printf 'nf_cse=%s metrics=70\n' "$(readlink -f "$OUTPUT_ROOT/nf_cse")"
  printf 'ustc_tfc2016=%s metrics=50\n' "$(readlink -f "$OUTPUT_ROOT/ustc_tfc2016")"
  printf 'composition=confirmed_cauchy_modality_union_v1_edge_plus_frozen_nf_cse_ustc\n'
} > "$OUTPUT_ROOT/COMPOSITE_SOURCES.txt"

for artifact in metrics.json scores.npz evidence_package.npz provenance.json; do
  observed=$(count_files "$OUTPUT_ROOT" "$artifact")
  if [[ "$observed" -ne 190 ]]; then
    printf 'composite artifact coverage mismatch for %s: %d/190\n' \
      "$artifact" "$observed" >&2
    exit 1
  fi
done

cd "$PROJECT_ROOT"
"$CONDA" run -n py3.9 python summarize_caeos_strict_v2.py \
  --root "$OUTPUT_ROOT" \
  --seeds 7,11,19,23,37 \
  --output-dir results/strict_v2_caeos_confirmed_policy_5seed
