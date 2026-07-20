# Strict-v4 AEGIS training baseline pilot

Expand to full102: `NONE`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| aegis_clean_adapter | 0.768204 | 0.834617 | 0.667903 | 0.346459 | 0.666426 | 1.00 |
| opendetect | 0.766127 | 0.800369 | 0.635266 | 0.350782 | 0.637880 | 2.00 |

## aegis_clean_adapter expansion gate

- `pilot_runs_complete`: PASS
- `split_and_leakage_integrity`: PASS
- `known_f1_tolerance`: PASS
- `top_two_rank`: PASS
- `metric_breadth`: PASS
- `overall_gain`: PASS
- `suite_robustness`: FAIL
