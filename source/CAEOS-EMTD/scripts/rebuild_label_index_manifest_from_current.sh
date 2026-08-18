#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 || $# -gt 5 ]]; then
  echo "usage: $0 CURRENT_MANIFEST REGISTRY EXCLUSION_POLICY ASSEMBLER [OUTPUT]" >&2
  exit 2
fi

current_manifest=$1
registry=$2
exclusion_policy=$3
assembler=$4
output=${5:-"${current_manifest}.new"}
python_binary=${PYTHON_BINARY:-python}

arguments=()
while IFS= read -r path; do
  [[ -n "$path" ]] && arguments+=(--index-audit "$path")
done < <(jq -r '.datasets[].index_audit_path // empty' "$current_manifest")
while IFS= read -r path; do
  [[ -n "$path" ]] && arguments+=(--coverage-audit "$path")
done < <(jq -r '.datasets[].coverage_evidence[]?.path // empty' "$current_manifest")

"$python_binary" "$assembler" \
  --registry "$registry" \
  --output "$output" \
  --exclusion-policy "$exclusion_policy" \
  "${arguments[@]}"
