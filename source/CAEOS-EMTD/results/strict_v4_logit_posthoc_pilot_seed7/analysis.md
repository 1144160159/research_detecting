# Strict-v4 GEN pilot analysis

Expand GEN to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.771531 | 0.730022 | 0.588984 | 0.563472 | 0.598130 | 1.00 |
| gen | 0.744728 | 0.618568 | 0.499841 | 0.619851 | 0.539728 | 2.25 |
| mlp_energy | 0.744728 | 0.621515 | 0.499059 | 0.626161 | 0.532834 | 2.75 |
| shannon_entropy | 0.744728 | 0.584246 | 0.491635 | 0.650981 | 0.520962 | 4.00 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `top_half_rank`: PASS
- `metric_breadth`: PASS
- `overall_gain`: PASS
- `suite_robustness`: FAIL
