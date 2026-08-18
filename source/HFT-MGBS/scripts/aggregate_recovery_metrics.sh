#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 4 ]]; then
  echo "usage: $0 OUTPUT_JSON RUN_DIR RUN_DIR RUN_DIR [RUN_DIR ...]" >&2
  exit 2
fi
output="$1"
shift
inputs=()
for run_dir in "$@"; do
  inputs+=("${run_dir}/recovery.json")
done
mkdir -p "$(dirname "${output}")"
jq -s \
  --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '
  {
    schema_version: 1,
    generated_at: $generated_at,
    evidence_scope: "three-repeat physical Rust to Python reverse-worker recovery",
    candidate_id: "A09",
    run_count: length,
    max_recovery_ms: 300.0,
    runs: map({
      generated_unix_ms,
      baseline_round_trip_ms,
      reconnect_ms,
      recovered_round_trip_ms,
      recovery_to_success_ms,
      passed
    }),
    observed_worst_case: {
      baseline_round_trip_ms_max: (map(.baseline_round_trip_ms) | max),
      reconnect_ms_max: (map(.reconnect_ms) | max),
      recovered_round_trip_ms_max: (map(.recovered_round_trip_ms) | max),
      recovery_to_success_ms_max: (map(.recovery_to_success_ms) | max)
    },
    passed: (
      length >= 3
      and ([.[].passed] | all)
      and ((map(.recovery_to_success_ms) | max) <= 300.0)
    )
  }' "${inputs[@]}" > "${output}"
sha256sum "${output}" > "${output}.sha256"
cat "${output}"
