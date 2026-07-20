# Strict-v4 efficiency evidence audit

Direct comparison allowed: `NO`.

| Method | Runs | Train | Wall | Inference | Throughput | GPU memory | Params |
|---|---:|---:|---:|---:|---:|---:|---:|
| caeos_pairwise_core_seed7 | 102/102 | 0/102 | 102/102 | 0/102 | 0/102 | 0/102 | 0/102 |
| opendetect_seed7 | 102/102 | 102/102 | 0/102 | 0/102 | 0/102 | 0/102 | 102/102 |

## Comparison gates

- `run_coverage_complete`: PASS
- `training_time_same_semantics`: FAIL
- `inference_time_complete`: FAIL
- `throughput_complete`: FAIL
- `peak_gpu_memory_complete`: FAIL
- `parameter_count_complete`: FAIL
- `hardware_provenance_complete`: FAIL

## Required follow-up

- run a controlled post-selection efficiency benchmark on identical hardware
- separate training, calibration, and inference wall time
- record warm-up, repetitions, batch size, P50/P95/P99 latency and throughput
- record peak GPU memory and exact hardware/software provenance
