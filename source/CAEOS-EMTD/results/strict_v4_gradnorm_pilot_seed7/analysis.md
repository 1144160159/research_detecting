# Strict-v4 GradNorm pilot analysis

Expand GradNorm to full 102: `NO`.

| Method | Known F1 | AUROC | AUPR | FPR95 | OSCR | Mean rank |
|---|---:|---:|---:|---:|---:|---:|
| opendetect | 0.783086 | 0.726231 | 0.569072 | 0.496291 | 0.628938 | 1.00 |
| mlp_energy | 0.756934 | 0.684673 | 0.511678 | 0.524982 | 0.613169 | 2.00 |
| gradnorm | 0.756934 | 0.578765 | 0.446665 | 0.673105 | 0.518274 | 3.00 |

## Expansion gate

- `pilot_runs_complete`: PASS
- `split_integrity`: PASS
- `known_f1_nonregression`: PASS
- `top_two_rank`: FAIL
- `metric_breadth`: FAIL
- `overall_gain`: FAIL
- `suite_robustness`: FAIL
