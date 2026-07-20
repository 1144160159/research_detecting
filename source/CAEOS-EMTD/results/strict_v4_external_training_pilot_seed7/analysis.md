# Strict-v4 external training baseline pilot

Expand to full102: `NONE`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.766127 | 0.800369 | 0.635266 | 0.350782 | 0.637880 | 1.00 |
| cade | 0.656757 | 0.648037 | 0.494933 | 0.659077 | 0.438386 | 2.75 |
| sieve | 0.634810 | 0.656299 | 0.468500 | 0.660250 | 0.486322 | 2.75 |
| closr | 0.616443 | 0.639626 | 0.416773 | 0.606059 | 0.425998 | 3.50 |

## closr expansion gate

- `pilot_runs_complete`: PASS
- `split_and_leakage_integrity`: PASS
- `known_f1_tolerance`: FAIL
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL

## cade expansion gate

- `pilot_runs_complete`: PASS
- `split_and_leakage_integrity`: PASS
- `known_f1_tolerance`: FAIL
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL

## sieve expansion gate

- `pilot_runs_complete`: PASS
- `split_and_leakage_integrity`: PASS
- `known_f1_tolerance`: FAIL
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
