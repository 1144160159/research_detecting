# Strict-v4 ODIN pilot analysis

Expand ODIN to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.784389 | 0.716186 | 0.513997 | 0.506786 | 0.591228 | 1.00 |
| mlp_energy | 0.749150 | 0.689551 | 0.482655 | 0.547152 | 0.583909 | 2.50 |
| odin | 0.749150 | 0.686378 | 0.474673 | 0.542374 | 0.585939 | 2.50 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: PASS
- `overall_gain`: FAIL
- `suite_robustness`: PASS
