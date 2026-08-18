#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -lt 4 ]]; then
  echo "usage: $0 OUTPUT_JSON RUN_DIR RUN_DIR RUN_DIR [RUN_DIR ...]" >&2
  exit 2
fi

output="$1"
shift
metrics=()
max_cpu_percent=0
max_rss_kb=0
runtime_batch_size=""
runtime_feature_flush_us=""
runtime_request_timeout_ms=""
for run_dir in "$@"; do
  metrics+=("${run_dir}/metrics.json")
  time_file="${run_dir}/physical_process_time.txt"
  manifest_file="${run_dir}/manifest.txt"
  batch_size="$(awk -F= '$1 == "batch_size" {print $2; exit}' "${manifest_file}")"
  feature_flush_us="$(awk -F= '$1 == "feature_flush_us" {print $2; exit}' "${manifest_file}")"
  request_timeout_ms="$(awk -F= '$1 == "gpu_timeout_ms" {print $2; exit}' "${manifest_file}")"
  [[ -n "${batch_size}" && -n "${feature_flush_us}" && -n "${request_timeout_ms}" ]] || {
    echo "runtime metadata is incomplete in ${manifest_file}" >&2
    exit 3
  }
  if [[ -z "${runtime_batch_size}" ]]; then
    runtime_batch_size="${batch_size}"
    runtime_feature_flush_us="${feature_flush_us}"
    runtime_request_timeout_ms="${request_timeout_ms}"
  elif [[ "${batch_size}" != "${runtime_batch_size}" \
    || "${feature_flush_us}" != "${runtime_feature_flush_us}" \
    || "${request_timeout_ms}" != "${runtime_request_timeout_ms}" ]]; then
    echo "runtime metadata differs across replay runs" >&2
    exit 3
  fi
  cpu_percent="$(awk -F: '/Percent of CPU/{gsub(/[%[:space:]]/, "", $2); print $2}' "${time_file}")"
  rss_kb="$(awk -F: '/Maximum resident set size/{gsub(/[[:space:]]/, "", $2); print $2}' "${time_file}")"
  if (( cpu_percent > max_cpu_percent )); then
    max_cpu_percent="${cpu_percent}"
  fi
  if (( rss_kb > max_rss_kb )); then
    max_rss_kb="${rss_kb}"
  fi
done

mkdir -p "$(dirname "${output}")"
jq -s \
  --arg generated_at "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --argjson physical_cpu_percent_max "${max_cpu_percent}" \
  --argjson physical_rss_kb_max "${max_rss_kb}" \
  --argjson runtime_batch_size "${runtime_batch_size}" \
  --argjson runtime_feature_flush_us "${runtime_feature_flush_us}" \
  --argjson runtime_request_timeout_ms "${runtime_request_timeout_ms}" \
  '
  def all_true(generator): [generator] | all;
  {
    schema_version: 1,
    generated_at: $generated_at,
    evidence_scope: "physical-host offline full-PCAP replay confirmation",
    candidate_id: "A09",
    runtime: {
      model_n_jobs: 1,
      batch_size: $runtime_batch_size,
      request_timeout_ms: $runtime_request_timeout_ms,
      feature_flush_us: $runtime_feature_flush_us,
      feature_encoding: "raw_v1",
      prediction_encoding: "ordered_v1"
    },
    run_count: length,
    runs: map({
      source,
      elapsed_s,
      packets_received,
      packets_parsed,
      parse_reject_rate,
      capture_drop_rate,
      flows_emitted,
      key_flow_coverage,
      gpu_flows_scored,
      gpu_queue_full,
      gpu_batches_ok,
      gpu_batches_failed,
      fallback_flows,
      budget_overrun_count,
      packet_p99_us: .packet_processing_latency.p99_us,
      packet_p999_us: .packet_processing_latency.p999_us,
      feature_enqueue_p99_us: .flow_materialization_to_feature_enqueue_latency.p99_us,
      feature_enqueue_p999_us: .flow_materialization_to_feature_enqueue_latency.p999_us,
      gpu_batch_p99_us: .gpu_batch_round_trip_latency.p99_us,
      gpu_batch_p999_us: .gpu_batch_round_trip_latency.p999_us
    }),
    observed_worst_case: {
      capture_drop_rate_max: (map(.capture_drop_rate) | max),
      parse_reject_rate_max: (map(.parse_reject_rate) | max),
      key_flow_coverage_min: (map(.key_flow_coverage) | min),
      gpu_queue_full_max: (map(.gpu_queue_full) | max),
      gpu_batches_failed_max: (map(.gpu_batches_failed) | max),
      fallback_flows_max: (map(.fallback_flows) | max),
      budget_overrun_count_max: (map(.budget_overrun_count) | max),
      packet_p99_us_max: (map(.packet_processing_latency.p99_us) | max),
      packet_p999_us_max: (map(.packet_processing_latency.p999_us) | max),
      feature_enqueue_p99_us_max: (map(.flow_materialization_to_feature_enqueue_latency.p99_us) | max),
      feature_enqueue_p999_us_max: (map(.flow_materialization_to_feature_enqueue_latency.p999_us) | max),
      gpu_batch_p99_us_max: (map(.gpu_batch_round_trip_latency.p99_us) | max),
      gpu_batch_p999_us_max: (map(.gpu_batch_round_trip_latency.p999_us) | max),
      physical_cpu_percent_max: $physical_cpu_percent_max,
      physical_rss_kb_max: $physical_rss_kb_max
    },
    gates: {
      min_runs: 3,
      max_capture_drop_rate: 0.0,
      min_key_flow_coverage: 0.99,
      max_gpu_queue_full: 0,
      max_gpu_batches_failed: 0,
      max_fallback_flows: 0,
      max_budget_overrun_count: 0,
      max_gpu_batch_p99_us: 100000,
      max_internal_feature_enqueue_p99_us: 5000
    },
    passed_offline_confirmation: (
      length >= 3
      and all_true(.[].capture_drop_rate == 0)
      and all_true(.[].key_flow_coverage >= 0.99)
      and all_true(.[].gpu_queue_full == 0)
      and all_true(.[].gpu_batches_failed == 0)
      and all_true(.[].fallback_flows == 0)
      and all_true(.[].budget_overrun_count == 0)
      and all_true(.[].gpu_batch_round_trip_latency.p99_us <= 100000)
      and all_true(.[].flow_materialization_to_feature_enqueue_latency.p99_us <= 5000)
    )
  }' "${metrics[@]}" > "${output}"

sha256sum "${output}" > "${output}.sha256"
cat "${output}"
