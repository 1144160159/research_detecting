# Strict-v4 complementary training baseline pilot

Expand to full102: `NONE`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.766127 | 0.800369 | 0.635266 | 0.350782 | 0.637880 | 1.00 |
| foss | 0.493533 | 0.735482 | 0.563435 | 0.561551 | 0.387305 | 3.00 |
| palm | 0.747314 | 0.617395 | 0.449965 | 0.596291 | 0.506372 | 3.50 |
| ronetc | 0.691196 | 0.574312 | 0.357768 | 0.511269 | 0.517134 | 3.50 |
| arpl | 0.730848 | 0.577955 | 0.442941 | 0.583859 | 0.496976 | 4.00 |

## arpl expansion gate

- `pilot_runs_complete`: PASS
- `split_and_leakage_integrity`: PASS
- `known_f1_tolerance`: FAIL
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL

## palm expansion gate

- `pilot_runs_complete`: PASS
- `split_and_leakage_integrity`: PASS
- `known_f1_tolerance`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL

## ronetc expansion gate

- `pilot_runs_complete`: PASS
- `split_and_leakage_integrity`: PASS
- `known_f1_tolerance`: FAIL
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL

## foss expansion gate

- `pilot_runs_complete`: PASS
- `split_and_leakage_integrity`: PASS
- `known_f1_tolerance`: FAIL
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
