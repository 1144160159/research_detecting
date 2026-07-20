# Strict-v4 fDBD pilot analysis

Expand fDBD to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| mlp_energy | 0.756812 | 0.664793 | 0.476054 | 0.594420 | 0.565793 | 1.25 |
| opendetect | 0.783009 | 0.655398 | 0.480744 | 0.605731 | 0.560082 | 2.25 |
| fdbd | 0.756812 | 0.644517 | 0.445560 | 0.603536 | 0.563653 | 2.50 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
