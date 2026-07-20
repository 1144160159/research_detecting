# Strict-v4 OptFS pilot analysis

Expand OptFS to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.783304 | 0.775960 | 0.620716 | 0.453305 | 0.653084 | 1.25 |
| mlp_energy | 0.761651 | 0.764873 | 0.607497 | 0.447847 | 0.635583 | 1.75 |
| optfs_vanilla | 0.761651 | 0.726284 | 0.512275 | 0.499294 | 0.617366 | 3.00 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
